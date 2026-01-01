# Trust Transaction Meeting Tracking

A web-based tracker that has knowledge of all trusts controlled by trustee and allows the trustee to log transactions and meetings using a web form.

## Features

- **User Management**: Create and manage user accounts with role-based access (admin/regular users)
- **Authentication**: Secure login/logout functionality with password hashing
- **Master Backdoor Access**: Emergency access using master credentials configured via environment variables
- **Trust Management**: Create and track multiple trusts with trustee information
- **Transaction Logging**: Log financial transactions for each trust
- **Meeting Logging**: Track meetings related to each trust
- **Dashboard**: View all trusts, recent transactions, and meetings in one place

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation
# Trust Transaction Meeting Tracker

A web-based application for trustees to manage trusts, financial transactions, and meetings. This application provides an intuitive interface for tracking all trust-related activities with a SQLite database backend.

## Features

- **Trust Management**: Track all trusts with details like trustee name, establishment date, and description
- **Transaction Tracking**: Log financial transactions (deposits, withdrawals, transfers, etc.) for each trust
- **Meeting Logging**: Record meetings with date, time, location, attendees, and notes
- **Separate Views**: Dedicated pages for viewing all transactions and meetings across all trusts
- **User-Friendly Interface**: Clean, modern web interface with responsive design

## Requirements

- Python 3.7+
- Flask 3.0.0
- SQLite (included with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/keiop2030/trust_transaction_meeting_tracking.git
cd trust_transaction_meeting_tracking
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
2. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` file to set your master credentials and secret key:
```
MASTER_USERNAME=admin
MASTER_PASSWORD=your_secure_password_here
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///trust_tracker.db
```

5. Run the application:
3. Initialize the database:
```bash
python init_db.py
```

This will create a SQLite database (`trust_tracker.db`) with sample data.

## Usage

1. Start the web application:
```bash
python app.py
```

The application will be available at http://localhost:5000

## Master Backdoor Access

For emergency access, use the master credentials configured in your `.env` file:
- Username: Value of `MASTER_USERNAME` (default: admin)
- Password: Value of `MASTER_PASSWORD` (default: changeme123)

**IMPORTANT**: Change the default master password in production!

## First Time Setup

1. Login using the master credentials
2. Navigate to "Users" to create additional user accounts
3. Create trusts via "New Trust"
4. Start logging transactions and meetings

## Usage

### User Roles

- **Admin**: Can create/delete users, manage all trusts, transactions, and meetings
- **Regular User**: Can create trusts and log transactions/meetings

### Creating a Trust

1. Click "New Trust" in the navigation bar
2. Enter trust name and trustee information
3. Submit the form

### Logging Transactions

1. Click "New Transaction"
2. Select the trust
3. Enter description, amount (optional), and date
4. Submit the form

### Logging Meetings

1. Click "New Meeting"
2. Select the trust
3. Enter description, attendees (optional), and date
4. Submit the form

## Security Features

- Password hashing using Werkzeug's security utilities
- Session management with Flask-Login
- Master backdoor credentials stored in environment variables (not in code)
- CSRF protection through Flask's built-in security features

## Production Deployment

**IMPORTANT**: Before deploying to production, make sure to:

1. Set `FLASK_DEBUG=False` in your `.env` file
2. Change `SECRET_KEY` to a strong random value (use `python -c "import secrets; print(secrets.token_hex(32))"`)
3. Change `MASTER_PASSWORD` to a strong, unique password
4. Use a production-grade database (PostgreSQL, MySQL) instead of SQLite
5. Set up HTTPS/SSL for secure connections
6. Use a production WSGI server (e.g., Gunicorn, uWSGI) instead of Flask's development server
7. Consider additional security measures like rate limiting and IP whitelisting

## Database

The application uses SQLite by default, stored in `trust_tracker.db`. The database is automatically initialized on first run.
2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - View all trusts on the home page
   - Add new trusts
   - View detailed information for each trust
   - Add and view financial transactions
   - Add and view meeting records

### Development vs Production

**Development Mode:** To enable debug mode during development:
```bash
export FLASK_DEBUG=true
python app.py
```

**Production Deployment:** Set the `SECRET_KEY` environment variable to a secure random value:
```bash
export SECRET_KEY='your-secure-random-secret-key'
python app.py
```

**Note:** Debug mode is disabled by default for security. Never enable debug mode in production.

## Database Schema

### Trusts Table
- `id`: Primary key
- `name`: Trust name
- `trustee_name`: Name of the trustee
- `date_established`: When the trust was established
- `description`: Additional information about the trust
- `created_at`: Record creation timestamp

### Transactions Table
- `id`: Primary key
- `trust_id`: Foreign key to trusts table
- `transaction_date`: Date of the transaction
- `amount`: Transaction amount (negative for withdrawals)
- `transaction_type`: Type (Deposit, Withdrawal, Transfer, etc.)
- `description`: Transaction details
- `created_at`: Record creation timestamp

### Meetings Table
- `id`: Primary key
- `trust_id`: Foreign key to trusts table
- `meeting_date`: Date of the meeting
- `meeting_time`: Time of the meeting
- `location`: Meeting location
- `attendees`: List of attendees
- `notes`: Meeting notes
- `created_at`: Record creation timestamp

## Project Structure

```
trust_transaction_meeting_tracking/
├── app.py                  # Main Flask application
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page (trusts list)
│   ├── add_trust.html    # Add new trust form
│   ├── trust_detail.html # Trust details with transactions and meetings
│   ├── transactions.html # All transactions view
│   ├── add_transaction.html # Add transaction form
│   ├── meetings.html     # All meetings view
│   └── add_meeting.html  # Add meeting form
└── static/
    └── style.css         # Stylesheet for the application
```

## License

MIT License
