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
MAX_RETRIES = 2
MAX_WAIT_SECONDS = 5


class GeminiCallError(RuntimeError):
    """Clean Gemini failure surfaced to tests without a large traceback chain."""


def _clean_error(message: str) -> GeminiCallError:
    return GeminiCallError(message)


def _sleep_capped(seconds: float) -> None:
    time.sleep(min(max(seconds, 0), MAX_WAIT_SECONDS))


def _strip_fences(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"^\s*```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _candidate_json_strings(text: str):
    decoder = json.JSONDecoder()
    stripped = _strip_fences(text)

    if stripped:
        yield stripped

    # Decode any complete object or array embedded in explanatory text.
    for match in re.finditer(r"[\{\[]", stripped):
        candidate = stripped[match.start():]
        try:
            _, end = decoder.raw_decode(candidate)
            yield candidate[:end]
        except json.JSONDecodeError:
            continue

    # Last-resort repair candidates for common model formatting mistakes.
    repaired = re.sub(r"//[^\n]*", "", stripped)
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    if repaired and repaired[0] == '"' and re.match(r'^"[^"]+"\s*:', repaired):
        repaired = "{" + repaired + "}"
    if repaired:
        yield repaired


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


def parse_gemini_json(raw: str):
    """Parse JSON from Gemini text, accepting fenced or embedded JSON."""
    if not raw:
        raise json.JSONDecodeError("empty Gemini response", "", 0)

    last_error = None
    for candidate in _candidate_json_strings(raw):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    extracted = _extract_json(raw)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError as exc:
        last_error = exc

    raise last_error or json.JSONDecodeError("no valid JSON found", raw, 0)


def call_gemini(client, system_prompt, user_prompt, config):
    """
    Call Gemini API and return parsed JSON response.
    - Retries up to 2 times on transient API/JSON errors
    - Caps every wait to 5 seconds
    - Automatically falls back to gemini-2.5-flash on quota exhaustion
    - Robust JSON extraction handles markdown, comments, trailing commas, truncation
    - Returns {"fallback_required": true, "error": "..."} on JSON parse failure
    - Raises GeminiCallError with a short message on API failure
    """
    max_retries = MAX_RETRIES
    current_model = config["model"]["model_name"]
    used_fallback = False
    last_error = None

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
            raw_text = getattr(response, "text", "") or ""
            try:
                return parse_gemini_json(raw_text)
            except json.JSONDecodeError as je:
                last_error = je
                if attempt < max_retries - 1:
                    print(f"    [RETRY] Gemini returned malformed JSON: {je.msg}. Retrying... (attempt {attempt + 1}/{max_retries})")
                    _sleep_capped(1)
                    continue
                return {
                    "fallback_required": True,
                    "error": f"Gemini returned malformed JSON after {max_retries} attempts: {je.msg}",
                }

        except json.JSONDecodeError:
            return {
                "fallback_required": True,
                "error": "Gemini returned malformed JSON.",
            }
        except GeminiCallError:
            raise
        except Exception as e:
            last_error = e
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
                wait = min(max(int(float(delay_match.group(1))) + 1, 3), MAX_WAIT_SECONDS) if delay_match else MAX_WAIT_SECONDS
                print(f"    [FALLBACK] Quota hit on {config['model']['model_name']}. Switching to {FALLBACK_MODEL}, waiting {wait}s...")
                _sleep_capped(wait)
                continue
            elif (is_quota or is_server) and attempt < max_retries - 1:
                # Parse retry delay from error if available
                delay_match = re.search(r'retry in (\d+(?:\.\d+)?)s', err_str)
                if delay_match:
                    wait = int(float(delay_match.group(1))) + 2
                else:
                    wait = 2 ** (attempt + 1)
                wait = min(wait, MAX_WAIT_SECONDS)
                print(f"    [RETRY] API error. Waiting {wait}s... (attempt {attempt + 1}/{max_retries}, model: {current_model})")
                _sleep_capped(wait)
                continue
            raise _clean_error(f"Gemini call failed: {str(e)[:220]}") from None

    detail = str(last_error)[:220] if last_error else "unknown error"
    raise _clean_error(f"Gemini call failed after {max_retries} attempts: {detail}") from None
