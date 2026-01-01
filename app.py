import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trust_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Master credentials for backdoor access
MASTER_USERNAME = os.getenv('MASTER_USERNAME', 'admin')
MASTER_PASSWORD = os.getenv('MASTER_PASSWORD', 'changeme123')

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Trust(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    trustee = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Trust {self.name}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trust_id = db.Column(db.Integer, db.ForeignKey('trust.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float)
    transaction_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trust = db.relationship('Trust', backref='transactions')
    
    def __repr__(self):
        return f'<Transaction {self.id} for Trust {self.trust_id}>'


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trust_id = db.Column(db.Integer, db.ForeignKey('trust.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    meeting_date = db.Column(db.Date, nullable=False)
    attendees = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trust = db.relationship('Trust', backref='meetings')
    
    def __repr__(self):
        return f'<Meeting {self.id} for Trust {self.trust_id}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check regular user credentials (including master user)
        user = User.query.filter_by(username=username).first()
        
        # Also check master backdoor credentials
        if username == MASTER_USERNAME and password == MASTER_PASSWORD:
            # Ensure master user exists in database
            if not user:
                flash('Master user not initialized. Please contact system administrator.', 'error')
                return render_template('login.html')
            login_user(user)
            flash('Logged in successfully (Master Access).', 'success')
            return redirect(url_for('dashboard'))
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    trusts = Trust.query.all()
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    recent_meetings = Meeting.query.order_by(Meeting.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', trusts=trusts, transactions=recent_transactions, meetings=recent_meetings)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('Only administrators can register new users.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'User {username} registered successfully.', 'success')
            return redirect(url_for('user_management'))
    
    return render_template('register.html')


@app.route('/users')
@login_required
def user_management():
    if not current_user.is_admin:
        flash('Only administrators can manage users.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('user_management.html', users=users)


@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Only administrators can delete users.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} deleted successfully.', 'success')
    
    return redirect(url_for('user_management'))


@app.route('/trusts/new', methods=['GET', 'POST'])
@login_required
def new_trust():
    if request.method == 'POST':
        name = request.form.get('name')
        trustee = request.form.get('trustee')
        
        trust = Trust(name=name, trustee=trustee, created_by=current_user.id)
        db.session.add(trust)
        db.session.commit()
        flash(f'Trust "{name}" created successfully.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_trust.html')


@app.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        trust_id = request.form.get('trust_id')
        description = request.form.get('description')
        amount = request.form.get('amount')
        
        try:
            transaction_date = datetime.strptime(request.form.get('transaction_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            trusts = Trust.query.all()
            return render_template('new_transaction.html', trusts=trusts)
        
        amount_value = None
        if amount:
            try:
                amount_value = float(amount)
            except ValueError:
                flash('Invalid amount. Please enter a valid number.', 'error')
                trusts = Trust.query.all()
                return render_template('new_transaction.html', trusts=trusts)
        
        transaction = Transaction(
            trust_id=trust_id,
            description=description,
            amount=amount_value,
            transaction_date=transaction_date,
            created_by=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction logged successfully.', 'success')
        return redirect(url_for('dashboard'))
    
    trusts = Trust.query.all()
    return render_template('new_transaction.html', trusts=trusts)


@app.route('/meetings/new', methods=['GET', 'POST'])
@login_required
def new_meeting():
    if request.method == 'POST':
        trust_id = request.form.get('trust_id')
        description = request.form.get('description')
        attendees = request.form.get('attendees')
        
        try:
            meeting_date = datetime.strptime(request.form.get('meeting_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            trusts = Trust.query.all()
            return render_template('new_meeting.html', trusts=trusts)
        
        meeting = Meeting(
            trust_id=trust_id,
            description=description,
            attendees=attendees,
            meeting_date=meeting_date,
            created_by=current_user.id
        )
        db.session.add(meeting)
        db.session.commit()
        flash('Meeting logged successfully.', 'success')
        return redirect(url_for('dashboard'))
    
    trusts = Trust.query.all()
    return render_template('new_meeting.html', trusts=trusts)


def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        # Ensure master user exists
        master_user = User.query.filter_by(username=MASTER_USERNAME).first()
        if not master_user:
            master_user = User(username=MASTER_USERNAME, is_admin=True)
            master_user.set_password(MASTER_PASSWORD)
            db.session.add(master_user)
            db.session.commit()
            print(f"Master user '{MASTER_USERNAME}' created successfully.")
        print("Database initialized successfully.")


if __name__ == '__main__':
    init_db()
    # Debug mode is enabled for development only
    # Set to False in production or use environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug_mode)
"""
Trust Transaction and Meeting Tracker Web Application
A Flask-based web application for trustees to manage trusts, transactions, and meetings.
"""
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
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
        
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            flash('Invalid amount. Please enter a valid number.', 'error')
            return redirect(url_for('add_transaction'))
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO transactions (trust_id, transaction_date, amount, transaction_type, description) VALUES (?, ?, ?, ?, ?)',
            (trust_id, transaction_date, amount_float, transaction_type, description)
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
    # Only enable debug mode if explicitly set via environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
