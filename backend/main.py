"""
main.py
-------
This script defines the FastAPI REST API for the SmartSACCO backend.
It exposes endpoints that allow external applications (like our AI Agent)
to query member financial data securely.
"""

from fastapi import FastAPI, HTTPException
import sqlite3
import os

# Initialize the FastAPI application instance.
# This object handles incoming web requests and routes them to the correct functions.
# We provide metadata here so it shows up in the auto-generated API documentation.
app = FastAPI(
    title="SmartSACCO API",
    description="Backend API for querying SACCO member financial data.",
    version="1.0.0"
)

# Define the path to our SQLite database.
# We use os.path to ensure it works regardless of the current working directory.
DB_PATH = os.path.join(os.path.dirname(__file__), "sacco.db")

def get_db_connection():
    """
    Helper function to establish a connection to the SQLite database.
    We set row_factory to sqlite3.Row so we can access columns by name 
    instead of just index numbers, making the code more readable and maintainable.
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
    
    Technical details:
    - Accepts a member_id as a path parameter.
    - Queries the 'members' and 'loans' tables using parameterized queries.
    - Returns a JSON object with the member's savings, outstanding loan, and status.
    
    Non-technical details:
    - This is the endpoint our AI will call when a user asks about their account balance 
      or loan status. It gathers all the raw numbers the AI needs to make a decision.
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
            "savings_balance": member["savings_balance"],
            "outstanding_loan_balance": outstanding_loan
        }

        return summary

    finally:
        # The 'finally' block ensures the database connection is always closed, 
        # even if an error occurs during the query. This prevents memory leaks.
        conn.close()