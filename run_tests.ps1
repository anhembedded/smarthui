param(
    [string]$path
)

# 1. Activate virtual environment if it exists
if (Test-Path -Path ".venv") {
    Write-Host "Activating virtual environment..."
    . .venv/Scripts/Activate.ps1
}

# 2. Install dependencies if not already installed
Write-Host "Checking and installing dependencies from requirements.txt..."
pip install -r requirements.txt | Out-Null

# 3. Determine the test path
$testPath = "tests" # Default path
if (-not [string]::IsNullOrEmpty($path)) {
    if (Test-Path -Path $path) {
        $testPath = $path
        Write-Host "Running tests for specific path: $testPath" -ForegroundColor Green
    }
    else {
        Write-Host "Error: The specified path '$path' does not exist." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Running all tests..." -ForegroundColor Green
}

# 4. Execute pytest
# Using python -m pytest adds the current directory to sys.path
python -m pytest -v $testPath

# 5. Check the exit code of the last command
if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
}
else {
    Write-Host "Some tests failed. Exit code: $LASTEXITCODE" -ForegroundColor Red
}

# 6. Deactivate virtual environment if it was activated
if (Test-Path -Path ".venv") {
    deactivate
}
