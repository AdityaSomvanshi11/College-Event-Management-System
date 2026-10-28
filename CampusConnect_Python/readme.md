# CampusConnect – College Event Management System

CampusConnect is a Python-based desktop application designed to manage college events and student participation. It provides separate dashboards for administrators, teachers, and students, with Oracle Database integration for storing and managing information.

## Features

### Admin Dashboard
- View and manage student information.
- Access college event management features.
- Manage event-related information.

### Teacher Dashboard
- Access assigned event-related features.
- Manage student attendance.

### Student Dashboard
- Register as a student.
- View available college events.
- Register for events.
- View registered events.
- Cancel registrations when attendance has not been recorded.
- View attendance records.

## Technologies Used

- **Programming Language:** Python
- **GUI:** Tkinter
- **Database:** Oracle Database
- **Database Connectivity:** `oracledb`
- **Development Environment:** Visual Studio Code

## Project Structure

```text
CampusConnect_Python/
│
├── database.py
├── login.py
├── admin.py
├── teacher.py
├── student.py
├── event.py
├── registration.py
├── attendance.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

Before running the project, install:

1. Python 3
2. Oracle Database with the required project tables and sequences
3. Python packages listed in `requirements.txt`

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/CampusConnect-Python.git
cd CampusConnect-Python
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the Database

- Start your Oracle Database.
- Create the project database user, tables, and sequences.
- Configure the connection details securely in `database.py`.
- Ensure that the database connection settings match your local Oracle setup.

Never publish database passwords or other private credentials in a public repository.

### 4. Run the Application

```bash
python login.py
```

## Database

The application uses Oracle Database to store information related to:

- Administrators
- Teachers
- Students
- Events
- Registrations
- Attendance

## Learning Outcomes

This project demonstrates the use of Python GUI development, database connectivity, SQL operations, user authentication, event registration, and attendance management.

## Future Enhancements

- Improved dashboard design
- Event notifications
- Event reports and analytics
- Enhanced authentication and access control

## Author

**Aditya Somvanshi**

MCA – Cloud Computing

## License

This project is intended for academic and learning purposes.

"""
