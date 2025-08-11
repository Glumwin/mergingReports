# Инструкции по сборке Cluster Organizer

## Автоматическая сборка

### Быстрая сборка
```cmd
build.bat
```

## Ручная сборка

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Компиляция с PyInstaller
```bash
pyinstaller --onefile --windowed --clean cluster_organizer.py
```

### 3. Результат
Исполняемый файл будет создан в папке `dist/cluster_organizer.exe`

## Параметры сборки

- `--onefile` - создает один исполняемый файл
- `--windowed` - запускает приложение без консольного окна
- `--clean` - очищает кэш для ускорения сборки

## Требования

- Python 3.7+
- PyInstaller 5.0+
- pandas 1.3+

## Устранение проблем

### Ошибка "PyInstaller не найден"
```bash
pip install pyinstaller
```

### Ошибка кодировки
Убедитесь, что в системе установлена поддержка UTF-8

### Большой размер файла
Это нормально для PyInstaller - он включает все зависимости Python
