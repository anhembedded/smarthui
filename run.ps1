# Script chạy ứng dụng SmartHui tự động
Write-Host "Đang khởi động SmartHui..." -ForegroundColor Green

# Kiểm tra thư mục hiện tại
$CurrentDir = Get-Location
Write-Host "Thư mục làm việc: $CurrentDir"

# Kiểm tra nếu có môi trường ảo (.venv)
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "Phát hiện môi trường ảo, đang khởi chạy..." -ForegroundColor Cyan
    & ".\.venv\Scripts\python.exe" "main.py"
}
else {
    Write-Host "Chạy bằng Python hệ thống..." -ForegroundColor Yellow
    python main.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Có lỗi xảy ra khi chạy ứng dụng. Vui lòng kiểm tra lại!" -ForegroundColor Red
    pause
}
