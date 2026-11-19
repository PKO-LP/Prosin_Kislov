import tkinter as tk
from tkinter import ttk, messagebox

class PizzaOrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyПицца — Учёт заказов пиццерии")
        self.root.geometry("820x520")
        self.root.resizable(False, False)

        # Цены на пиццу (в рублях)
        self.prices = {
            "Маргарита": 450,
            "Пепперони": 550,
            "Четыре сыра": 600,
            "Гавайская": 520,
            "Мясная": 650
        }
        # Коэффициенты размера
        self.size_multipliers = {
            "Маленькая (25 см)": 1.0,
            "Средняя (30 см)": 1.3,
            "Большая (35 см)": 1.6
        }

        # Хранилище заказов в памяти (список словарей по ТЗ)
        self.orders = []
        self.next_id = 1

        self._create_widgets()
        self._load_demo_data()

    def _create_widgets(self):
        # Верхняя панель: форма ввода
        form_frame = ttk.LabelFrame(self.root, text="Новый / Редактируемый заказ", padding=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        # Выбор пиццы
        ttk.Label(form_frame, text="Пицца:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pizza_var = tk.StringVar(value="Пепперони")
        self.pizza_cb = ttk.Combobox(form_frame, textvariable=self.pizza_var, values=list(self.prices.keys()), state="readonly", width=18)
        self.pizza_cb.grid(row=0, column=1, padx=5, pady=5)

        # Выбор размера
        ttk.Label(form_frame, text="Размер:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.size_var = tk.StringVar(value="Средняя (30 см)")
        self.size_cb = ttk.Combobox(form_frame, textvariable=self.size_var, values=list(self.size_multipliers.keys()), state="readonly", width=18)
        self.size_cb.grid(row=0, column=3, padx=5, pady=5)

        # Количество
        ttk.Label(form_frame, text="Кол-во:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.qty_entry = ttk.Entry(form_frame, width=8)
        self.qty_entry.insert(0, "1")
        self.qty_entry.grid(row=0, column=5, padx=5, pady=5)

        # Статус
        ttk.Label(form_frame, text="Статус:").grid(row=0, column=6, sticky="w", padx=5, pady=5)
        self.status_var = tk.StringVar(value="Готовится")
        self.status_cb = ttk.Combobox(form_frame, textvariable=self.status_var, values=["Готовится", "Готов", "Выдан"], state="readonly", width=12)
        self.status_cb.grid(row=0, column=7, padx=5, pady=5)

        # Кнопки управления
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill="x", padx=10)

        ttk.Button(btn_frame, text="Добавить заказ", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Изменить выбранный", command=self.update_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Удалить выбранный", command=self.delete_order).pack(side="left", padx=5)

        # Поиск
        ttk.Label(btn_frame, text="Поиск:").pack(side="left", padx=(30, 5))
        self.search_entry = ttk.Entry(btn_frame, width=20)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())
        ttk.Button(btn_frame, text="Сброс", command=self.reset_search).pack(side="left", padx=2)

        # Таблица заказов
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "pizza", "size", "qty", "total", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.tree.heading("id", text="№")
        self.tree.heading("pizza", text="Пицца")
        self.tree.heading("size", text="Размер")
        self.tree.heading("qty", text="Кол-во")
        self.tree.heading("total", text="Сумма (руб.)")
        self.tree.heading("status", text="Статус")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("pizza", width=160)
        self.tree.column("size", width=160)
        self.tree.column("qty", width=80, anchor="center")
        self.tree.column("total", width=120, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _calculate_total(self, pizza, size, qty):
        base = self.prices[pizza]
        mult = self.size_multipliers[size]
        return int(round(base * mult * qty))

    def _validate_qty(self):
        val = self.qty_entry.get().strip()
        if not val.isdigit() or int(val) <= 0 or int(val) > 50:
            messagebox.showerror("Ошибка ввода", "Количество должно быть целым числом от 1 до 50.")
            return None
        return int(val)

    def add_order(self):
        qty = self._validate_qty()
        if qty is None:
            return

        pizza = self.pizza_var.get()
        size = self.size_var.get()
        status = self.status_var.get()
        total = self._calculate_total(pizza, size, qty)

        self.orders.append({
            "id": self.next_id,
            "pizza": pizza,
            "size": size,
            "qty": qty,
            "total": total,
            "status": status
        })
        self.next_id += 1
        self.refresh_table()

    def update_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ в таблице для изменения.")
            return

        qty = self._validate_qty()
        if qty is None:
            return

        order_id = int(self.tree.item(selected[0])["values"][0])
        pizza = self.pizza_var.get()
        size = self.size_var.get()
        status = self.status_var.get()
        total = self._calculate_total(pizza, size, qty)

        for order in self.orders:
            if order["id"] == order_id:
                order.update({"pizza": pizza, "size": size, "qty": qty, "total": total, "status": status})
                break

        self.refresh_table()

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления.")
            return

        order_id = int(self.tree.item(selected[0])["values"][0])
        self.orders = [o for o in self.orders if o["id"] != order_id]
        self.refresh_table()

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])["values"]
        self.pizza_var.set(values[1])
        self.size_var.set(values[2])
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, str(values[3]))
        self.status_var.set(values[5])

    def reset_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.search_entry.get().strip().lower()
        for o in self.orders:
            if query in o["pizza"].lower() or query in o["status"].lower() or query == str(o["id"]):
                self.tree.insert("", tk.END, values=(o["id"], o["pizza"], o["size"], o["qty"], o["total"], o["status"]))

    def _load_demo_data(self):
        demo = [
            ("Пепперони", "Большая (35 см)", 2, "Готовится"),
            ("Маргарита", "Средняя (30 см)", 1, "Готов"),
            ("Четыре сыра", "Маленькая (25 см)", 3, "Выдан")
        ]
        for pizza, size, qty, status in demo:
            self.orders.append({
                "id": self.next_id,
                "pizza": pizza,
                "size": size,
                "qty": qty,
                "total": self._calculate_total(pizza, size, qty),
                "status": status
            })
            self.next_id += 1
        self.refresh_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaOrderApp(root)
    root.mainloop()
