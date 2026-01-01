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

## Database

The application uses SQLite by default, stored in `trust_tracker.db`. The database is automatically initialized on first run.

## License

MIT License
