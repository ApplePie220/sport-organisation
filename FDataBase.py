import psycopg2
from psycopg2.extras import DictCursor


# получение всех доступных заданий из бд
def getTrainingAnounce(db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM training ORDER BY status")
            res = cursor.fetchall()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка в получении тренировок.")

    return []


# получение всех клиентов из бд
def getClientAnounce(db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:

            cursor.execute("SELECT * FROM client ORDER BY client_number")
            res = cursor.fetchall()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка в получении клиентов.")

    return []


# поиск клиента по его id
def findClientById(client_id, db):
    try:
        with db.cursor() as cursor:

            cursor.execute(f'SELECT * FROM client WHERE client_number={client_id}')
            res = cursor.fetchone()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка получения клиента по его id.")

    return False


# добавление нового задания в бд
def addtask(status, contract, author, executor, description, client, priority, db):
    try:
        with db.cursor() as cursor:
            cursor.execute("CALL add_task(%s,%s,%s,%s,%s,%s,%s)",
                           (description, status, contract, author, executor, client, priority))
            # db.commit()
    except Exception as e:
        print("Ошибкад добавления задачи " + e)
        return False

    return True


# получить задание по его id из бд
def getTrain(id, db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM training WHERE training_number =%(training_number)s",
                           {'training_number': id})
            res = cursor.fetchone()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка получения тренировки из БД.")
    return (False, False)


#  для менеджера и обычного сотрудника функции изменения задания разные.
def updateTrain(stat,start,finish,date,group,trainer,description, db, train_id, is_manager, is_admin):
    try:
        with db.cursor() as cursor:
            if is_manager or is_admin:
                cursor.execute(f'''UPDATE training SET start_time = '{start}',
                                finish_time = '{finish}',training_date = '{date}',
                                status = '{stat}',training_name = '{description}',
                                group_number = '{group}',trainer_number = '{trainer}'
                                 WHERE training_number = '{train_id}' ''')
            else:
                cursor.execute(f'''UPDATE training SET start_time = '{start}',
                                finish_time = '{finish}',training_date = '{date}',
                                status = '{stat}' WHERE training_number = '{train_id}' ''')

    except Exception as e:
        print(e)
        print("Ошибка редактирования тренировки.")


# добавление нового пользователя в бд
def addUser(name, login, password, phone, email, role, db):
    try:
        id_role = 0
        if role == 'worker':
            id_role = 2
        if role == 'manager':
            id_role = 1
        with db.cursor() as cursor:
            cursor.execute("CALL create_user(%s,%s,%s,%s,%s,%s)", (name, email, phone, login, password, id_role))
            db.commit()
    except Exception as e:
        print(e)
        print("Ошибка добавления пользователя в бд")
        return False

    return True


# получение пользователя из бд по его Id
def getUser(user_id, db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM employee WHERE employee_number = %(employee_number)s",
                           {'employee_number': user_id})
            res = cursor.fetchone()
            if not res:
                print("Пользовтель не найден.")
                return False
            return res
    except Exception as e:
        print(e)
        print("Ошибка получения данных из бд.")
    return False


# получение пользователя из бд по его логину
def getUserByLogin(login, db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            try:
                cursor.execute("SELECT * FROM employee WHERE employee_login = %(employee_login)s",
                               {'employee_login': login})
                res = cursor.fetchone()
            except psycopg2.OperationalError as e:
                print(e)
                res = False
            # if not res:
            # print("Пользователь не найден.")
            return res

    except Exception as e:
        print(e)
        print("Ошибка получения пользователя из бд.")

    return False


# получение пароля пользователя по его логину
def getPassUserByLogin(login, pasw, db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(f'''SELECT employee_password = crypt('{pasw}', employee_password) 
                                FROM employee WHERE employee_login = '{login}' ''')
            res = cursor.fetchone()[0]
            if not res:
                print("Пользователь не найден.")
                return False
            return res

    except Exception as e:
        print(e)
        print("Ошибка получения пользователя из бд.")

    return False


# получение номера позиции пользователя
def getPositionUser(user_id, db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT position_number FROM employee WHERE employee_number = %(employee_number)s",
                           {'employee_number': user_id})
            res = cursor.fetchone()
            if not res:
                print("Пользователя с таким id нет.")
                return False
            return res

    except Exception as e:
        print(e)
        print("Ошибка получения юзера из бд.")

    return False


# создание отчета по заданиям
def getReport(path, db):
    try:
        with db.cursor() as cursor:
            cursor.execute(f'''CALL export_report_json('{path}')''')

    except Exception as e:
        print(e)
        print("Ошибка вызова функции генерации отчета.")
        return False

    return True


# создание отчета по заданиям для конкретного пользователя
def get_report_task(path, start, finish, id, db):
    try:
        with db.cursor() as cursor:
            cursor.execute(f'''CALL export_data_employee_csv('{id}','{start}','{finish}','{path}')''')

    except Exception as e:
        print(e)
        print("Ошибка вызова функции генерации отчета по сотруднику.")
        return False

    return True
