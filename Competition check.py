import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox, filedialog

def read_competitors_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    data = []
    i = 0
    while i < len(lines):
        main_info = lines[i].strip().split('\t')
        if len(main_info) < 5:
            i += 1  # Пропустити рядок, якщо він не містить достатньо даних
            continue
        
        rank = int(main_info[0])
        name = main_info[1]
        status = main_info[2].strip()
        priority = main_info[3].strip()
        
        score_str = main_info[4].strip().split()[0]
        try:
            score = float(score_str)  # Витягування балу
        except ValueError:
            score = None  # Або можна використати інше значення за замовчуванням, наприклад 0.0
        
        # Пропуск рядка з "розрахунок" та інших деталей
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
            i += 1
        
        data.append([rank, name, status, priority, score])
        
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

def show_data_in_window(df, original_file_name):
    # Створення вікна
    window = tk.Tk()
    window.title("Перевірка конкуренції")

    # Встановлення розміру вікна на весь екран
    window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))

    # Додавання фрейму для таблиці та повзунка
    frame = ttk.Frame(window)
    frame.pack(expand=True, fill='both')

    # Додавання стовпця для власної нумерації
    df.insert(0, 'No.', range(1, len(df) + 1))

    # Створення таблиці для відображення даних
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
    
    # Налаштування стовпців
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Додавання даних до таблиці
    for index, row in df.iterrows():
        tree.insert('', 'end', values=list(row))

    # Додавання вертикального повзунка для прокрутки таблиці
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # Підрахунок кількості пунктів з різними пріоритетами
    count_1, count_2, count_3 = count_priorities(df)

    # Відображення кількості пунктів списку
    count_label = ttk.Label(window, text=f"Кількість пунктів списку з пріоритетом 1: {count_1}, з пріоритетом 2: {count_2}, з пріоритетом 3: {count_3}, загалом конкурентів {len(df)}")
    count_label.pack()

    # Додавання кнопки для збереження відфільтрованих даних
    def save_filtered_data():
        filtered_file_name = f"{os.path.splitext(original_file_name)[0]}_filtered.txt"
        df.to_csv(filtered_file_name, sep='\t', index=False, encoding='utf-8')
        messagebox.showinfo("Збереження", f"Відфільтрований список збережено у файл {filtered_file_name}")

    save_button = ttk.Button(window, text="Зберегти відфільтрований список", command=save_filtered_data)
    save_button.pack()

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

    # Відкрити файловий менеджер для вибору файлу
    selected_file = filedialog.askopenfilename(
        title="Виберіть файл зі списком абітурієнтів",
        filetypes=[("Text files", "*.txt")],
        initialdir=os.path.dirname(os.path.abspath(__file__))
    )

    if not selected_file:
        messagebox.showerror("Помилка", "Файл не було обрано.")
        return

    # Запит кількості балів у користувача
    user_score = simpledialog.askfloat("Ваші бали", "Введіть ваш конкурсний бал:")

    if user_score is None:  # Користувач натиснув "Скасувати"
        return

    # Читання даних з файлу
    competitors_df = read_competitors_from_txt(selected_file)

    # Фільтрація конкурентів
    filtered_competitors = filter_competitors(competitors_df, user_score)

    # Показ даних у вікні Tkinter
    show_data_in_window(filtered_competitors, os.path.basename(selected_file))

if __name__ == "__main__":
    main()
