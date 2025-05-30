from models import get_db_connection



# ──────────────── Add Transaction Function ────────────────
def add_transaction(user_id, category_id, amount, day, month, year, notes=""):
    """
    Inserts a new transaction into the transactions table,
    using separate day, month, year, and notes fields.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO transactions 
              (user_id, category_id, amount, day, month, year, notes)
            VALUES 
              (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, category_id, amount, day, month, year, notes)
        )
        conn.commit()
        return True, "Transaction added successfully."
    except Exception as e:
        return False, f"Error adding transaction: {e}"
    finally:
        cursor.close()
        conn.close()


# ──────────────── Get Categories Function ────────────────
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# ──────────────── Add New Category Function ────────────────
def add_category(name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Category added successfully."
    except Exception as e:
        return False, str(e)


# ──────────────── Get User Balance Function ────────────────
def get_user_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return float(result[0])
    return 0.0


# ──────────────── Update User Balance Function ────────────────
def update_user_balance(user_id, new_balance):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Balance updated successfully."
    except Exception as e:
        return False, str(e)



# ──────────────── Get User Balance ────────────────
def get_user_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0.0

# ──────────────── Get User Transactions ────────────────
def get_user_transactions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.category_name, t.amount, t.day, t.month, t.year, t.notes
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
        ORDER BY t.year DESC, t.month DESC, t.day DESC
    """, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


# ──────────────── Get Filtered Transaction Function ────────────────
def get_filtered_transactions(user_id,
                              category_id=None,
                              min_amount=None,
                              max_amount=None,
                              month=None,
                              year=None):
    """
    Fetch transactions for user_id applying optional filters.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Base query
    query = """
        SELECT c.category_name,
               t.amount,
               t.day, t.month, t.year,
               t.notes
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = %s
    """
    params = [user_id]

    # Append filters
    if category_id is not None:
        query += " AND t.category_id = %s"
        params.append(category_id)
    if min_amount is not None:
        query += " AND t.amount >= %s"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND t.amount <= %s"
        params.append(max_amount)
    if month is not None:
        query += " AND t.month = %s"
        params.append(month)
    if year is not None:
        query += " AND t.year = %s"
        params.append(year)

    query += " ORDER BY t.year DESC, t.month DESC, t.day DESC"

    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results





# ──────────────── Get Expense Function ────────────────
def get_expense_summary(user_id):
    """
    Returns a dict of category_name -> total amount spent by the user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.category_name, SUM(t.amount)
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
            GROUP BY c.category_name
        """, (user_id,))
        
        rows = cursor.fetchall()
        return {category: float(total) for category, total in rows}
    except Exception as e:
        print(f"[get_expense_summary] Error: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()



# ──────────────── Get Expense Count Function ────────────────
def get_expense_counts(user_id):
    """
    Returns a dict of category_name -> number of expenses by the user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT c.category_name, COUNT(*)
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
            GROUP BY c.category_name
        """, (user_id,))
        rows = cursor.fetchall()
        return {category: int(count) for category, count in rows}
    except Exception as e:
        print(f"[get_expense_counts] Error: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()



# ──────────────── Get Monthly Expense Summary ────────────────
def get_monthly_expense_summary(user_id, year):
    """
    Returns an ordered dict of month_name -> total amount spent by the user for the given year.
    If year is None, uses current year.
    """
    from datetime import datetime
    if year is None:
        year = datetime.now().year

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.month, SUM(t.amount)
            FROM transactions t
            WHERE t.user_id = %s AND t.year = %s
            GROUP BY t.month
            ORDER BY t.month
        """, (user_id, year))
        rows = cursor.fetchall()
        # map month number to month name
        import calendar
        summary = {calendar.month_name[m]: float(total) for m, total in rows}
        return summary
    except Exception as e:
        print(f"[get_monthly_expense_summary] Error: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

