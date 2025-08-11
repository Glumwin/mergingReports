@echo off
echo === Быстрая сборка с оптимизацией ===

echo Компилируем с оптимизацией...
pyinstaller --clean cluster_organizer.spec

if %errorlevel% equ 0 (
    echo === Готово! ===
    echo Файл: dist/cluster_organizer.exe
) else (
    echo === Ошибка! ===
)

pause
