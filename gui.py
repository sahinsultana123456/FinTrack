import tkinter as tk
from tkinter import ttk, simpledialog
import tkinter.font as tkFont
import services_auth, services
import calendar
from tkcalendar import DateEntry
from datetime import datetime
from decimal import Decimal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




#Main Window
root = None

# ──────────────── Main Window ────────────────
def main_gui():
    global root
    root = tk.Tk()
    root.title("FinTrack - Personal Finance Tracker")
    root.geometry("700x500")
    root.configure(bg="black")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="black", foreground="white", font=("Arial", 16))
    style.configure("TButton", background="black", foreground="white")
    style.map("TButton",
              background=[("active", "#B6DA95")],
              foreground=[("active", "#08180b")])

    ttk.Label(root, text="FinTrack", font=("Arial", 24), foreground="#008000").pack(pady=(100, 10))
    ttk.Label(root, text="Personal Finance Tracker and Analyzer",
              font=("Arial", 22), foreground="#90EE90").pack()

    ttk.Button(root, text="Register", command=register_user_window).pack(pady=5)
    ttk.Button(root, text="Login", command=login_user_window).pack(pady=5)

    root.mainloop()

# ──────────────── Registration Window ────────────────
def register_user_window():
    win = tk.Toplevel()
    win.title("Register")
    win.configure(bg="black")
    win.geometry("350x300")

    ttk.Label(win, text="Username:", background="black", foreground="white", font=("Arial", 12)).pack(pady=(20, 5))
    username_entry = tk.Entry(win, bg="black", fg="white", insertbackground="white", font=("Arial", 12))
    username_entry.pack(pady=5)

    ttk.Label(win, text="Password:", background="black", foreground="white", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(win, bg="black", fg="white", insertbackground="white", font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    ttk.Label(win, text="Confirm Password:", background="black", foreground="white", font=("Arial", 12)).pack(pady=5)
    confirm_entry = tk.Entry(win, bg="black", fg="white", insertbackground="white", font=("Arial", 12), show="*")
    confirm_entry.pack(pady=5)

    def register_action():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm = confirm_entry.get().strip()

        if not username or not password or not confirm:
            show_error_popup("Input Error", "All fields are required.")
            return
        if password != confirm:
            show_error_popup("Mismatch", "Passwords do not match.")
            return

        success, msg = services_auth.register_user(username, password)
        if success:
            show_success_popup(msg)
            win.destroy()
        else:
            show_error_popup("Registration Failed", msg)

    ttk.Button(win, text="Register", command=register_action).pack(pady=15)

# ──────────────── Login Window ────────────────
def login_user_window():
    win = tk.Toplevel()
    win.title("Login")
    win.configure(bg="black")
    win.geometry("350x250")

    ttk.Label(win, text="Username:", background="black", foreground="white", font=("Arial", 12)).pack(pady=(20, 5))
    username_entry = tk.Entry(win, bg="black", fg="white", insertbackground="white", font=("Arial", 12))
    username_entry.pack(pady=5)

    ttk.Label(win, text="Password:", background="black", foreground="white", font=("Arial", 12)).pack(pady=5)
    password_entry = tk.Entry(win, bg="black", fg="white", insertbackground="white", font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    def login_action():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            show_error_popup("Input Error", "Username and password are required.")
            return

        success, user_id = services_auth.login_user(username, password)
        if success:
            show_success_popup(f"Login successful. Welcome, {username}!")
            win.destroy()
            root.withdraw()
            dashboard_window(user_id, username)
        else:
            show_error_popup("Login Failed", "Invalid username or password.")

    ttk.Button(win, text="Login", command=login_action).pack(pady=15)


# # ──────────────── Dashboard Window (after login) ────────────────
def dashboard_window(user_id, username):
    dash = tk.Toplevel()
    dash.title("FinTrack Dashboard")
    dash.geometry("700x500")
    dash.configure(bg="black")

    style = ttk.Style(dash)
    style.theme_use("clam")
    style.configure("TLabel", background="black", foreground="white", font=("Arial", 16))
    style.configure("TButton", background="black", foreground="white", padding=10)
    style.map("TButton",
              background=[("active", "#B6DA95")],
              foreground=[("active", "#08180b")])

    # Welcome text
    ttk.Label(dash, text=f"Welcome, {username}", font=("Arial", 24), foreground="#008000").pack(pady=(80, 10))
    ttk.Label(dash, text="Personal Finance Tracker and Analyzer",
              font=("Arial", 22), foreground="#90EE90").pack()

    # Frame for two buttons side by side
    button_frame = tk.Frame(dash, bg="black")
    # button_frame = ttk.Frame(dash)
    button_frame.pack(pady=50)

    # Add Transactions button
    add_trans_btn = ttk.Button(button_frame, text="Add Transactions", command=lambda: add_transaction_window(user_id))
    add_trans_btn.grid(row=0, column=0, padx=(0, 20))  # 20px gap on right

    # Balance Enquiry button
    balance_btn = ttk.Button(button_frame, text="Balance Enquiry", command=lambda: balance_enquiry_window(user_id))
    balance_btn.grid(row=0, column=1)

    # inside dashboard_window(...) after your other buttons:
    # ttk.Button(
    #     button_frame,
    #     text="View Expense Chart",
    #     command=lambda: lollipop_chart_window(user_id)
    # ).grid(row=0, column=2, padx=(20,0))

    ttk.Button(
    button_frame,
    text="View Expense Charts",
    command=lambda: view_expense_charts_window(user_id)).grid(row=0, column=2, padx=(20,0))


    # Logout button
    def logout_action():
        show_success_popup("Logged out successfully.")  # Show success popup
        dash.destroy()
        root.deiconify()

    ttk.Button(dash, text="Logout", command=logout_action).pack(pady=20)


# # ──────────────── Lolipop Chart Function ────────────────
def lollipop_chart_window(user_id):
    summary = services.get_expense_summary(user_id)
    counts = services.get_expense_counts(user_id)  # New helper defined in service.py

    if not summary or not counts:
        show_error_popup("No Data", "No expense data available to display.")
        return

    categories = list(summary.keys())
    amounts = [summary[cat] for cat in categories]
    tx_counts = [counts.get(cat, 0) for cat in categories]

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Use distinct colors
    cmap = plt.get_cmap('tab10')
    colors = [cmap(i % 10) for i in range(len(categories))]

    # Plot vertical lollipop chart
    for i, (cat, amt, cnt) in enumerate(zip(categories, amounts, tx_counts)):
        ax.vlines(x=i, ymin=0, ymax=amt, color=colors[i], linewidth=2)
        ax.scatter(i, amt, color=colors[i], s=80, zorder=3)

        # Label above each dot
        ax.text(
            i, amt + max(amounts) * 0.02,
            f"₹{amt:.0f} | {cnt} txn{'s' if cnt != 1 else ''}",
            ha='center', va='bottom', color='white', fontsize=9
        )

    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10, color='white')
    ax.set_ylabel("Total Spent (₹)", fontsize=12, color='white')
    ax.set_title("Spending per Category", fontsize=14, color='white')

    plt.tight_layout()
    plt.show()

# # ──────────────── View Expense Chart Function ────────────────
def view_expense_charts_window(user_id):
    win = tk.Toplevel()
    win.title("Expense Charts")
    win.geometry("1000x700")
    win.configure(bg="black")

    style = ttk.Style(win)
    style.configure("TButton", background="black", foreground="white", padding=6)
    style.map("TButton",
              background=[("active", "#B6DA95")],
              foreground=[("active", "#08180b")])

    # Year selection frame
    top_frame = tk.Frame(win, bg="black")
    top_frame.pack(fill="x", pady=5, padx=10)

    tk.Label(top_frame, text="Select Year:", bg="black", fg="white", font=("Arial", 10)).pack(side="left")

    # Example: available years (ideally, get this list dynamically from your data)
    current_year = 2025  # or datetime.datetime.now().year
    available_years = [str(y) for y in range(current_year - 5, current_year + 1)]

    year_var = tk.StringVar(value=available_years[-1])  # default current year

    year_combo = ttk.Combobox(top_frame, values=available_years, textvariable=year_var, state="readonly", width=6)
    year_combo.pack(side="left", padx=5)

    btn_frame = tk.Frame(win, bg="black")
    btn_frame.pack(fill="x", pady=(10, 0))

    canvas_frame = tk.Frame(win, bg="black")
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#121212')
    ax.set_facecolor('#121212')
    canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw_category_chart():
        ax.clear()
        summary = services.get_expense_summary(user_id)
        counts = services.get_expense_counts(user_id)
        if not summary:
            show_error_popup("No Data", "No expense data available.")
            return

        cats = list(summary.keys())
        amounts = [summary[c] for c in cats]
        txns = [counts.get(c, 0) for c in cats]

        cmap = plt.get_cmap('tab10')
        colors = [cmap(i % 10) for i in range(len(cats))]

        for i, (c, a, t) in enumerate(zip(cats, amounts, txns)):
            ax.vlines(i, 0, a, color=colors[i], linewidth=2)
            ax.scatter(i, a, color=colors[i], s=80, zorder=3)
            ax.text(i, a + max(amounts) * 0.02, f"₹{a:.0f} | {t} txn{'s' if t != 1 else ''}",
                    ha='center', va='bottom', color='white', fontsize=9)

        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels(cats, rotation=60, ha='right', fontsize=9, color='white')
        ax.set_ylabel("Total Spent (₹)", fontsize=12, color='white')
        ax.set_title("Spending per Category", fontsize=14, color='white')

        fig.tight_layout()
        canvas.draw()

    def draw_monthly_chart():
        ax.clear()
        selected_year = int(year_var.get())
        month_summary = services.get_monthly_expense_summary(user_id, selected_year)
        if not month_summary:
            show_error_popup("No Data", f"No monthly data available for year {selected_year}.")
            return

        months = list(month_summary.keys())
        amounts = list(month_summary.values())

        cmap = plt.get_cmap('tab10')
        colors = [cmap(i % 10) for i in range(len(months))]

        for i, (m, a) in enumerate(zip(months, amounts)):
            ax.vlines(i, 0, a, color=colors[i], linewidth=2)
            ax.scatter(i, a, color=colors[i], s=80, zorder=3)
            ax.text(i, a + max(amounts) * 0.02, f"₹{a:.0f}", ha='center', va='bottom', color='white', fontsize=9)

        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha='right', fontsize=10, color='white')
        ax.set_ylabel("Total Spent (₹)", fontsize=12, color='white')
        ax.set_title(f"Monthly Expense Trend - {selected_year}", fontsize=14, color='white')

        fig.tight_layout()
        canvas.draw()

    def on_year_change(event):
        # redraw the currently visible chart with new year
        if current_view.get() == "monthly":
            draw_monthly_chart()

    year_combo.bind("<<ComboboxSelected>>", on_year_change)

    current_view = tk.StringVar(value="category")

    def show_category():
        current_view.set("category")
        draw_category_chart()

    def show_monthly():
        current_view.set("monthly")
        draw_monthly_chart()

    ttk.Button(btn_frame, text="Category Wise", command=show_category).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Monthly Wise", command=show_monthly).pack(side="left", padx=10)

    ttk.Button(btn_frame, text="Download Report in PDF", command=lambda: generate_pdf_report(user_id)).pack(side="left", padx=10)


    draw_category_chart()  # default



# ──────────────── Add Transaction Window ────────────────
def add_transaction_window(user_id):
    win = tk.Toplevel()
    win.title("Add Transaction")
    win.geometry("420x460")
    win.configure(bg="black")

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("TLabel", background="black", foreground="white", font=("Arial", 12))
    style.configure("TEntry", fieldbackground="black", foreground="white", insertcolor="white")
    style.configure("TCombobox", fieldbackground="black", foreground="white")
    style.configure("TButton", background="black", foreground="white", padding=8)
    style.map("TButton",
        background=[("active", "#B6DA95")],
        foreground=[("active", "#08180b")]
    )

    # ─── Date Picker ───────────────────────────────────────────────
    date_frame = tk.Frame(win, bg="black")
    date_frame.pack(fill="x", padx=20, pady=(20, 15))
    tk.Label(date_frame, text="Date:", bg="black", fg="white", font=("Arial", 12)).grid(
        row=0, column=0, sticky="w", padx=(0, 10)
    )
    date_picker = DateEntry(
        date_frame, width=18, font=('Arial', 12), date_pattern='yyyy-MM-dd',
        background="#2b2b2b", foreground="white", borderwidth=2,
        headersbackground="#444444", headersforeground="white",
        normalbackground="#2b2b2b", normalforeground="white",
        weekendbackground="#333333", weekendforeground="white",
        othermonthforeground="#666666", othermonthbackground="#2b2b2b",
        selectbackground="#B6DA95", selectforeground="black",
        arrowcolor="white"
    )
    date_picker.grid(row=0, column=1, sticky="w")

    # ─── Amount ────────────────────────────────────────────────────
    ttk.Label(win, text="Amount:").pack(anchor="w", padx=20, pady=(0, 5))
    amount_entry = ttk.Entry(win, font=("Arial", 12), justify="right")
    amount_entry.pack(fill="x", padx=20, pady=(0, 15))

    # ─── Category ──────────────────────────────────────────────────
    ttk.Label(win, text="Category:").pack(anchor="w", padx=20, pady=(0, 5))
    def refresh_categories():
        cats = services.get_categories()
        names = [name for _, name in cats]
        return cats, names + ["Add New Category"]
    cats, cat_names = refresh_categories()
    cat_var = tk.StringVar()
    cat_cb = ttk.Combobox(win, textvariable=cat_var, values=cat_names, state="readonly", font=("Arial", 12))
    cat_cb.pack(fill="x", padx=20, pady=(0, 15))

    def handle_category_selection(event):
        if cat_var.get() == "Add New Category":
            cat_win = tk.Toplevel(win)
            cat_win.title("New Category")
            cat_win.geometry("300x120")
            cat_win.configure(bg="black")
            ttk.Label(cat_win, text="Enter new category name:", background="black", foreground="white").pack(padx=10, pady=10)
            new_cat_var = tk.StringVar()
            new_entry = tk.Entry(cat_win, textvariable=new_cat_var, bg="black", fg="white", insertbackground="white", font=("Arial", 12))
            new_entry.pack(padx=10, pady=(0, 10))
            def save_new_cat():
                name = new_cat_var.get().strip()
                if not name:
                    show_error_popup("Input Error", "Please enter a category name.")
                    return
                success, msg = services.add_category(name)
                if success:
                    show_success_popup(msg)
                    cat_win.destroy()
                    nonlocal cats, cat_names
                    cats, cat_names = refresh_categories()
                    cat_cb['values'] = cat_names
                    cat_var.set(name)
                else:
                    show_error_popup("Error", msg)
            ttk.Button(cat_win, text="Add", command=save_new_cat).pack(pady=(0, 10))
    cat_cb.bind("<<ComboboxSelected>>", handle_category_selection)

    # ─── Notes ─────────────────────────────────────────────────────
    ttk.Label(win, text="Notes:").pack(anchor="w", padx=20, pady=(0, 5))
    notes_entry = ttk.Entry(win, font=("Arial", 12))
    notes_entry.pack(fill="x", padx=20, pady=(0, 20))

    # ─── Helper to collect & validate input ───────────────────────
    def collect_fields():
        sel = date_picker.get_date()
        day, month, year = sel.day, sel.month, sel.year
        amt = amount_entry.get().strip()
        cat_name = cat_var.get().strip()
        notes = notes_entry.get().strip()
        if not amt or not cat_name or cat_name == "Add New Category":
            show_error_popup("Input Error", "Please fill in Amount and Category.")
            return None
        try:
            amount = float(amt)
        except:
            show_error_popup("Input Error", "Amount must be a number.")
            return None
        try:
            category_id = next(cid for cid, nm in cats if nm == cat_name)
        except StopIteration:
            show_error_popup("Error", "Selected category not found.")
            return None
        return day, month, year, amount, category_id, notes

    # ─── Actions ──────────────────────────────────────────────────
    def add_and_update_balance():
        sel_date = date_picker.get_date()
        day, month, year = sel_date.day, sel_date.month, sel_date.year

        amt_text = amount_entry.get().strip()
        cat_name = cat_var.get().strip()
        notes = notes_entry.get().strip()

        if not amt_text or not cat_name or cat_name == "Add New Category":
            show_error_popup("Input Error", "Please fill in Amount and Category.")
            return
        try:
            amount = Decimal(amt_text)  #Convert to Decimal instead of float
        except:
            show_error_popup("Input Error", "Amount must be a number.")
            return

        try:
            category_id = next(cid for cid, nm in cats if nm == cat_name)
        except StopIteration:
            show_error_popup("Error", "Selected category not found.")
            return

        success, msg = services.add_transaction(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            day=day,
            month=month,
            year=year,
            notes=notes
        )
        if success:
            current = services.get_user_balance(user_id)
            new_bal = current - amount  #This now works because both are Decimal
            services.update_user_balance(user_id, new_bal)
            show_success_popup("Transaction added and balance updated.")
            win.destroy()
        else:
            show_error_popup("Database Error", msg)

    def add_without_balance_update():
        data = collect_fields()
        if not data: return
        day, month, year, amount, category_id, notes = data
        ok, msg = services.add_transaction(user_id, category_id, amount, day, month, year, notes)
        if ok:
            show_success_popup("Transaction added.")
            win.destroy()
        else:
            show_error_popup("Error", msg)

    # ─── Buttons ──────────────────────────────────────────────────
    btn_frame = tk.Frame(win, bg="black")
    btn_frame.pack(pady=(0, 20))
    ttk.Button(btn_frame, text="Add & Update Balance", command=add_and_update_balance).pack(side="left", padx=10)
    tk.Frame(btn_frame, width=10, bg="black").pack(side="left")
    ttk.Button(btn_frame, text="Add Without Balance Update", command=add_without_balance_update).pack(side="left", padx=10)




# ──────────────── Balance Enquiry Window ────────────────
def balance_enquiry_window(user_id):
    import calendar
    from datetime import datetime
    import tkinter as tk
    from tkinter import ttk

    win = tk.Toplevel()
    win.title("Balance Enquiry")
    win.geometry("650x500")
    win.configure(bg="black")

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("TLabel", background="black", foreground="white", font=("Arial", 12))
    style.configure("TButton", background="black", foreground="white", padding=6)
    style.map("TButton", background=[("active", "#B6DA95")], foreground=[("active", "#08180b")])
    style.configure("Treeview", background="black", foreground="white", fieldbackground="black", font=("Arial", 11))
    style.configure("Treeview.Heading", background="gray20", foreground="white", font=("Arial", 12, "bold"))
    style.configure("Black.TFrame", background="black")  # For black backgrounds on ttk.Frame if needed

    # ─── Display Current Balance ──────────────────────────────
    balance = services.get_user_balance(user_id)
    balance_label = ttk.Label(
        win,
        text=f"Your current balance: ₹ {balance:.2f}" if balance is not None else "Balance not available"
    )
    balance_label.pack(pady=(20, 5))

    # ─── Input for New Balance ────────────────────────────────
    ttk.Label(win, text="Enter your current balance:").pack()
    balance_entry = tk.Entry(
        win,
        font=("Arial", 12),
        justify="right",
        fg="white",
        bg="black",
        insertbackground="white"
    )
    balance_entry.pack(pady=5)

    def submit_balance():
        val = balance_entry.get().strip()
        try:
            new_bal = float(val)
        except ValueError:
            show_error_popup("Invalid Input", "Please enter a valid number.")
            return

        success, msg = services.update_user_balance(user_id, new_bal)
        if success:
            show_success_popup(msg)
            balance_label.config(text=f"Your current balance: ₹ {new_bal:.2f}")
        else:
            show_error_popup("Database Error", msg)

    ttk.Button(win, text="Submit", command=submit_balance).pack(pady=(0, 10))

    # ─── Transaction Table ────────────────────────────────────
    ttk.Label(win, text="Your Transactions:").pack(anchor="w", padx=20)

    columns = ("Category", "Amount", "Date", "Notes")
    tree = ttk.Treeview(win, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=140)
    tree.pack(fill="both", padx=20, pady=(5, 10), expand=True)

    def populate_tree(transactions):
        for item in tree.get_children():
            tree.delete(item)
        for t in transactions:
            # t: (category_name, amount, day, month, year, notes)
            date_str = f"{t[2]:02d}-{t[3]:02d}-{t[4]}"
            tree.insert("", "end", values=(t[0], f"₹ {t[1]:.2f}", date_str, t[5]))

    # Initial load
    all_tx = services.get_user_transactions(user_id)
    populate_tree(all_tx)

    def open_filter_window():
        fwin = tk.Toplevel(win)
        fwin.title("Filter Transactions")
        fwin.geometry("320x400")
        fwin.configure(bg="black")

        ttk.Label(fwin, text="Category:", background="black").pack(anchor="w", padx=20, pady=(20,5))
        cats = services.get_categories()
        cat_options = ["All"] + [name for _, name in cats]
        cat_var = tk.StringVar(value="All")
        ttk.Combobox(
            fwin,
            values=cat_options,
            textvariable=cat_var,
            state="readonly",
            font=("Arial", 12)
        ).pack(fill="x", padx=20)

        ttk.Label(fwin, text="Min Amount:", background="black").pack(anchor="w", padx=20, pady=(15,5))
        min_var = tk.StringVar()
        tk.Entry(
            fwin,
            textvariable=min_var,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Arial", 12)
        ).pack(fill="x", padx=20)

        ttk.Label(fwin, text="Max Amount:", background="black").pack(anchor="w", padx=20, pady=(15,5))
        max_var = tk.StringVar()
        tk.Entry(
            fwin,
            textvariable=max_var,
            bg="black",
            fg="white",
            insertbackground="white",
            font=("Arial", 12)
        ).pack(fill="x", padx=20)

        ttk.Label(fwin, text="Month:", background="black").pack(anchor="w", padx=20, pady=(15,5))
        months = ["All"] + list(calendar.month_name)[1:]
        month_var = tk.StringVar(value="All")
        ttk.Combobox(
            fwin,
            values=months,
            textvariable=month_var,
            state="readonly",
            font=("Arial", 12)
        ).pack(fill="x", padx=20)

        ttk.Label(fwin, text="Year:", background="black").pack(anchor="w", padx=20, pady=(15,5))
        current_year = datetime.now().year
        years = ["All"] + [str(y) for y in range(current_year, current_year-10, -1)]
        year_var = tk.StringVar(value="All")
        ttk.Combobox(
            fwin,
            values=years,
            textvariable=year_var,
            state="readonly",
            font=("Arial", 12)
        ).pack(fill="x", padx=20)

        def apply_filters():
            cat_sel = cat_var.get()
            cat_id = None if cat_sel == "All" else next((cid for cid, nm in cats if nm == cat_sel), None)
            min_amt = float(min_var.get()) if min_var.get().strip() else None
            max_amt = float(max_var.get()) if max_var.get().strip() else None
            mon = None if month_var.get() == "All" else months.index(month_var.get())
            yr = None if year_var.get() == "All" else int(year_var.get())

            filtered = services.get_filtered_transactions(
                user_id=user_id,
                category_id=cat_id,
                min_amount=min_amt,
                max_amount=max_amt,
                month=mon,
                year=yr
            )
            populate_tree(filtered)
            fwin.destroy()

        ttk.Button(fwin, text="Apply Filters", command=apply_filters).pack(pady=20)

    def clear_filters():
        populate_tree(all_tx)

    # Buttons frame with black background and black spacer
    btn_frame = ttk.Frame(win, style="Black.TFrame")
    btn_frame.pack(pady=(0, 5))

    ttk.Button(btn_frame, text="Filter", command=open_filter_window).pack(side="left")

    # Spacer with black bg using tk.Frame for perfect black gap
    gap = tk.Frame(btn_frame, width=10, bg="black", height=30)
    gap.pack(side="left")

    ttk.Button(btn_frame, text="Clear Filters", command=clear_filters).pack(side="left")





# ──────────────── Success Message Popup ────────────────
def show_success_popup(msg):
    # Create the popup window
    popup = tk.Toplevel()
    popup.title("Success")
    popup.configure(bg="black")

    # Choose a font for measurement and display
    display_font = ("Arial", 14)
    measure_font = tkFont.Font(family=display_font[0], size=display_font[1])

    # Measure the message width in pixels
    text_width_px = measure_font.measure(msg)

    # Determine window width: at least 300px, or message width + padding
    win_width = max(300, text_width_px + 40)
    win_height = 120

    # Apply geometry
    popup.geometry(f"{win_width}x{win_height}")
    popup.resizable(False, False)

    # Message label (with wrap if message is very long)
    label = ttk.Label(
        popup,
        text=msg,
        background="black",
        foreground="#00FF00",
        font=display_font,
        wraplength=win_width - 40
    )
    label.pack(pady=20, padx=20)

    # OK button
    def close():
        popup.destroy()

    ttk.Button(popup, text="OK", command=close).pack(pady=(0, 10))

    # Center the popup on screen
    popup.update_idletasks()
    screen_w = popup.winfo_screenwidth()
    screen_h = popup.winfo_screenheight()
    x = (screen_w // 2) - (popup.winfo_width() // 2)
    y = (screen_h // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")

    # Make modal
    popup.grab_set()
    popup.focus_set()
    popup.wait_window()

# ──────────────── Error Message Popup ────────────────
def show_error_popup(title, msg):
    popup = tk.Toplevel()
    popup.title(title)
    popup.configure(bg="black")
    popup.resizable(False, False)  # still prevent resizing by user

    # Dynamically wrap long messages at 40 characters per line
    label = ttk.Label(
        popup,
        text=msg,
        background="black",
        foreground="#FF4444",
        font=("Arial", 14),
        wraplength=300,  # Wraps text if too wide
        justify="center"
    )
    label.pack(padx=20, pady=20)

    def close():
        popup.destroy()

    ttk.Button(popup, text="OK", command=close).pack(pady=(0, 15))

    # Let Tkinter calculate natural window size before centering
    popup.update_idletasks()
    width = popup.winfo_reqwidth()
    height = popup.winfo_reqheight()
    x = (popup.winfo_screenwidth() // 2) - (width // 2)
    y = (popup.winfo_screenheight() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")

    # Modal behavior
    popup.grab_set()
    popup.focus_set()
    popup.wait_window()




from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from collections import defaultdict, OrderedDict
from datetime import datetime
import os
import mysql.connector

def generate_pdf_report(user_id):
    # — use your existing get_db_connection or inline credentials —
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sahin@Neel00",
        database="fintrack_database"
    )
    cursor = conn.cursor()

    # 1) Fetch exactly username & balance
    cursor.execute(
        "SELECT username, balance FROM users WHERE user_id = %s",
        (user_id,)
    )
    result = cursor.fetchone()
    if not result:
        show_error_popup("Report Error", "User not found.")
        cursor.close()
        conn.close()
        return

    username, balance = result

    # 2) Fetch year/category totals
    cursor.execute("""
        SELECT t.year, c.category_name, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        GROUP BY t.year, c.category_name
        ORDER BY t.year DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # 3) Organize into {year: {category: total}}
    year_data = defaultdict(lambda: defaultdict(float))
    for year, cat, tot in rows:
        year_data[year][cat] += float(tot)

    # 4) Keep only the latest 5 years
    sorted_years = sorted(year_data.keys(), reverse=True)[:5]
    limited = OrderedDict((yr, year_data[yr]) for yr in sorted_years)

    # 5) Create the PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"FinTrack_Report_{username}_{timestamp}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, height - 1*inch, "FinTrack Expense Report")
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 1.4*inch, f"User: {username}")
    c.drawString(1*inch, height - 1.7*inch, f"Current Balance: ₹{balance:,.2f}")
    c.drawString(1*inch, height - 2.0*inch,
                 f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 2.5*inch
    for yr, cats in limited.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1*inch, y, f"Year: {yr}")
        y -= 0.3*inch

        c.setFont("Helvetica", 12)
        for cat, amt in cats.items():
            c.drawString(1.2*inch, y, f"- {cat}: ₹{amt:,.2f}")
            y -= 0.25*inch
            if y < 1.5*inch:
                c.showPage()
                y = height - 1*inch

    c.save()

    # Auto-open the PDF (Windows/macOS)
    if os.name == 'nt':
        os.startfile(filename)
    else:
        os.system(f'open "{filename}"')

    show_success_popup(f"PDF report saved as:\n{filename}")






if __name__ == "__main__":
    main_gui()