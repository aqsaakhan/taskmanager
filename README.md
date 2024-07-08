# TaskMaster

TaskMaster is a comprehensive web-based task management application designed to help users organize, track, and complete their tasks efficiently.

## Live Demo

Visit the live application: https://aqsaakhan.pythonanywhere.com

For demo purposes, you can use the following credentials:
- Username: aqsaanwar
- Password: 1234

## Features

- User Authentication
- Task Management (CRUD operations)
- Task Completion Tracking
- Data Persistence
- RESTful API
- Asynchronous Processing with RabbitMQ
- Data Analysis

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask framework
- Database: SQLAlchemy with SQLite
- Authentication: Flask-Login
- Session Management: Flask-Session
- Message Queue: RabbitMQ
- Asynchronous Tasks: Celery
- API: Flask-based RESTful API
- Deployment: PythonAnywhere

## Key Requirements Fulfilled

- Messaging Queue: Implemented using RabbitMQ for asynchronous task processing
- REST API: Provides programmatic access to task data
- Persistence Data Storage: Uses SQLite database for storing user and task information
- Data Analysis: Includes basic statistics on task completion and user productivity

## Repository

The source code for TaskMaster is available at: https://github.com/aqsaakhan/taskmanager

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Initialize the database
6. Ensure RabbitMQ is installed and running
7. Run the application: `python app.py`

For detailed installation instructions, please refer to the project documentation.

## API Usage

The TaskMaster API provides endpoints for task management. For detailed API documentation, please refer to the API section in the application.

Contributions to TaskMaster are welcome! Please feel free to submit a Pull Request.

This project is licensed under the MIT License.
