from operation_to_do_app import Operation
import mysql.connector


def operation_selector():
    menu_for_user = ('Choose:\n'
                     '-> 1 if You want to append a task\n'
                     '-> 2 if You want to delete a task\n'
                     '-> 3 if You want to change a status of task\n'
                     '-> 4 if You want to change task priority\n'
                     '-> 5 if You want to add a description\n'
                     '-> 6 if You want to change a title of task\n'
                     '-> 7 if You want to change a deadline of task\n'
                     '-> 8 if You want to add reminder\n'
                     '-> 9 if You want to find a task\n')
    function = input(f'{menu_for_user}\n')

    try:
        return int(function) if 0 < int(function) < 13 else None
    except ValueError:
        print('Invalid operation')
        return None


def is_redo():
    repeat = input('Do You want to repeat? Input: Y/N\n').upper()
    while repeat not in ('Y', 'N'):
        repeat = input('Do You want to repeat? Y/N\n ').upper()

    return True if repeat == 'Y' else False


def do_operation(func: int, row):
    operations = {1: Op.append_task,
                  2: Op.del_task,
                  3: Op.set_status,
                  4: Op.set_task_priority,
                  5: Op.add_desc,
                  6: Op.update_title,
                  7: Op.update_time,
                  8: Op.add_reminder,
                  9: Op.find_task}

    function = operations.get(func)

    if function(row) == 'Done':
        print('Operation has been executed')




if __name__ == '__main__':
    print('Welcome in to_do_app')

    is_first = None
    while is_first not in ('Y', 'N'):
        is_first = input('First time here? Input Y/N\n').upper()
    try:
        with Operation() as Op:
            if is_first == 'N':
                Op.sign_in()

            taskid = None
            while taskid is None:
                taskid = Op.logging()

            operation = operation_selector()

            while is_redo():
                operation = operation_selector()
                while operation is None:
                    operation = operation_selector()

            do_operation(operation, taskid)

    except EOFError:
        print('Nothing input')
    except ValueError:
        print('Value has wrong type')
    except TypeError:
        print('Cannot combine different datatypes')
    except OverflowError:
        print('Results too large')
    except RuntimeError as e:
        print('Error: ', e)
    except mysql.connector.InterfaceError as e:
        print("Interface error:", e)
    except mysql.connector.ProgrammingError as e:
        print("Programming error:", e)
    except mysql.connector.OperationalError as e:
        print("Operational error:", e)
    except mysql.connector.NotSupportedError as e:
        print("Not supported error:", e)
    except mysql.connector.InternalError as e:
        print("Internal error:", e)