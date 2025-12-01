import mysql.connector
import datetime


class Operation:
    def __enter__(self):
        self.cnx = mysql.connector.connect(user='', password='', database='to_do_list')
        self.cur = self.cnx.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cnx.commit()
        self.cur.close()
        self.cnx.close()

    def sign_in(self):
        print('Your username has to be unique')
        username = input('Input Your username:\n')
        query = "INSERT INTO users (userName) VALUES (%s)"

        try:
            self.cur.execute(query, params=(username, ))
        except mysql.connector.errors.IntegrityError:
            print(f"User {username} exists")

    def logging(self):
        username = input('Input Your username:\n')
        query = "SELECT userId FROM users WHERE userName = %s;"

        self.cur.execute(query, params=(username, ))
        row = self.cur.fetchone()

        if row is None:
            print("User has not been found")
            return None
        return int(row[0])

    def get_tasks(self, row, column1=None, value1=None, column2=None, value2=None):
        if value1 is None:
            query = ('SELECT * FROM tasks'
                     'WHERE userId=%s;')
            self.cur.execute(query, params=(row,))
            return self.cur.fetchall() if self.cur.fetchall() else None

        if value1 and value2:
            query = ('SELECT * FROM tasks'
                     'WHERE userId=%s'
                     'AND %s=%s'
                     'AND %s=%s;')
            self.cur.execute(query, params=(row, column1, value1, column2, value2))
            return self.cur.fetchall() if self.cur.fetchall() else None

        query = ('SELECT * FROM tasks'
                 'WHERE userId=%s'
                 'AND %s=%s;')
        self.cur.execute(query, params=(row, column1, value1))
        return self.cur.fetchall() if self.cur.fetchall() else None

    def get_task_id(self, row):
        title = input('Input title of task or print SHOW to print out existing tasks:\n')

        if title == 'SHOW':
            print('Existing tasks:')
            list_with_tasks = self.get_tasks(row)
            print(list_with_tasks)
            title = input('Input title of task:\n')
            list_with_tasks = self.get_tasks(row, 'title', title)

            if len(list_with_tasks) > 1:
                clarifier = input('Found too much matching tasks. '
                                  'Input due time (YY if You want to clarify '
                                  'or leave empty if You want to change status first tasks from list:\n')

                if clarifier:
                    due_time = None

                    while due_time is None:
                        try:
                            due_time = datetime.datetime.strptime(
                                input('Input a deadline (YYYY/MM/DD HH:MM):\n'),
                                "%Y/%m/%d %H:%M")
                        except ValueError:
                            print("Invalid format")
                            due_time = None

                    taskid = self.get_tasks(row, 'title', title, 'due_time', due_time)
                    if len(taskid) > 1:
                        taskid = taskid[0]
                else:
                    taskid = self.get_tasks(row, 'title', title)

            else:
                taskid = list_with_tasks[0]
        else:
            taskid = self.get_tasks(row, 'title', title)
            if not taskid:
                return 'Unfound'
        return int(str(taskid)) # I don't know if it works out

    def append_task(self, row):
        title = input('Input a title:\n')

        dt = None
        while dt is None:
            try:
                dt = datetime.datetime.strptime(
                    input('Input a deadline (YYYY/MM/DD HH:MM):\n'),
                    "%Y/%m/%d %H:%M")
            except ValueError:
                print("Invalid format")
                dt = None

        desc = input('Input description. If You do not want to add, leave it empty.\n')
        if not desc:
            desc = None

        status = input('Input status below. '
                       'Acceptable: (in progress, blocked, done, pending). '
                       'Default: in progress. '
                       'Leave empty to set default.\n').lower()
        if not status:
            status = None

        priority = None
        while priority not in ('Y', 'N'):
            priority = input('Input Y if You want to set high priority for this task. '
                         'Input N if not. \n').upper()
        priority = True if priority == 'Y' else False

        reminder = dt - datetime.timedelta(hours=1)

        query = ('INSERT INTO tasks (userId, title, due_time, description, status, priority)'
                 'VALUES (%s, %s, %s, %s, %s, %s);')

        self.cur.execute(query, params=(row, title, dt, desc, status, priority))
        task_id = self.cur.lastrowid
        query = ('INSERT INTO reminders (taskId, remindAt)'
                 'VALUES (%s, %s);')
        self.cur.execute(query, params=(task_id, reminder))
        return 'Done'

    def del_task(self, row):
        title = input('Input title of task or print SHOW to print out existing tasks:\n')
        if title == 'SHOW':
            print('Existing tasks:')
            list_with_tasks = self.get_tasks(row)

            if list_with_tasks:
                for value in range(len(list_with_tasks)):
                    print(f'-> {list_with_tasks[value-1]}')

        title = input('Input title of task')
        self.cur.execute('SELECT * FROM tasks '
                            'WHERE userId=%s AND title=%s;', params=(row, title))

        if self.cur.fetchall():
            query = ('DELETE FROM tasks '
             'WHERE taskId=%s;')
            self.cur.execute(query, params=(title, ))
            return 'Done'
        return 'Task has not been found'

    def set_status(self, row):
        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        new_status = None
        while new_status is None:
            new_status = input("Input new status of task. "
                               "Choose from: \n'in progress', \n'blocked', \n'done', \n'pending'\n->")
            if new_status not in ('in progress', 'blocked', 'done', 'pending'):
                print('Invalid value')

        query = ('UPDATE tasks '
                 'SET status = %s '
                 'WHERE taskId = %s;')
        self.cur.execute(query, params=(new_status, taskid))
        return 'Done'

    def set_task_priority(self, row):
        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        priority = None
        while priority is None:
            priority = input('Do You want to set priority for the task? Input Y/N').upper()
            if priority == 'Y':
                priority = True
            elif priority == 'N':
                priority = False
            else:
                priority = None


        query = ('UPDATE tasks '
                 'SET priority = %s '
                 'WHERE taskId = %s;')
        self.cur.execute(query, params=(priority, taskid))
        return 'Done'

    def add_desc(self, row):

        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        desc = input('Input a description:\n')

        query = ('UPDATE tasks '
                 'SET description = %s'
                 'WHERE taskId = %s;')
        self.cur.execute(query, params=(desc, taskid))
        return 'Done'

    def update_title(self, row):
        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        title = input('Input a title:\n')
        if len(title) > 100:
            print('title is too long' )

        query = ('UPDATE tasks '
                 'SET title = %s '
                 'WHERE taskId = %s;')
        self.cur.execute(query, params=(title, taskid))
        return 'Done'

    def update_time(self, row):
        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        dt = None
        while dt is None:
            try:
                dt = datetime.datetime.strptime(
                    input('Input a deadline (YYYY/MM/DD HH:MM):\n'),
                    "%Y/%m/%d %H:%M")
            except ValueError:
                print("Invalid format")
                dt = None

        query = ('UPDATE tasks '
                 'SET due_time = %s '
                 'WHERE taskId = %s;')
        self.cur.execute(query, params=(dt, taskid))
        return 'Done'

    def add_reminder(self, row):
        taskid = self.get_task_id(row)
        if taskid == 'Unfound':
            return taskid

        reminder = None
        while reminder is None:
            try:
                reminder = datetime.datetime.strptime(
                    input('Input a reminder (YYYY/MM/DD HH:MM):\n'),
                    "%Y/%m/%d %H:%M")
            except ValueError:
                print("Invalid format")
                reminder = None

        query = ('INSERT INTO reminders (taskId, remindAt)'
                 'VALUES (%s, %s);')
        self.cur.execute(query, params=(taskid, reminder))
        return 'Done'

    def find_task(self, row):
        value_name1 = input('Input title of the task'
                             ' or leave empty '
                             'if You do not want to clarify it with title:\n')
        value_name2  = input('Input due time of the task'
                             ' or leave empty '
                             'if You do not want to clarify it with due time:\n')

        if not value_name1:
            value_name1 = None
        if not value_name2:
            value_name2 = None

        list_with_tasks = self.get_tasks(row,
                                         column1='title',
                                         value1=value_name1,
                                         column2='due_time',
                                         value2=value_name2)

        for i in list_with_tasks:
            print(list_with_tasks[i-1])