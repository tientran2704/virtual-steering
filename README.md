# Virtual Steering System

A virtual steering system that uses hand gestures to control a virtual vehicle.

## Prerequisites

- Python 3.8 or higher
- MySQL Server 8.0 or higher
- MySQL Workbench
- Webcam

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtual-steering
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up MySQL Database:
   - Open MySQL Workbench
   - Connect to your MySQL server
   - Open the `database_setup.sql` file
   - Execute the SQL script to create the database and tables

5. Configure the database connection:
   - Open `app.py`
   - Update the MySQL connection string with your credentials:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/virtual_steering'
   ```

## Running the Application

1. Make sure MySQL server is running

2. Start the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Database Structure

### User Table
- id: Primary key
- username: Unique username
- email: Unique email address
- password_hash: Hashed password
- created_at: Account creation timestamp
- last_login: Last login timestamp

### User Sessions Table
- id: Primary key
- user_id: Foreign key to user table
- session_start: Session start timestamp
- session_end: Session end timestamp

### User Activity Log Table
- id: Primary key
- user_id: Foreign key to user table
- activity_type: Type of activity
- activity_details: Additional activity information
- created_at: Activity timestamp

## Features

- User registration and authentication
- Hand gesture recognition for virtual steering
- Session tracking
- Activity logging
- Responsive web interface

## Security Features

- Password hashing
- Session management
- SQL injection prevention
- XSS protection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Install game "Extreme Off-road 4x4 Driving" to controll   
