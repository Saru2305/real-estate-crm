
import sqlite3

DATABASE = "crm.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    # =========================
    # USERS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Admin account
    conn.execute("""
        INSERT OR IGNORE INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "Admin",
        "admin@gmail.com",
        "admin123",
        "Admin"
    ))

    # Sales employee account
    conn.execute("""
        INSERT OR IGNORE INTO users
        (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (
        "Sales Employee",
        "sales@gmail.com",
        "sales123",
        "Sales Employee"
    ))


    # =========================
    # LEADS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            source TEXT,
            stage TEXT DEFAULT 'New',
            assigned_to INTEGER,
            notes TEXT,
            follow_up_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (assigned_to)
            REFERENCES users(id)
        )
    """)


    # =========================
    # PROPERTIES TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            building_name TEXT,
            unit_number TEXT NOT NULL,
            property_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Available',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =========================
    # BOOKINGS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            lead_id INTEGER NOT NULL,

            property_id INTEGER NOT NULL,

            booked_by INTEGER NOT NULL,

            amount REAL DEFAULT 0,

            status TEXT DEFAULT 'Confirmed',

            booking_date TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (lead_id)
            REFERENCES leads(id),

            FOREIGN KEY (property_id)
            REFERENCES properties(id),

            FOREIGN KEY (booked_by)
            REFERENCES users(id)
        )
    """)


    conn.commit()
    conn.close()

