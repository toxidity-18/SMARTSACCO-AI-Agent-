"""
main.py
-------
This script defines the FastAPI REST API for the SmartSACCO backend.
It exposes endpoints that allow external applications (like our AI Agent)
to query member financial data securely.
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import sqlite3
import os

# Define the path to our SQLite database.
DB_PATH = os.path.join(os.path.dirname(__file__), "sacco.db")

def initialize_database():
    """
    Creates the database tables and inserts mock data if the database does not exist.
    This ensures the API works immediately upon deployment to cloud platforms like Render.
    """
    if os.path.exists(DB_PATH):
        print("Database already exists. Skipping initialization.")
        return
    
    print("Initializing database with mock data...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,
            full_name TEXT,
            account_status TEXT,
            savings_balance REAL
        )
    ''')

    # Create loans table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            loan_id TEXT PRIMARY KEY,
            member_id TEXT,
            outstanding_balance REAL
        )
    ''')

    # Insert mock members
    mock_members = [
        ('M001', 'John Kamau', 'Active', 150000.0),
        ('M002', 'Mary Wanjiku', 'Active', 20000.0),
        ('M003', 'Peter Ochieng', 'Active', 300000.0),
        ('M004', 'Amina Hassan', 'Inactive', 5000.0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO members VALUES (?, ?, ?, ?)', mock_members)

    # Insert mock loans
    mock_loans = [
        ('L001', 'M001', 30000.0),
        ('L002', 'M003', 100000.0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO loans VALUES (?, ?, ?)', mock_loans)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# Define the lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code here runs on startup
    initialize_database()
    yield
    # Code here runs on shutdown (if needed)

# Initialize the FastAPI application instance with the lifespan context manager
app = FastAPI(
    title="SmartSACCO API",
    description="Backend API for querying SACCO member financial data.",
    version="1.0.0",
    lifespan=lifespan
)

def get_db_connection():
    """
    Helper function to establish a connection to the SQLite database.
    We set row_factory to sqlite3.Row so we can access columns by name.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    """
    Root endpoint. Acts as a health check to ensure the API server is running.
    """
    return {"status": "SmartSACCO API is running", "version": "1.0.0"}

@app.get("/api/members/{member_id}/financial-summary")
def get_financial_summary(member_id: str):
    """
    Retrieves the complete financial summary for a specific member.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch member details using a parameterized query to prevent SQL injection
        cursor.execute("SELECT * FROM members WHERE member_id = ?", (member_id,))
        member = cursor.fetchone()

        # If the member doesn't exist, raise a 404 Not Found HTTP exception
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Fetch their current outstanding loan balance (if any)
        cursor.execute(
            "SELECT outstanding_balance FROM loans WHERE member_id = ?", 
            (member_id,)
        )
        loan = cursor.fetchone()
        
        # If they have no active loan, set the outstanding balance to 0.0
        outstanding_loan = loan["outstanding_balance"] if loan else 0.0

        # Construct the response dictionary. FastAPI will automatically convert this to JSON.
        summary = {
            "member_id": member["member_id"],
            "full_name": member["full_name"],
            "account_status": member["account_status"],
            "savings_balance": float(member["savings_balance"]),
            "outstanding_loan_balance": float(outstanding_loan)
        }

        return summary

    finally:
        # The 'finally' block ensures the database connection is always closed.
        conn.close()