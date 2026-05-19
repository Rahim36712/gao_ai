param(
    [switch]$RunTests  # Add -RunTests flag to also run agent pipelines
)

$ErrorActionPreference = "Continue"
$Host.UI.RawUI.WindowTitle = "Gaon Guard AI Demo"

Write-Host ""
Write-Host "  +--------------------------------------------------+" -ForegroundColor Cyan
Write-Host "  |        GAON GUARD AI -- DEMO LAUNCHER            |" -ForegroundColor Cyan
Write-Host "  |  3-Engine Agentic Crisis Intelligence System     |" -ForegroundColor Cyan
Write-Host "  +--------------------------------------------------+" -ForegroundColor Cyan
Write-Host ""

# === Step 1: Set API Key =================================
$env:GEMINI_API_KEY = "AIzaSyCm_dCYE6n7K8nvGw4VrMnnASLMHVDGlRM"
Write-Host "  [1/3] API Key loaded" -ForegroundColor Green

# === Step 2: Kill old server if running ==================
try {
    $existing = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    if ($existing) {
        $pids = $existing | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids) {
            if ($p -gt 0) {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                Write-Host "        Killed old server on port 8000 (PID $p)" -ForegroundColor DarkGray
            }
        }
        Start-Sleep -Seconds 2
    }
} catch {}

# === Step 3: Start Backend ===============================
Write-Host "  [2/3] Starting FastAPI backend..." -ForegroundColor Yellow

$backendDir = Join-Path $PSScriptRoot "backend"
Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --port 8000" -WorkingDirectory $backendDir -NoNewWindow
Start-Sleep -Seconds 4

# Health check: wait up to 15 seconds for port 8000 to accept connections
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 8000)
        $tcp.Close()
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($ready) {
    Write-Host "        Backend is live at http://localhost:8000" -ForegroundColor Green
    Write-Host "        Swagger UI: http://localhost:8000/docs" -ForegroundColor DarkGray
} else {
    Write-Host "        [ERROR] Backend failed to start!" -ForegroundColor Red
    Write-Host "        Try manually: cd backend; python -m uvicorn main:app --port 8000" -ForegroundColor Red
    exit 1
}

# === Step 4 (Optional): Run Agent Tests ==================
if ($RunTests) {
    Write-Host ""
    Write-Host "  [TESTS] Running agent pipelines (this uses API quota)..." -ForegroundColor Yellow

    Push-Location (Join-Path $PSScriptRoot "antigravity")

    $scripts = @(
        @{ Name = "A1-A3 Crisis Intelligence"; File = "test_a1_a3.py" },
        @{ Name = "A4-X  Dispatch & Coordinator"; File = "test_a4_x.py" },
        @{ Name = "B1-B3 Missing Person Engine"; File = "test_b1_b3.py" },
        @{ Name = "C1-C3 Aid Accountability"; File = "test_c1_c3.py" }
    )

    foreach ($s in $scripts) {
        Write-Host "        -> $($s.Name)..." -ForegroundColor Gray -NoNewline
        try {
            python $s.File 2>&1 | Out-Null
            Write-Host " Done" -ForegroundColor Green
        } catch {
            Write-Host " Error (non-fatal)" -ForegroundColor Yellow
        }
    }

    Pop-Location
    Write-Host "        Agent tests complete." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  [INFO] Skipping agent tests (saves API quota for live demo)." -ForegroundColor DarkGray
    Write-Host "         To run tests: .\start_demo.ps1 -RunTests" -ForegroundColor DarkGray
}

# === Step 5: Launch Flutter ==============================
Write-Host ""
Write-Host "  [3/3] Launching Flutter app in Chrome..." -ForegroundColor Yellow

$mobileDir = Join-Path $PSScriptRoot "mobile"
Push-Location $mobileDir

try {
    flutter run -d chrome
} catch {
    Write-Host "        [ERROR] Flutter not found in PATH." -ForegroundColor Red
    Write-Host "        Open a terminal where 'flutter' works and run:" -ForegroundColor Red
    Write-Host "          cd mobile; flutter run -d chrome" -ForegroundColor White
}

Pop-Location

Write-Host ""
Write-Host "  +--------------------------------------------------+" -ForegroundColor Cyan
Write-Host "  |           DEMO SESSION ENDED                     |" -ForegroundColor Cyan
Write-Host "  +--------------------------------------------------+" -ForegroundColor Cyan
