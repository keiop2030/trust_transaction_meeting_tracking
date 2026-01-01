"""
Trust Transaction and Meeting Tracker Web Application
A Flask-based web application for trustees to manage trusts, transactions, and meetings.
"""
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'trust_tracker_secret_key_2024'
DB_NAME = 'trust_tracker.db'

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_trusts():
    """Retrieve all trusts from the database."""
    conn = get_db_connection()
    trusts = conn.execute('SELECT * FROM trusts ORDER BY name').fetchall()
    conn.close()
    return trusts

@app.route('/')
def index():
    """Home page showing all trusts."""
    trusts = get_all_trusts()
    return render_template('index.html', trusts=trusts)

@app.route('/trust/<int:trust_id>')
def trust_detail(trust_id):
    """Show details for a specific trust."""
    conn = get_db_connection()
    trust = conn.execute('SELECT * FROM trusts WHERE id = ?', (trust_id,)).fetchone()
    
    if trust is None:
        conn.close()
        flash('Trust not found', 'error')
        return redirect(url_for('index'))
    
    transactions = conn.execute(
        'SELECT * FROM transactions WHERE trust_id = ? ORDER BY transaction_date DESC',
        (trust_id,)
    ).fetchall()
    
    meetings = conn.execute(
        'SELECT * FROM meetings WHERE trust_id = ? ORDER BY meeting_date DESC',
        (trust_id,)
    ).fetchall()
    
    conn.close()
    return render_template('trust_detail.html', trust=trust, transactions=transactions, meetings=meetings)

@app.route('/trust/add', methods=['GET', 'POST'])
def add_trust():
    """Add a new trust."""
    if request.method == 'POST':
        name = request.form['name']
        trustee_name = request.form['trustee_name']
        date_established = request.form.get('date_established')
        description = request.form.get('description')
        
        if not name or not trustee_name:
            flash('Name and Trustee Name are required!', 'error')
            return redirect(url_for('add_trust'))
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO trusts (name, trustee_name, date_established, description) VALUES (?, ?, ?, ?)',
            (name, trustee_name, date_established if date_established else None, description)
        )
        conn.commit()
        conn.close()
        
        flash('Trust added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_trust.html')

@app.route('/transactions')
def transactions():
    """View all transactions across all trusts."""
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT t.*, tr.name as trust_name
        FROM transactions t
        JOIN trusts tr ON t.trust_id = tr.id
        ORDER BY t.transaction_date DESC
    ''').fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/transaction/add', methods=['GET', 'POST'])
def add_transaction():
    """Add a new transaction."""
    if request.method == 'POST':
        trust_id = request.form['trust_id']
        transaction_date = request.form['transaction_date']
        amount = request.form['amount']
        transaction_type = request.form['transaction_type']
        description = request.form.get('description')
        
        if not trust_id or not transaction_date or not amount or not transaction_type:
            flash('All required fields must be filled!', 'error')
            return redirect(url_for('add_transaction'))
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO transactions (trust_id, transaction_date, amount, transaction_type, description) VALUES (?, ?, ?, ?, ?)',
            (trust_id, transaction_date, float(amount), transaction_type, description)
        )
        conn.commit()
        conn.close()
        
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    trusts = get_all_trusts()
    return render_template('add_transaction.html', trusts=trusts)

@app.route('/meetings')
def meetings():
    """View all meetings across all trusts."""
    conn = get_db_connection()
    meetings = conn.execute('''
        SELECT m.*, t.name as trust_name
        FROM meetings m
        JOIN trusts t ON m.trust_id = t.id
        ORDER BY m.meeting_date DESC
    ''').fetchall()
    conn.close()
    return render_template('meetings.html', meetings=meetings)

@app.route('/meeting/add', methods=['GET', 'POST'])
def add_meeting():
    """Add a new meeting."""
    if request.method == 'POST':
        trust_id = request.form['trust_id']
        meeting_date = request.form['meeting_date']
        meeting_time = request.form.get('meeting_time')
        location = request.form.get('location')
        attendees = request.form.get('attendees')
        notes = request.form.get('notes')
        
        if not trust_id or not meeting_date:
            flash('Trust and Meeting Date are required!', 'error')
            return redirect(url_for('add_meeting'))
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO meetings (trust_id, meeting_date, meeting_time, location, attendees, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (trust_id, meeting_date, meeting_time, location, attendees, notes)
        )
        conn.commit()
        conn.close()
        
        flash('Meeting added successfully!', 'success')
        return redirect(url_for('meetings'))
    
    trusts = get_all_trusts()
    return render_template('add_meeting.html', trusts=trusts)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
