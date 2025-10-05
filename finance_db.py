# finance_db.py
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

DB_PATH = "finance_data.db"

def init_database():
    """Initialize the finance database with necessary tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # User profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        monthly_income REAL NOT NULL,
        status TEXT,
        dependents INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # Expenses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # Savings goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS savings_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0,
        deadline TEXT,
        status TEXT DEFAULT 'active',
        created_at TEXT NOT NULL
    )
    """)
    
    # Budget rules table (for 50/30/20 tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budget_allocations (
        id INTEGER PRIMARY KEY,
        needs_percentage REAL DEFAULT 50,
        wants_percentage REAL DEFAULT 30,
        savings_percentage REAL DEFAULT 20,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Insert default budget allocation if not exists
    cursor.execute("SELECT COUNT(*) FROM budget_allocations")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO budget_allocations (needs_percentage, wants_percentage, savings_percentage, updated_at) VALUES (?, ?, ?, ?)",
            (50, 30, 20, datetime.now().isoformat())
        )
    
    conn.commit()
    conn.close()
    return "Database initialized successfully"

def save_user_profile(name: str, monthly_income: float, status: str = "Single", dependents: int = 0):
    """Save or update user profile"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if profile exists
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    exists = cursor.fetchone()[0] > 0
    
    if exists:
        cursor.execute("""
        UPDATE user_profile 
        SET name=?, monthly_income=?, status=?, dependents=?
        WHERE id=1
        """, (name, monthly_income, status, dependents))
    else:
        cursor.execute("""
        INSERT INTO user_profile (id, name, monthly_income, status, dependents, created_at)
        VALUES (1, ?, ?, ?, ?, ?)
        """, (name, monthly_income, status, dependents, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_user_profile():
    """Get user profile"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_profile WHERE id=1")
    profile = cursor.fetchone()
    conn.close()
    
    if profile:
        return dict(profile)
    return None

def add_expense(date: str, category: str, amount: float, note: str = ""):
    """Add a new expense"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO expenses (date, category, amount, note, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (date, category, amount, note, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_expenses(start_date: str = None, end_date: str = None):
    """Get expenses with optional date filtering"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if start_date and end_date:
        cursor.execute("""
        SELECT * FROM expenses 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
        """, (start_date, end_date))
    else:
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    
    expenses = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in expenses]

def delete_expense(expense_id: int):
    """Delete an expense by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    
    conn.commit()
    conn.close()

def add_savings_goal(goal_name: str, target_amount: float, deadline: str = None):
    """Add a new savings goal"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO savings_goals (goal_name, target_amount, deadline, created_at)
    VALUES (?, ?, ?, ?)
    """, (goal_name, target_amount, deadline, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

def get_savings_goals():
    """Get all active savings goals"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM savings_goals WHERE status='active' ORDER BY created_at DESC")
    goals = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in goals]

def update_goal_progress(goal_id: int, current_amount: float):
    """Update savings goal progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE savings_goals 
    SET current_amount=?
    WHERE id=?
    """, (current_amount, goal_id))
    
    conn.commit()
    conn.close()

def get_expense_summary_by_category():
    """Get total expenses grouped by category"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT category, SUM(amount) as total
    FROM expenses
    GROUP BY category
    ORDER BY total DESC
    """)
    
    summary = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in summary]

# Initialize database when module is imported
if not os.path.exists(DB_PATH):
    init_database()