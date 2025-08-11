# Скрипт для автоматической компиляции Cluster Organizer
# Требует установленный PyInstaller: pip install pyinstaller

Write-Host "=== Cluster Organizer Build Script ===" -ForegroundColor Green
Write-Host "Начинаем сборку приложения..." -ForegroundColor Yellow

# Проверяем наличие PyInstaller
try {
    $pyinstallerVersion = pyinstaller --version
    Write-Host "PyInstaller найден: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "PyInstaller не найден. Устанавливаем..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ошибка установки PyInstaller!" -ForegroundColor Red
        exit 1
    }
}

# Создаем папку dist если её нет
if (!(Test-Path "dist")) {
    New-Item -ItemType Directory -Path "dist" | Out-Null
    Write-Host "Создана папка dist" -ForegroundColor Green
}

# Очищаем папку dist
Write-Host "Очищаем папку dist..." -ForegroundColor Yellow
Get-ChildItem -Path "dist" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

# Удаляем старые файлы сборки
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Удалена папка build" -ForegroundColor Yellow
}

if (Test-Path "cluster_organizer.spec") {
    Remove-Item -Path "cluster_organizer.spec" -Force -ErrorAction SilentlyContinue
    Write-Host "Удален файл .spec" -ForegroundColor Yellow
}

# Компилируем приложение
Write-Host "Компилируем приложение..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --name "Cluster Organizer" cluster_organizer.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "=== Сборка завершена успешно! ===" -ForegroundColor Green
    Write-Host "Исполняемый файл находится в: dist/Cluster Organizer.exe" -ForegroundColor Cyan
    
    # Проверяем размер файла
    $exePath = "dist/Cluster Organizer.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Host "Размер файла: $fileSizeMB MB" -ForegroundColor Cyan
    }
    
    # Копируем примеры файлов в dist
    Write-Host "Копируем примеры файлов..." -ForegroundColor Yellow
    Copy-Item "*.csv" -Destination "dist/" -ErrorAction SilentlyContinue
    Copy-Item "README.md" -Destination "dist/" -ErrorAction SilentlyContinue
    Copy-Item "requirements.txt" -Destination "dist/" -ErrorAction SilentlyContinue
    
    Write-Host "Все файлы скопированы в папку dist" -ForegroundColor Green
    Write-Host "Можно запустить: dist/Cluster Organizer.exe" -ForegroundColor Cyan
    
} else {
    Write-Host "=== Ошибка сборки! ===" -ForegroundColor Red
    Write-Host "Проверьте логи выше для деталей" -ForegroundColor Red
    exit 1
}

Write-Host "`nНажмите любую клавишу для выхода..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
