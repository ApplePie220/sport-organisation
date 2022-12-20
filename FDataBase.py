import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import sql


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

            cursor.execute("SELECT * FROM client WHERE client_number=%(client_number)s",
                           {'client_number': client_id})
            res = cursor.fetchone()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка получения клиента по его id.")

    return False


# добавление новой тренировки в бд
def addclient(firstname, surname, lastname, phone, mail, address, date, group, db):
    try:
        with db.cursor() as cursor:
            query1 = sql.SQL("CALL add_client_transaction({fn},{sn},{ln},{ph},{em},{adr},{dt},{grr})") \
                .format(fn=sql.Literal(firstname), sn=sql.Literal(surname), ln=sql.Literal(lastname),
                        ph=sql.Literal(phone), em=sql.Literal(mail), adr=sql.Literal(address),
                        dt=sql.Literal(date), grr=sql.Literal(group))
            cursor.execute(query1)
            db.commit()
    except Exception as e:
        print("Ошибкад добавления клиента." + e)
        return False

    return True


# добавление новой тренировки в бд
def addtrain(date, start, finish, group, trainer, description, db):
    try:
        with db.cursor() as cursor:
            query1 = sql.SQL("CALL add_training({dat},{strt},{fnsh},{descr},{gr},{tr})") \
                .format(dat=sql.Literal(date), strt=sql.Literal(start),fnsh=sql.Literal(finish),
                        descr=sql.Literal(description), gr=sql.Literal(group),
                        tr=sql.Literal(trainer))
            cursor.execute(query1)
            db.commit()
    except Exception as e:
        print("Ошибкад добавления тренировки " + e)
        return False

    return True


# получить задание по его id из бд
def getTrain(id, db):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM training WHERE training_number = %(training_number)s",
                           {'training_number': id})
            res = cursor.fetchone()
            if res:
                return res
    except Exception as e:
        print(e)
        print("Ошибка получения тренировки из БД.")
    return (False, False)


#  для менеджера и обычного сотрудника функции изменения задания разные.
def updateTrain(start, finish, date, group, trainer, description, db, train_id, is_manager, is_admin):
    try:
        with db.cursor() as cursor:
            if is_manager or is_admin:
                query = sql.SQL("UPDATE training SET start_time = {startd},finish_time = {finishd},"
                                "training_date = {dated},training_name = {descriptions},"
                                "group_number = {groupn},trainer_number = {trainern} "
                                "WHERE training_number = {train_num}") \
                    .format(startd=sql.Literal(start), finishd=sql.Literal(finish),
                            dated=sql.Literal(date),descriptions=sql.Literal(description),
                            groupn=sql.Literal(group),trainern=sql.Literal(trainer),
                            train_num=sql.Literal(train_id))

                cursor.execute(query)
            else:
                query1 = sql.SQL("UPDATE training SET start_time = {startd},finish_time = {finishd},"
                                "training_date = {dated},"
                                "WHERE training_number = {train_num}") \
                    .format(startd=sql.Literal(start), finishd=sql.Literal(finish),
                            dated=sql.Literal(date),train_num=sql.Literal(train_id))
                cursor.execute(query1)
        db.commit()
    except Exception as e:
        print(e)
        print("Ошибка редактирования тренировки.")


def getgroups(db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM vieww")
            res = cursor.fetchall()
            if not res:
                print("Группы не найдены.")
                return False
            return res
    except Exception as e:
        print(e)
        print("Ошибка получения спорт. групп из бд.")
    return False


def addgroup(name, type, db):
    try:
        with db.cursor() as cursor:
            query = sql.SQL("CALL add_group({nam},{typ})") \
                .format(nam=sql.Literal(name), typ=sql.Literal(type))
            cursor.execute(query)
            db.commit()
    except Exception as e:
        print("Ошибка добавления группы" + e)
        return False

    return True


# добавление нового пользователя в бд
def addUser(firstname, surname, lastname, email, phone, login, password, expirience, role, db):
    try:
        id_role = 0
        if role == 'trainer':
            id_role = 2
        if role == 'manager':
            id_role = 1
        with db.cursor() as cursor:
            query = sql.SQL("CALL create_user({fn},{sn},{ln},{em},{ph},{lg},{psw},{exp},{role})") \
                .format(fn=sql.Literal(firstname),sn=sql.Literal(surname),ln=sql.Literal(lastname),
                        em=sql.Literal(email),ph=sql.Literal(phone),lg=sql.Literal(login),
                        psw=sql.Literal(password),exp=sql.Literal(expirience),role=sql.Literal(id_role),)
            cursor.execute(query)
            db.commit()
    except Exception as e:
        print(e)
        print("Ошибка добавления пользователя в бд")
        return False

    return True


def getequips(db):
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM sport_equip_training")
            res = cursor.fetchall()
            if not res:
                print("Группы не найдены.")
                return False
            return res
    except Exception as e:
        print(e)
        print("Ошибка получения спорт. групп из бд.")
    return False


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
            query = sql.SQL("SELECT employee_password = crypt({passws}, employee_password) "
                            "FROM employee WHERE employee_login = {logi}") \
                .format(passws=sql.Literal(pasw),
                        logi=sql.Literal(login))

            cursor.execute(query)
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


# создание отчета по тренировкам
def get_report_task(path, start, finish, db):
    try:
        with db.cursor() as cursor:
            query = sql.SQL("CALL export_data_training_csv({startd},{finishd},{paths})") \
                .format(startd=sql.Literal(start),
                        finishd=sql.Literal(finish),
                        paths=sql.Literal(path))
            cursor.execute(query)

    except Exception as e:
        print(e)
        print("Ошибка вызова функции генерации отчета по сотруднику.")
        return False

    return True
