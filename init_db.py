"""
Database initialization script for Trust Transaction and Meeting Tracker.
Creates the SQLite database schema.
"""
import sqlite3
import os

DB_NAME = 'trust_tracker.db'

def init_database():
    """Initialize the database with required tables."""
    # Remove existing database if it exists (for fresh start)
    if os.path.exists(DB_NAME):
        print(f"Removing existing database: {DB_NAME}")
        os.remove(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create trusts table
    cursor.execute('''
        CREATE TABLE trusts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            trustee_name TEXT NOT NULL,
            date_established DATE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trust_id INTEGER NOT NULL,
            transaction_date DATE NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trust_id) REFERENCES trusts (id)
        )
    ''')
    
    # Create meetings table
    cursor.execute('''
        CREATE TABLE meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trust_id INTEGER NOT NULL,
            meeting_date DATE NOT NULL,
            meeting_time TIME,
            location TEXT,
            attendees TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trust_id) REFERENCES trusts (id)
        )
    ''')
    
    # Insert sample data for demonstration
    cursor.execute('''
        INSERT INTO trusts (name, trustee_name, date_established, description)
        VALUES 
            ('Smith Family Trust', 'John Doe', '2020-01-15', 'Family trust for estate planning'),
            ('Johnson Charitable Trust', 'Jane Smith', '2019-06-20', 'Charitable contributions trust'),
            ('Williams Living Trust', 'John Doe', '2021-03-10', 'Revocable living trust')
    ''')
    
    # Insert sample transactions
    cursor.execute('''
        INSERT INTO transactions (trust_id, transaction_date, amount, transaction_type, description)
        VALUES 
            (1, '2024-01-15', 50000.00, 'Deposit', 'Initial funding'),
            (1, '2024-03-20', -5000.00, 'Withdrawal', 'Beneficiary distribution'),
            (2, '2024-02-10', 25000.00, 'Deposit', 'Annual contribution'),
            (3, '2024-01-05', 100000.00, 'Deposit', 'Property transfer')
    ''')
    
    # Insert sample meetings
    cursor.execute('''
        INSERT INTO meetings (trust_id, meeting_date, meeting_time, location, attendees, notes)
        VALUES 
            (1, '2024-01-10', '14:00', 'Law Office Conference Room', 'John Doe, Smith Family', 'Discussed trust setup and funding'),
            (2, '2024-02-05', '10:00', 'Virtual Meeting', 'Jane Smith, Board Members', 'Annual charity allocation review'),
            (1, '2024-06-15', '15:30', 'Client Office', 'John Doe, Smith Family', 'Quarterly review of trust performance')
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database '{DB_NAME}' created successfully!")
    print("Sample data inserted for demonstration.")

if __name__ == '__main__':
    init_database()
