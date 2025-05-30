import mysql.connector

# ──────────────── Create Database ────────────────
def create_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="create_your_password"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS fintrack_database;")
    print("Database 'fintrack_database' created.")
    cursor.close()
    conn.close()

# ──────────────── Connect to Database ────────────────
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="create_your_password",
        database="fintrack_database"
    )

# ──────────────── Create Users Table ────────────────
def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ──────────────── Create Categories Table ────────────────
def create_categories_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(50) NOT NULL UNIQUE
    );
    """)

    default_categories = ["Food", "Rent", "Salary", "Utilities", "Transport", "Entertainment"]
    for category in default_categories:
        cursor.execute("""
        INSERT IGNORE INTO categories (category_name) VALUES (%s);
        """, (category,))

    conn.commit()
    cursor.close()
    conn.close()

# ──────────────── Create Transactions Table ────────────────
def create_transactions_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        category_id INT NOT NULL,
        amount DECIMAL(10,2),
        day INT,
        month INT,
        year INT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

# ──────────────── Master Setup Function ────────────────
def setup_database():
    create_database()
    create_users_table()
    create_categories_table()
    create_transactions_table()
    print("All tables created inside 'fintrack_database'.")

# ──────────────── Drop All Tables Function ────────────────
def drop_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop tables in order considering foreign keys
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("DROP TABLE IF EXISTS categories;")
    cursor.execute("DROP TABLE IF EXISTS users;")

    conn.commit()
    cursor.close()
    conn.close()
    print("All tables dropped successfully.")

# ──────────────── Run It ────────────────
if __name__ == "__main__":
    setup_database()
    # drop_all_tables()