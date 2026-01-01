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
    app.run(debug=True)
