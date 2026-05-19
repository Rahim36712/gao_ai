"""
Gaon Guard AI — Robust Gemini API caller with retry and JSON repair.
Shared across all test scripts.
All data is SYNTHETIC DEMO DATA.
"""

import json
import re
import time

from google import genai
from google.genai import types

# Fallback model when primary model hits rate limits
FALLBACK_MODEL = "gemini-2.5-flash"


def _extract_json(raw: str) -> str:
    """
    Extract valid JSON from Gemini's response text.
    Handles: markdown fences, thinking blocks, trailing commas,
    single-line comments, truncated output, and missing outer braces.
    """
    text = raw.strip()

    # 1. Remove markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'```(?:json)?\s*\n?', '', text)
    text = text.strip()

    # 2. Check if the response is bare key:value pairs (missing outer braces)
    #    Pattern: text starts with "some_key": ... (quoted key followed by colon)
    #    This means the model returned JSON content without wrapping { }
    if text and text[0] == '"' and not text.startswith('['):
        # Check if it looks like "key": value (not a standalone string)
        bare_kv = re.match(r'^"[^"]+"\s*:', text)
        if bare_kv:
            text = '{' + text + '}'

    # 3. Find the outermost JSON object or array
    first_brace = text.find('{')
    first_bracket = text.find('[')

    if first_brace == -1 and first_bracket == -1:
        # Last resort: wrap in braces
        text = '{' + text + '}'
        first_brace = 0

    if first_brace == -1:
        start = first_bracket
    elif first_bracket == -1:
        start = first_brace
    else:
        start = min(first_brace, first_bracket)

    # Find the matching closing bracket from the end
    if text[start] == '{':
        end = text.rfind('}')
    else:
        end = text.rfind(']')

    if end == -1 or end <= start:
        text = text[start:]
    else:
        text = text[start:end + 1]

    # 4. Remove single-line comments (// ...) that break JSON
    text = re.sub(r'//[^\n]*', '', text)

    # 5. Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # 6. Fix truncated JSON (unbalanced brackets)
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')

    if open_braces > 0 or open_brackets > 0:
        # Close any unterminated string
        if text.count('"') % 2 != 0:
            text += '"'
        # Remove trailing partial values (incomplete numbers, dangling colons, commas)
        text = re.sub(r',\s*"[^"]*"\s*:\s*[^,}\]]*$', '', text)  # trailing "key": partial_val
        text = text.rstrip().rstrip(',').rstrip(':')
        # Recount after cleanup
        open_brackets = text.count('[') - text.count(']')
        open_braces = text.count('{') - text.count('}')
        # Close remaining brackets
        for _ in range(max(0, open_brackets)):
            text += ']'
        for _ in range(max(0, open_braces)):
            text += '}'

    # 7. Final fallback: if JSON still invalid, progressively strip trailing chars
    try:
        json.loads(text)
    except (json.JSONDecodeError, ValueError):
        # Try stripping from the last complete key-value pair
        for trim in range(1, min(len(text), 100)):
            candidate = text[:len(text) - trim].rstrip().rstrip(',')
            # Rebalance brackets
            ob = candidate.count('{') - candidate.count('}')
            ol = candidate.count('[') - candidate.count(']')
            if candidate.count('"') % 2 != 0:
                candidate += '"'
                candidate = candidate.rstrip().rstrip(',')
            for _ in range(max(0, ol)):
                candidate += ']'
            for _ in range(max(0, ob)):
                candidate += '}'
            try:
                json.loads(candidate)
                text = candidate
                break
            except (json.JSONDecodeError, ValueError):
                continue

    return text


def call_gemini(client, system_prompt, user_prompt, config):
    """
    Call Gemini API and return parsed JSON response.
    - Retries up to 5 times on 429/503 errors with smart backoff
    - Automatically falls back to gemini-2.0-flash on quota exhaustion
    - Retries up to 3 times on JSON parse errors (re-calls the model)
    - Robust JSON extraction handles markdown, comments, trailing commas, truncation
    """
    max_retries = 5
    current_model = config["model"]["model_name"]
    used_fallback = False

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=current_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=config["model"]["temperature"],
                    max_output_tokens=config["model"]["max_output_tokens"],
                    response_mime_type=config["model"]["response_mime_type"],
                ),
            )
            raw_text = response.text
            text = _extract_json(raw_text)
            try:
                return json.loads(text)
            except json.JSONDecodeError as je:
                if attempt < max_retries - 1:
                    print(f"    [RETRY] JSON parse error: {je.msg} at pos {je.pos}. Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(1)
                    continue
                else:
                    print(f"    [ERROR] Raw Gemini response (first 500 chars):")
                    print(f"    {raw_text[:500]}")
                    raise

        except json.JSONDecodeError:
            raise
        except Exception as e:
            err_str = str(e).lower()

            # Check if it's a rate limit / quota error
            is_quota = "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str
            is_server = "503" in err_str or "unavailable" in err_str or "overloaded" in err_str or "500" in err_str

            if is_quota and not used_fallback:
                # Switch to fallback model immediately
                used_fallback = True
                current_model = FALLBACK_MODEL
                # Parse retry delay from error if available
                delay_match = re.search(r'retry in (\d+(?:\.\d+)?)s', err_str)
                wait = max(int(float(delay_match.group(1))) + 1, 3) if delay_match else 5
                print(f"    [FALLBACK] Quota hit on {config['model']['model_name']}. Switching to {FALLBACK_MODEL}, waiting {wait}s...")
                time.sleep(wait)
                continue
            elif (is_quota or is_server) and attempt < max_retries - 1:
                # Parse retry delay from error if available
                delay_match = re.search(r'retry in (\d+(?:\.\d+)?)s', err_str)
                if delay_match:
                    wait = int(float(delay_match.group(1))) + 2
                else:
                    wait = min(2 ** (attempt + 1), 30)  # 2, 4, 8, 16, 30
                print(f"    [RETRY] API error. Waiting {wait}s... (attempt {attempt + 1}/{max_retries}, model: {current_model})")
                time.sleep(wait)
                continue
            raise
