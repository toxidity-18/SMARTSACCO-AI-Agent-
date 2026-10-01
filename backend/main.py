"""
main.py
-------
FastAPI backend for the SmartSACCO AI Agent.
"""

import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI(title="SmartSACCO API", version="1.0.0")

# Allow CORS so Streamlit Cloud can talk to this Render backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define database path
DB_PATH = os.path.join(os.path.dirname(__file__), "sacco.db")

def initialize_database():
    """Creates tables and inserts mock data if they don't exist."""
    print("=== STARTING DATABASE INITIALIZATION ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS members (
        member_id TEXT PRIMARY KEY, full_name TEXT, account_status TEXT, savings_balance REAL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS loans (
        loan_id TEXT PRIMARY KEY, member_id TEXT, outstanding_balance REAL
    )''')
    
    # Insert mock data (INSERT OR IGNORE prevents duplicates on restart)
    cursor.execute("INSERT OR IGNORE INTO members VALUES ('M001', 'John Kamau', 'Active', 150000.0)")
    cursor.execute("INSERT OR IGNORE INTO members VALUES ('M002', 'Mary Wanjiku', 'Active', 20000.0)")
    cursor.execute("INSERT OR IGNORE INTO members VALUES ('M003', 'Peter Ochieng', 'Active', 300000.0)")
    cursor.execute("INSERT OR IGNORE INTO loans VALUES ('L001', 'M001', 30000.0)")
    
    conn.commit()
    conn.close()
    print("=== DATABASE INITIALIZATION COMPLETE ===")

# Run initialization when the server starts
@app.on_event("startup")
def startup_event():
    initialize_database()

@app.get("/")
def read_root():
    return {"status": "SmartSACCO API is running", "version": "1.0.0"}

@app.get("/api/members/{member_id}/financial-summary")
def get_financial_summary(member_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM members WHERE member_id = ?", (member_id,))
        member = cursor.fetchone()

        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        cursor.execute("SELECT outstanding_balance FROM loans WHERE member_id = ?", (member_id,))
        loan = cursor.fetchone()
        
        outstanding_loan = loan["outstanding_balance"] if loan else 0.0

        return {
            "member_id": member["member_id"],
            "full_name": member["full_name"],
            "account_status": member["account_status"],
            "savings_balance": float(member["savings_balance"]),
            "outstanding_loan_balance": float(outstanding_loan)
        }

    except HTTPException:
        raise
    except Exception as e:
        # Print the exact error to the Render logs so we can debug it
        print(f"!!! BACKEND ERROR: {str(e)} !!!")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()