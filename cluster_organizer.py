# -*- coding: utf-8 -*-
import sys
import os

# Настройка кодировки для Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Безопасная настройка stdout/stderr для скомпилированного приложения
    if sys.stdout is not None:
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass
    if sys.stderr is not None:
        try:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except:
            pass

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import json
from pathlib import Path
import traceback

class ClusterOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Cluster Organizer")
        self.root.geometry("900x750")
        
        # Переменные для хранения путей к файлам
        self.file_1000_path = tk.StringVar()
        self.file_200_path = tk.StringVar()
        
        # Список для хранения виджетов настроек кластеров
        self.cluster_entries = []
        
        # Дефолтные настройки кластеров
        self.default_clusters = [
            ("8,0,5", "TOPs"),
            ("3,4,10,7", "MIDLs"),
            ("16,1,18", "WEAKs"),
            ("19,14,11,17,6,13,15,9,2,12", "FISHs")
        ]
        
        # Путь к файлу конфигурации
        self.config_file = Path("cluster_config.json")
        
        # Переменные для выбора столбцов
        self.column_vars = {}
        self.columns_frame = None
        self.columns_dropdown_visible = False
        self.columns_button = None
        self.all_columns_var = tk.BooleanVar(value=True)
        self.available_columns = []  # Список всех доступных столбцов из файлов
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для адаптивного размера
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === Секция выбора файлов ===
        files_frame = ttk.LabelFrame(main_frame, text="Выбор файлов", padding="10")
        files_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        files_frame.columnconfigure(1, weight=1)
        
        # Файл 1000+
        ttk.Label(files_frame, text="Файл 1000+:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Entry(files_frame, textvariable=self.file_1000_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(files_frame, text="Обзор", command=lambda: self.select_file("1000")).grid(row=0, column=2, padx=5)
        
        # Файл 200+
        ttk.Label(files_frame, text="Файл 200+:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(files_frame, textvariable=self.file_200_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(files_frame, text="Обзор", command=lambda: self.select_file("200")).grid(row=1, column=2, padx=5, pady=5)
        
        # === Секция настроек кластеров ===
        clusters_label_frame = ttk.LabelFrame(main_frame, text="Настройки кластеров", padding="10")
        clusters_label_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        clusters_label_frame.columnconfigure(0, weight=1)
        clusters_label_frame.rowconfigure(0, weight=1)
        
        # Создаем Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(clusters_label_frame, height=200)
        scrollbar = ttk.Scrollbar(clusters_label_frame, orient="vertical", command=canvas.yview)
        self.clusters_frame = ttk.Frame(canvas)
        
        self.clusters_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.clusters_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Заголовки
        ttk.Label(self.clusters_frame, text="Номера кластеров", font=("", 9, "bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.clusters_frame, text="Имя файла", font=("", 9, "bold")).grid(row=0, column=1, padx=5, pady=2)
        
        # Добавляем дефолтные строки
        for i, (clusters, name) in enumerate(self.default_clusters, start=1):
            self.add_cluster_row(clusters, name)
        
        # Кнопка добавления строки
        ttk.Button(clusters_label_frame, text="+ Добавить строку", command=self.add_cluster_row).grid(row=1, column=0, pady=5)
        
        # === Секция выбора столбцов ===
        columns_label_frame = ttk.LabelFrame(main_frame, text="Выбор столбцов для сохранения", padding="10")
        columns_label_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Кнопка для открытия выпадающего списка
        self.columns_button = ttk.Button(columns_label_frame, text="▼ Выбрать столбцы для сохранения", 
                                         command=self.toggle_columns_dropdown)
        self.columns_button.grid(row=0, column=0, sticky=tk.W)
        
        # Фрейм для чекбоксов (изначально скрыт)
        self.columns_container = ttk.Frame(columns_label_frame)
        self.columns_container.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.columns_container.grid_remove()  # Скрываем изначально
        
        # Создаем скроллируемый фрейм для чекбоксов
        canvas = tk.Canvas(self.columns_container, height=200)
        scrollbar = ttk.Scrollbar(self.columns_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Чекбокс "Все"
        self.all_check = ttk.Checkbutton(self.scrollable_frame, text="Все столбцы", 
                                    variable=self.all_columns_var, 
                                    command=self.toggle_all_columns)
        self.all_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Информационная метка
        self.columns_info_label = ttk.Label(self.scrollable_frame, 
                                           text="Выберите файлы для загрузки списка столбцов",
                                           foreground="gray")
        self.columns_info_label.grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)
        
        # === Секция управления ===
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(control_frame, text="Обработать", command=self.process_files, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Сохранить настройки", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Загрузить настройки", command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        # === Лог/статус ===
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def add_cluster_row(self, clusters="", name=""):
        row = len(self.cluster_entries) + 1
        
        clusters_var = tk.StringVar(value=clusters)
        name_var = tk.StringVar(value=name)
        
        clusters_entry = ttk.Entry(self.clusters_frame, textvariable=clusters_var, width=40)
        clusters_entry.grid(row=row, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        name_entry = ttk.Entry(self.clusters_frame, textvariable=name_var, width=20)
        name_entry.grid(row=row, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        remove_btn = ttk.Button(self.clusters_frame, text="X", width=3, 
                                command=lambda r=row-1: self.remove_cluster_row(r))
        remove_btn.grid(row=row, column=2, padx=2, pady=2)
        
        self.cluster_entries.append((clusters_var, name_var, clusters_entry, name_entry, remove_btn))
        
        # Настройка весов для адаптивного размера
        self.clusters_frame.columnconfigure(0, weight=2)
        self.clusters_frame.columnconfigure(1, weight=1)
        
    def remove_cluster_row(self, index):
        if index < len(self.cluster_entries):
            # Удаляем виджеты
            clusters_var, name_var, clusters_entry, name_entry, remove_btn = self.cluster_entries[index]
            clusters_entry.destroy()
            name_entry.destroy()
            remove_btn.destroy()
            
            # Удаляем из списка
            del self.cluster_entries[index]
            
            # Перерисовываем оставшиеся строки
            self.redraw_cluster_rows()
    
    def redraw_cluster_rows(self):
        for i, (clusters_var, name_var, clusters_entry, name_entry, remove_btn) in enumerate(self.cluster_entries):
            row = i + 1
            clusters_entry.grid(row=row, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
            name_entry.grid(row=row, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
            remove_btn.grid(row=row, column=2, padx=2, pady=2)
            # Обновляем команду кнопки удаления
            remove_btn.configure(command=lambda r=i: self.remove_cluster_row(r))
    
    def toggle_columns_dropdown(self):
        """Переключает видимость выпадающего списка столбцов"""
        if self.columns_dropdown_visible:
            self.columns_container.grid_remove()
            self.columns_button.configure(text="▼ Выбрать столбцы для сохранения")
        else:
            self.columns_container.grid()
            self.columns_button.configure(text="▲ Скрыть выбор столбцов")
        self.columns_dropdown_visible = not self.columns_dropdown_visible
    
    def toggle_all_columns(self):
        """Переключает все чекбоксы столбцов"""
        state = self.all_columns_var.get()
        for var in self.column_vars.values():
            var.set(state)
    
    def on_column_change(self):
        """Обработчик изменения состояния чекбокса столбца"""
        # Если хотя бы один столбец не выбран, снимаем галочку с "Все"
        all_checked = all(var.get() for var in self.column_vars.values())
        if not all_checked:
            self.all_columns_var.set(False)
        # Если все столбцы выбраны, ставим галочку на "Все"
        elif all_checked and len(self.column_vars) > 0:
            self.all_columns_var.set(True)
    
    def update_columns_list(self):
        """Обновляет список столбцов на основе выбранных файлов"""
        if not self.file_1000_path.get() and not self.file_200_path.get():
            return
        
        try:
            columns_set = set()
            
            # Читаем столбцы из файла 1000+
            if self.file_1000_path.get() and Path(self.file_1000_path.get()).exists():
                df = pd.read_csv(self.file_1000_path.get(), nrows=1, encoding='utf-8')
                columns_set.update(df.columns.tolist())
            
            # Читаем столбцы из файла 200+
            if self.file_200_path.get() and Path(self.file_200_path.get()).exists():
                df = pd.read_csv(self.file_200_path.get(), nrows=1, encoding='utf-8')
                columns_set.update(df.columns.tolist())
            
            if columns_set:
                self.available_columns = sorted(list(columns_set))
                self.recreate_column_checkboxes()
                self.log(f"Загружено {len(self.available_columns)} столбцов из файлов")
        except Exception as e:
            self.log(f"Ошибка при чтении столбцов: {str(e)}")
    
    def recreate_column_checkboxes(self):
        """Пересоздает чекбоксы для всех доступных столбцов"""
        # Сохраняем текущие выбранные столбцы
        previously_selected = {col: var.get() for col, var in self.column_vars.items()}
        
        # Удаляем старые чекбоксы (кроме "Все столбцы")
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.all_check and not isinstance(widget, ttk.Label):
                widget.destroy()
        
        # Очищаем словарь переменных
        self.column_vars.clear()
        
        # Удаляем информационную метку если она есть
        if hasattr(self, 'columns_info_label'):
            self.columns_info_label.destroy()
        
        # Создаем новые чекбоксы для всех столбцов
        for i, col in enumerate(self.available_columns, start=1):
            var = tk.BooleanVar(value=previously_selected.get(col, False))
            self.column_vars[col] = var
            check = ttk.Checkbutton(self.scrollable_frame, text=col, variable=var,
                                   command=self.on_column_change)
            check.grid(row=i, column=0, sticky=tk.W, padx=20, pady=1)
        
        # Обновляем состояние чекбокса "Все"
        self.on_column_change()
    
    def get_selected_columns(self):
        """Возвращает список выбранных столбцов"""
        if self.all_columns_var.get():
            return None  # None означает сохранить все столбцы
        else:
            selected = [col for col, var in self.column_vars.items() if var.get()]
            return selected if selected else None
    
    def select_file(self, file_type):
        filename = filedialog.askopenfilename(
            title=f"Выберите файл {file_type}+",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        if filename:
            if file_type == "1000":
                self.file_1000_path.set(filename)
            else:
                self.file_200_path.set(filename)
            self.log(f"Выбран файл {file_type}+: {filename}")
            
            # Обновляем список столбцов при выборе файла
            self.update_columns_list()
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def save_config(self):
        config = {
            "clusters": [],
            "selected_columns": self.get_selected_columns(),
            "all_columns": self.all_columns_var.get()
        }
        
        for clusters_var, name_var, _, _, _ in self.cluster_entries:
            clusters = clusters_var.get().strip()
            name = name_var.get().strip()
            if clusters and name:
                config["clusters"].append({
                    "clusters": clusters,
                    "name": name
                })
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.log("Настройки успешно сохранены")
            messagebox.showinfo("Успех", "Настройки сохранены")
        except Exception as e:
            self.log(f"Ошибка при сохранении настроек: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
    
    def load_config(self):
        if not self.config_file.exists():
            self.log("Файл конфигурации не найден, используются настройки по умолчанию")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Очищаем текущие строки
            for _, _, clusters_entry, name_entry, remove_btn in self.cluster_entries:
                clusters_entry.destroy()
                name_entry.destroy()
                remove_btn.destroy()
            self.cluster_entries.clear()
            
            # Загружаем сохраненные строки
            for cluster_config in config.get("clusters", []):
                self.add_cluster_row(cluster_config["clusters"], cluster_config["name"])
            
            # Загружаем настройки столбцов
            if "all_columns" in config:
                self.all_columns_var.set(config["all_columns"])
            
            if "selected_columns" in config and config["selected_columns"]:
                # Сохраняем настройки для применения после загрузки файлов
                self.saved_column_selection = config["selected_columns"]
            else:
                self.saved_column_selection = None
            
            self.log("Настройки успешно загружены")
            
            # Обновляем список столбцов если файлы уже выбраны
            if self.file_1000_path.get() or self.file_200_path.get():
                self.update_columns_list()
                
                # Применяем сохраненные настройки столбцов
                if hasattr(self, 'saved_column_selection') and self.saved_column_selection:
                    for col, var in self.column_vars.items():
                        var.set(col in self.saved_column_selection)
        except Exception as e:
            self.log(f"Ошибка при загрузке настроек: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {str(e)}")
    
    def process_files(self):
        # Очищаем лог
        self.log_text.delete(1.0, tk.END)
        
        # Проверяем выбранные файлы
        if not self.file_1000_path.get() or not self.file_200_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите оба файла (1000+ и 200+)")
            return
        
        try:
            self.log("Начинаем обработку файлов...")
            
            # Читаем CSV файлы
            self.log("Читаем файл 1000+...")
            df_1000 = pd.read_csv(self.file_1000_path.get(), encoding='utf-8')
            self.log(f"Прочитано {len(df_1000)} строк из файла 1000+")
            
            self.log("Читаем файл 200+...")
            df_200 = pd.read_csv(self.file_200_path.get(), encoding='utf-8')
            self.log(f"Прочитано {len(df_200)} строк из файла 200+")
            
            # Проверяем наличие колонки Cluster
            if 'Cluster' not in df_1000.columns:
                raise ValueError("В файле 1000+ отсутствует колонка 'Cluster'")
            if 'Cluster' not in df_200.columns:
                raise ValueError("В файле 200+ отсутствует колонка 'Cluster'")
            
            # Обновляем список столбцов после загрузки файлов
            self.update_columns_list()
            
            # Определяем директорию для сохранения (где находится файл 1000+)
            output_dir = Path(self.file_1000_path.get()).parent
            self.log(f"Результаты будут сохранены в: {output_dir}")
            
            # Кластеры, которые всегда берутся из файла 200+
            clusters_from_200 = set([19, 14, 11, 17, 6, 13, 15, 9, 2, 12])
            
            # Обрабатываем каждую группу кластеров
            for clusters_var, name_var, _, _, _ in self.cluster_entries:
                clusters_str = clusters_var.get().strip()
                name = name_var.get().strip()
                
                if not clusters_str or not name:
                    continue
                
                self.log(f"\nОбработка группы '{name}': {clusters_str}")
                
                # Парсим номера кластеров
                try:
                    cluster_numbers = [int(c.strip()) for c in clusters_str.split(',')]
                except ValueError:
                    self.log(f"Ошибка: неверный формат кластеров для группы '{name}'")
                    continue
                
                # Собираем данные из соответствующих файлов
                result_df = pd.DataFrame()
                
                for cluster_num in cluster_numbers:
                    if cluster_num in clusters_from_200:
                        # Берем из файла 200+
                        cluster_data = df_200[df_200['Cluster'] == cluster_num]
                        self.log(f"  Кластер {cluster_num}: {len(cluster_data)} строк из файла 200+")
                    else:
                        # Берем из файла 1000+
                        cluster_data = df_1000[df_1000['Cluster'] == cluster_num]
                        self.log(f"  Кластер {cluster_num}: {len(cluster_data)} строк из файла 1000+")
                    
                    result_df = pd.concat([result_df, cluster_data], ignore_index=True)
                
                # Фильтруем столбцы если нужно
                selected_columns = self.get_selected_columns()
                if selected_columns is not None and len(selected_columns) > 0:
                    # Проверяем какие из выбранных столбцов существуют в датафрейме
                    existing_columns = [col for col in selected_columns if col in result_df.columns]
                    if existing_columns:
                        result_df = result_df[existing_columns]
                        self.log(f"  Сохраняем только столбцы: {', '.join(existing_columns)}")
                    else:
                        self.log(f"  Предупреждение: выбранные столбцы не найдены в данных")
                
                # Сохраняем результат
                output_file = output_dir / f"{name}.csv"
                result_df.to_csv(output_file, index=False, encoding='utf-8')
                self.log(f"Сохранено {len(result_df)} строк в файл: {output_file}")
            
            self.log("\n=== Обработка завершена успешно! ===")
            messagebox.showinfo("Успех", "Файлы успешно обработаны и сохранены!")
            
        except Exception as e:
            error_msg = f"Ошибка при обработке файлов:\n{str(e)}\n\n{traceback.format_exc()}"
            self.log(error_msg)
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ClusterOrganizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()