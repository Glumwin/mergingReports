@echo off
echo === Сверхбыстрая сборка ===

echo Компилируем...
pyinstaller --onefile --windowed --clean cluster_organizer.py

if %errorlevel% equ 0 (
    echo === Готово! ===
    echo Файл: dist/cluster_organizer.exe
) else (
    echo === Ошибка! ===
)

pause
