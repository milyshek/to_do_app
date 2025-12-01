A command-line Python application that allows users to manage personal tasks stored in a MySQL database. Users can create accounts, log in, and perform full CRUD (Create, Read, Update, Delete) operations on their tasks. Each task can have a title, deadline, description, status, priority, and reminders.

**Key Features:**
- User authentication: unique usernames for sign-up and login.
- Task management: add, delete, update title, description, due date, status, and priority.
- Reminders: set reminders for tasks relative to deadlines or custom times.
- Task searching and filtering by title or due date.
- Handles multiple tasks with the same title using clarification prompts.
- Database-backed: uses MySQL to store users, tasks, and reminders.

**Technologies:**

- Python 3.13
- mysql-connector-python for database operations
- datetime for handling deadlines and reminders
