# StudyMate

## Overview
StudyMate is a platform designed to assist students in efficiently organizing their study routines, setting study goals, and monitoring their academic progress. This Flask application incorporates user authentication, allowing users to register, log in, and manage their study items. Users can view their completed study items, add new ones, edit existing ones, mark them as done, and delete them.

The application utilizes Flask for web development, Flask-SQLAlchemy for database management, Flask-Login for user authentication, and Werkzeug for password hashing.


## Schema
The application has three tables in the database ``study_items.db``:

### User Table
Table Name: User

- **id** Integer, Primary Key
- **username:** Unique, Not Null
- **email:** Unique, Not Null
- **password:** Not Null (hashed password)
- **tasks:** Relationship with Task Table (One-to-Many)

### Task Table
Table Name: Task

- **id** Integer, Primary Key
- **task** Not Null
- **user_id:** Integer, Foreign Key referencing User Table
- **tag_id:** Relationship with Tag Table (Many-to-one)

### Category Table
Table Name: Tag

- **id** Integer, Primary Key
- **name** Not Null

The tables uses a system where each user (from the User table) can have multiple tasks associated with them (in the Task table) and multiple tasks to one category(in the Tag table).


### Key Features
1. User Registration and Authentication: Users can register for an account and securely log in to access their study items.
2. Study Item Management: Users can view, add, edit, mark as completed, and delete study items.
3. Categorization: Study items can be categorized by subject for easy organization.
4. Filtering: Users can filter their views based on study item categories.
5. Progress Tracking: Users have an overview of completed study goals, providing insight into their academic achievements.
6. Paging View: The initial 5 study items are displayed on the study item page, with the remaining items shown in next pages format for improved user experience.

## Setup and Local Deployment

## Starter Code
The Studymate app uses Flask, SQLAlchemy and werkzeug.security

- The application logic is in app.py
- The code for managing the database is in the /instance folder.
- The html files are in /templates folder
- The stylesheets are in /static folder

### Prerequisites
- Python
- pip (Python package installer)

### Installation
1. Clone the repository:

    ``````
    git clone https://github.com/tobiloba7/StudyMate
    cd studymate
    ``````

2. Install the dependencies using pip:

    ```pip install -r requirements.txt```

## Running the application

1. Run the Flask app: Start the application in debug mode by running:
    ```flask --debug run```
2. Open your browser and go to [http://localhost:5000]

These are the routes that app.py serves:

- '/' is the index route, and it shows a the created study items
- '/login' is the route to login to the app
- '/register' is the registration route for new users
- '/logout' is the route to log out

**Task routes:**
- '/add' is the route to add study items
- '/layout' is the route for the add study item
- '/edit/<int:id>' is the route to edit tasks
- '/check/<int:id>' is to check completed task
- '/delete/<int:id>' is to remove tasks
- '/tag/<tag>' to filter study items by tag
- '/completed' to view all completed study items 

Click through all of the pages to see how they currently behave.
Rendered app- https://codecavetodoapp.onrender.com
