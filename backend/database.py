"""
database.py
-----------
This script initializes our mock SACCO database using SQLite.
It creates the necessary tables and populates them with dummy data 
so our REST API has something to query during testing.
"""

import sqlite3
import os

# Define the name of our SQLite database file. 
# It will be created in the 'backend' folder where this script runs.
DB_NAME = "sacco.db"

def setup_database():
    """
    Connects to the SQLite database, creates the required tables, 
    and inserts mock member data if the database is empty.
    """
    
    # 1. Establish a connection to the database. 
    # If 'sacco.db' doesn't exist, SQLite will automatically create it.
    conn = sqlite3.connect(DB_NAME)
    
    # 2. Create a cursor object. 
    # The cursor allows us to execute SQL commands and fetch results.
    cursor = conn.cursor()

    # ==========================================
    # TABLE CREATION
    # ==========================================
    
    # Create the 'members' table
    # We use 'IF NOT EXISTS' so running this script twice doesn't crash the app.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            member_id TEXT PRIMARY KEY,  -- Unique ID for the member (e.g., 'M001')
            full_name TEXT NOT NULL,     -- Member's full name
            phone_number TEXT NOT NULL,  -- Contact number
            savings_balance REAL NOT NULL, -- Current savings in KES (Real handles decimals)
            account_status TEXT NOT NULL   -- 'Active', 'Dormant', or 'Suspended'
        )
    """)

    # Create the 'loans' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            loan_id TEXT PRIMARY KEY,    -- Unique ID for the loan
            member_id TEXT NOT NULL,     -- Foreign key linking to the members table
            loan_amount REAL NOT NULL,   -- Total loan amount taken in KES
            outstanding_balance REAL NOT NULL, -- How much they still owe
            FOREIGN KEY (member_id) REFERENCES members(member_id)
        )
    """)

    # ==========================================
    # MOCK DATA INSERTION
    # ==========================================
    
    # Check if we already have data to prevent duplicate entries
    cursor.execute("SELECT COUNT(*) FROM members")
    if cursor.fetchone()[0] == 0:
        print("Database is empty. Inserting mock SACCO member data...")
        
        # Insert mock members. 
        # Notice the varying savings balances. We will use these later to test 
        # the AI's logic (e.g., a member with low savings shouldn't get a huge loan).
        mock_members = [
            ('M001', 'John Kamau', '0711111111', 150000.00, 'Active'),    # High saver
            ('M002', 'Mary Wanjiku', '0722222222', 25000.00, 'Active'),   # Low saver
            ('M003', 'Peter Ochieng', '0733333333', 80000.00, 'Active'),  # Medium saver
            ('M004', 'Amina Hassan', '0744444444', 5000.00, 'Dormant')    # Dormant account
        ]
        
        # Insert the members into the database
        cursor.executemany("""
            INSERT INTO members (member_id, full_name, phone_number, savings_balance, account_status)
            VALUES (?, ?, ?, ?, ?)
        """, mock_members)

        # Insert mock loans. 
        # We are giving John (M001) a loan, but leaving others without active loans for testing.
        mock_loans = [
            ('L001', 'M001', 50000.00, 30000.00) # John has an outstanding balance of 30k
        ]
        
        cursor.executemany("""
            INSERT INTO loans (loan_id, member_id, loan_amount, outstanding_balance)
            VALUES (?, ?, ?, ?)
        """, mock_loans)

        # Commit the transaction to save the changes to the database file
        conn.commit()
        print("Mock data inserted successfully!")
    else:
        print("Database already contains data. Skipping insertion.")

    # ==========================================
    # VERIFICATION (Optional but good for debugging)
    # ==========================================
    
    # Let's fetch and print the data to prove it worked
    print("\n--- Current Members in Database ---")
    cursor.execute("SELECT member_id, full_name, savings_balance FROM members")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Savings: KES {row[2]:,.2f}")

    # Close the connection to free up resources
    conn.close()
    print("\n Database setup complete! 'sacco.db' is ready.")


# This ensures the setup function only runs if we execute this file directly 
# (e.g., `python database.py`), and not if it's imported by another file.
if __name__ == "__main__":
    setup_database()