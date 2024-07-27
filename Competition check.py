import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox

def read_competitors_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Парсинг даних з файлу
    data = []
    i = 0
    while i < len(lines):
        # Збір основної інформації
        main_info = lines[i].strip().split('\t')
        if len(main_info) < 5:
            i += 1  # Перехід до наступного рядка, якщо дані неповні
            continue
        
        rank = int(main_info[0])
        name = main_info[1]
        status = main_info[2].strip()
        priority = main_info[3].strip()
        score = float(main_info[4].strip().split()[0])  # Витягування балу
        
        # Пропуск рядка з "розрахунок"
        i += 2
        
        # Пропуск рядка з деталями предметів
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(''):
            i += 1
        
        # Додати запис до списку даних
        data.append([rank, name, status, priority, score])
        
        # Перехід до наступного абітурієнта
        i += 1  # Переходити до наступного запису після "розрахунок" і деталей

    # Перетворення даних у DataFrame для зручності обробки
    df = pd.DataFrame(data, columns=['Rank', 'Name', 'Status', 'Priority', 'Score'])
    df = df.sort_values(by='Priority')
    return df

def filter_competitors(df, user_score):
    valid_statuses = ['Допущено', 'Заява надійшла з сайту', 'Зареєстровано']
    filtered_df = df[
        (df['Status'].isin(valid_statuses)) &
        (df['Score'] >= user_score) &
        (df['Priority'].apply(lambda x: x.isdigit() and int(x) <= 3))
    ]
    return filtered_df

def count_priorities(df):
    priority_counts = df['Priority'].value_counts()
    count_1 = priority_counts.get('1', 0)
    count_2 = priority_counts.get('2', 0)
    count_3 = priority_counts.get('3', 0)
    return count_1, count_2, count_3

def show_data_in_window(df):
    # Створення вікна
    window = tk.Tk()
    window.title("Перевірка конкуренції")

    # Встановлення розміру вікна на весь екран
    window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))

    # Створення таблиці для відображення даних
    tree = ttk.Treeview(window, columns=list(df.columns), show='headings')
    
    # Налаштування стовпців
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Додавання даних до таблиці
    for index, row in df.iterrows():
        tree.insert('', 'end', values=list(row))

    tree.pack(expand=True, fill='both')

    # Підрахунок кількості пунктів з різними пріоритетами
    count_1, count_2, count_3 = count_priorities(df)

    # Відображення кількості пунктів списку
    count_label = ttk.Label(window, text=f"Кількість пунктів списку з пріоритетом 1: {count_1}, з пріоритетом 2: {count_2}, з пріоритетом 3: {count_3}")
    count_label.pack()

    # Запуск основного циклу Tkinter
    window.mainloop()

def center_window(window, width, height):
    window.geometry(f'{width}x{height}')
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'+{x}+{y}')

def main():
    root = tk.Tk()
    root.withdraw()  # Приховати основне вікно

    # Отримання шляху до поточної папки
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Отримання списку всіх txt файлів у поточній папці
    txt_files = [f for f in os.listdir(current_directory) if f.endswith('.txt')]

    if not txt_files:
        messagebox.showerror("Помилка", "Не знайдено цього файлу в цій діректорії.")
        return

    # Створення вікна для вибору файлу
    file_selection_window = tk.Tk()
    file_selection_window.title("Виберіть файл зі списком абітурієнтів")
    center_window(file_selection_window, 430, 100)

    # Випадаючий список з файлами
    file_var = tk.StringVar(value=txt_files[0])
    file_combobox = ttk.Combobox(file_selection_window, textvariable=file_var, values=txt_files, state='readonly')
    file_combobox.pack(pady=10)

    def on_submit():
        selected_file = file_var.get()
        file_selection_window.destroy()
        # Запит кількості балів у користувача
        user_score = simpledialog.askfloat("Ваші бали", "Введіть ваш конкурсний бал:")

        # Читання даних з файлу
        file_path = os.path.join(current_directory, selected_file)
        competitors_df = read_competitors_from_txt(file_path)

        # Фільтрація конкурентів
        filtered_competitors = filter_competitors(competitors_df, user_score)

        # Показ даних у вікні Tkinter
        show_data_in_window(filtered_competitors)

    submit_button = ttk.Button(file_selection_window, text="Обрати", command=on_submit)
    submit_button.pack(pady=10)

    file_selection_window.mainloop()

if __name__ == "__main__":
    main()

