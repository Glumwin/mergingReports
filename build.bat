@echo off
chcp 65001 >nul
echo === Cluster Organizer Build Script ===
echo Начинаем сборку приложения...

REM Проверяем наличие PyInstaller
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller не найден. Устанавливаем...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Ошибка установки PyInstaller!
        pause
        exit /b 1
    )
)

REM Создаем папку dist если её нет
if not exist "dist" (
    mkdir dist
    echo Создана папка dist
)

REM Очищаем папку dist
echo Очищаем папку dist...
if exist "dist" (
    rmdir /s /q dist 2>nul
    mkdir dist
)

REM Удаляем старые файлы сборки
if exist "build" (
    rmdir /s /q build
    echo Удалена папка build
)

if exist "cluster_organizer.spec" (
    del cluster_organizer.spec
    echo Удален файл .spec
)

REM Компилируем приложение
echo Компилируем приложение...
pyinstaller --onefile --windowed --name "Cluster Organizer" cluster_organizer.py

if %errorlevel% equ 0 (
    echo === Сборка завершена успешно! ===
    echo Исполняемый файл находится в: dist/Cluster Organizer.exe
    
    REM Проверяем размер файла
    if exist "dist/Cluster Organizer.exe" (
        for %%A in ("dist/Cluster Organizer.exe") do (
            set /a size=%%~zA/1024/1024
            echo Размер файла: !size! MB
        )
    )
    
    REM Копируем примеры файлов в dist
    echo Копируем примеры файлов...
    copy "*.csv" "dist\" >nul 2>&1
    copy "README.md" "dist\" >nul 2>&1
    copy "requirements.txt" "dist\" >nul 2>&1
    
    echo Все файлы скопированы в папку dist
    echo Можно запустить: dist/Cluster Organizer.exe
    
) else (
    echo === Ошибка сборки! ===
    echo Проверьте логи выше для деталей
    pause
    exit /b 1
)

echo.
pause
