import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import webbrowser

def validate_file(file_path):
    if not os.path.isfile(file_path):
        messagebox.showerror("Помилка", "Обраний файл не існує.")
        return False
    if not file_path.endswith('.txt'):
        messagebox.showerror("Помилка", "Обраний файл не є текстовим файлом.")
        return False
    return True

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
        
    df = pd.DataFrame(data, columns=['Ранг', 'Ім\'я', 'Статус', 'Пріоритет', 'Бали'])
    df = df.sort_values(by='Пріоритет') #Сортування
    #Додавання початкових статистик (пізніше це зробити нереально)
    global min_score, max_score, average_score, count_1, count_2, count_3, all
    average_score = df['Бали'].mean()
    max_score = df['Бали'].max()
    min_score = df['Бали'].min()
    all = len(df)
    count_1, count_2, count_3 = count_priorities(df)
    # Додавання колонки з посиланнями
    df['Посилання'] = df['Ім\'я'].apply(generate_link)
    return df

def generate_link(name):
    parts = name.split()
    if len(parts) < 2:
        return ""
    surname = parts[0]
    first_initial = parts[1][0]
    if len(parts) > 2:
        middle_initial = parts[2][0]
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}+{middle_initial}"
    else:
        return f"https://abit-poisk.org.ua/#search-{surname}+{first_initial}"



def filter_competitors(df, user_score, status_list=None, max_priority=3):
    if status_list is None:
        status_list = ['Допущено', 'Заява надійшла з сайту', 'Зареєстровано']
    
    filtered_df = df[
        (df['Статус'].isin(status_list)) &
        (df['Бали'] >= user_score) &
        (df['Пріоритет'].apply(lambda x: x.isdigit() and int(x) <= max_priority))
    ]
    return filtered_df

def count_priorities(df):
    priority_counts = df['Пріоритет'].value_counts()
    count_1 = priority_counts.get('1', 0)
    count_2 = priority_counts.get('2', 0)
    count_3 = priority_counts.get('3', 0)
    return count_1, count_2, count_3

def open_link(event):
    item = tree.selection()[0]
    name = tree.item(item, "values")[2]  # Ім'я знаходиться в другому стовпчику
    link = generate_link(name)
    if link:
        webbrowser.open(link)

def save_filtered_data(df, original_file_name):
    filtered_file_name = f"{os.path.splitext(original_file_name)[0]}_filtered.txt"
    df.to_csv(filtered_file_name, sep='\t', index=False, encoding='utf-8')
    messagebox.showinfo("Збереження", f"Відфільтрований список збережено у файл {filtered_file_name}")

def export_to_format(df, original_file_name, file_format):
    file_name = f"{os.path.splitext(original_file_name)[0]}_filtered"
    if file_format == "Excel":
        df.to_excel(f"{file_name}.xlsx", index=False)
    elif file_format == "CSV":
        df.to_csv(f"{file_name}.csv", index=False)
    messagebox.showinfo("Експорт", f"Дані успішно експортовано у файл {file_name}.{file_format.lower()}")

def calculate_statistics(df):
    average_score_post = df['Бали'].mean()
    max_score_post = df['Бали'].max()
    min_score_post = df['Бали'].min()
    all_post = len(df)
    count_1_post, count_2_post, count_3_post = count_priorities(df)
    messagebox.showinfo("Статистика",f"Середній бал: {average_score:.2f}\n Після фільтрації: {average_score_post:.2f}\nМаксимальний бал: {max_score}\n  Після фільтрації: {max_score_post}\nМінімальний бал: {min_score}\n  Після фільтрації: {min_score_post}\nЗаяв з першим пріоритетом: {count_1}\n  Після фільтрації: {count_1_post}\nЗаяв з другим пріоритетом: {count_2}\n  Після фільтрації: {count_2_post}\nЗаяв з третім пріоритетом: {count_3}\n  Після фільтрації: {count_3_post}\nЗагальна кількість заяв: {all}\n  Після фільтрації: {all_post}")
def add_menu(window, df, original_file_name):
    menu_bar = tk.Menu(window)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Експортувати в TXT", command=lambda: save_filtered_data(df, original_file_name))
    file_menu.add_command(label="Експортувати в CSV", command=lambda: export_to_format(df, original_file_name, "CSV"))
    file_menu.add_separator()
    file_menu.add_command(label="Підрахувати статистику", command=lambda: calculate_statistics(df))
    menu_bar.add_cascade(label="Файл", menu=file_menu)
    window.config(menu=menu_bar)

def add_search(frame, tree):
    def search_tree(event=None):
        search_term = search_entry.get()
        for item in tree.get_children():
            values = tree.item(item, "values")
            if any(search_term.lower() in str(value).lower() for value in values):
                tree.selection_set(item)
                tree.see(item)
                break

    search_label = ttk.Label(frame, text="Пошук:")
    search_label.pack(side=tk.LEFT, padx=5)
    search_entry = ttk.Entry(frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    search_entry.bind('<Return>', search_tree)
    search_button = ttk.Button(frame, text="Шукати", command=search_tree)
    search_button.pack(side=tk.LEFT, padx=5)

def show_data_in_window(df, original_file_name):
    global tree
    window = tk.Tk()
    window.title("Перевірка конкуренції")
    window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))
    
    menu_frame = ttk.Frame(window)
    menu_frame.pack(side=tk.TOP, fill=tk.X)
    frame = ttk.Frame(window)
    frame.pack(expand=True, fill='both')

    df.insert(0, '№', range(1, len(df) + 1))

    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for index, row in df.iterrows():
        values = list(row)
        tree.insert('', 'end', values=values)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    tree.bind('<Double-1>', open_link)

    add_menu(window, df, original_file_name)
    add_search(menu_frame, tree)  # Додавання поля пошуку до верхньої частини вікна

    window.protocol("WM_DELETE_WINDOW", window.quit)  # Виклик завершення основного циклу при закритті вікна

    window.mainloop()

def main():
    root = tk.Tk()
    root.withdraw()  # Приховати основне вікно

    selected_file = filedialog.askopenfilename(
        title="Виберіть файл зі списком абітурієнтів",
        filetypes=[("Text files", "*.txt")],
        initialdir=os.path.dirname(os.path.abspath(__file__))
    )

    if not selected_file:
        messagebox.showerror("Помилка", "Файл не було обрано.")
        return

    if not validate_file(selected_file):
        return

    user_score = simpledialog.askfloat("Ваші бали", "Введіть ваш конкурсний бал:")

    if user_score is None:  # Користувач натиснув "Скасувати"
        return

    status_list = ['Допущено', 'Заява надійшла з сайту', 'Зареєстровано']
    competitors_df = read_competitors_from_txt(selected_file)
    filtered_competitors = filter_competitors(competitors_df, user_score, status_list)
    show_data_in_window(filtered_competitors, os.path.basename(selected_file))

if __name__ == "__main__":
    main()
