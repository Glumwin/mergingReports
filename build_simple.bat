@echo off
echo === Быстрая сборка Cluster Organizer ===

REM Удаляем старые файлы
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del *.spec

REM Компилируем
echo Компилируем...
pyinstaller --onefile --windowed cluster_organizer.py

if %errorlevel% equ 0 (
    echo === Готово! ===
    echo Файл: dist/cluster_organizer.exe
) else (
    echo === Ошибка! ===
)

pause
