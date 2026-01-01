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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

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
