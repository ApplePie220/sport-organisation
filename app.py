from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
from FDataBase import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from dotenv import load_dotenv
import bcrypt
import psycopg2
import re
import os

# подулючение виртуального окружения для получения секретных данных
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY  # Секретный ключ для сессии


# Настройка лоигрования юзера и ограничения доступа к страницам
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message = "Пожалуйста, авторизуйтесь  для доступа к закрытым страницам"
login_manager.login_message_category = "success"
user_is_manager = False  # отображение вкладки с добавл. задания только для менеджера
user_id_admin = False # отображение вкладки с добавл. задания только для админа
salt = bcrypt.gensalt(6, prefix=b"2a")

# Подключение к бд
def connection_db(user_log, user_pass):
    try:
        # подключаемся к бд
        connection = psycopg2.connect(
            host='localhost',
            user=user_log,
            password=user_pass,
            database='sportorg'
        )
        # чтобы все изменения в бд автоматически применялись
        connection.autocommit = True
        print("PostgreSQL connected")
        return connection

    except Exception as _ex:
        print("ERROR while working with PostgreSQL", _ex)
        return False


# Подключение к бд через логин и пароль юзера
# Создание юзера в сессии
@login_manager.user_loader
def load_user(user_id):
    db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
    return UserLogin().from_DB(user_id, db)


# отображение страницы с ошибкой
@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title='Страница не найдена', manager=user_is_manager)


# авторизация пользователя
@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:  # если юзер уже авторизован, то при переходе на авторизацию
        return redirect(url_for('profile'))  # его будет перенаправлять в его профиль
    user = None
    if request.method == "POST":
        user_login = request.form.get('username')
        if user_login and len(request.form['psw'])>0:
            db = connection_db(user_log=DB_USER, user_pass=DB_PASSWORD)
            with db:
                with db.cursor(cursor_factory=DictCursor) as cursor:
                    query = sql.SQL("SELECT employee_password "
                                    "FROM employee WHERE employee_login = {logi}") \
                        .format(logi=sql.Literal(user_login))
                    cursor.execute(query)
                    res = cursor.fetchone()
                # сравниваем введенный пароль с паролем в бд
                res['employee_password'] = res['employee_password'].encode('utf-8')
                # если пароль верный, то создаем сессию этого пользователя
                if bcrypt.hashpw(request.form['psw'].encode('utf-8'), res['employee_password']) == res['employee_password']:
                    user = getUserByLogin(user_login, db)
                    userlogin = UserLogin().create(user)

                    # для запоминания пользователя в сессии
                    rm = True if request.form.get('remainme') else False
                    login_user(userlogin, remember=rm)
                    session['current_user'] = user
                    session['user_password'] = request.form.get('psw')
                    return redirect(url_for("profile"))
                else:
                    flash("Введен неверный пароль.", "error")

        else:
            flash('Неверный ввод логина/пароля', 'error')

    return render_template("login.html", title="Авторизация")


# регистрация пользователя
@app.route('/register', methods=["POST", "GET"])
def register():
    db = connection_db(DB_USER, DB_PASSWORD)
    position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
    user_id_admin = True if position_user['position_number'] == 3 else False
    if request.method == "POST":
        if len(request.form['firstname'])>0 and len(request.form['surname'])>0 and len(request.form['username'])>0\
                and len(request.form['phone'])>0 and len(request.form['email'])>0 and len(request.form['psw'])>0\
                and len(request.form['psw2'])>0 and len(request.form['expirience'])>0:
            with db:
                id_role = 0
                if request.form['role'] == 'trainer':
                    id_role = 2
                if request.form['role'] == 'manager':
                    id_role = 1
                with db.cursor() as cursor:
                    query = sql.SQL("CALL create_user({fn},{sn},{ln},{em},{ph},{lg},{psw},{exp},{role})") \
                        .format(fn=sql.Literal(request.form.get('firstname')), sn=sql.Literal(request.form.get('surname')),
                                ln=sql.Literal(request.form.get('lastname')),em=sql.Literal(request.form.get('email')),
                                ph=sql.Literal(request.form.get('phone')), lg=sql.Literal(request.form.get('username')),
                                psw=sql.Literal(request.form.get('psw')), exp=sql.Literal(request.form.get('expirience')),
                                role=sql.Literal(id_role), )
                    cursor.execute(query)
                    db.commit()
                    flash('Работник успешно зарегистрирован.', 'success')
                    return redirect(url_for('index'))

        else:
            flash('Неверно заполнены поля', 'error')

    return render_template('register.html', title="Регистрация работника.", admin = user_id_admin)


# отображение списка клиентов
@app.route('/clients', methods=["POST", "GET"])
@login_required
def clients():
    if 'current_user':
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
        if request.method == "POST":
            with db:
                client_id = request.form.get('id')
                check_correct_id = re.findall(r"[^0-9]", client_id)
                if check_correct_id:
                    flash("Введите корректный id.","error")
                else:
                    if not client_id:
                        flash("Введите id клиента для поиска.", "error")
                    else:
                        return redirect(url_for('showClient', id_client=client_id))
        clients_list = getClientAnounce(db)
    return render_template('clients_list.html', clients=clients_list, admin = user_id_admin,
                           manager=user_is_manager, title="Список клиентов")

@app.route('/groups')
@login_required
def groups():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        groups = getgroups(db)
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    return render_template('groups_list.html', groups=groups, admin=user_id_admin,
                           manager=user_is_manager, title="Список спортивных групп.")

@app.route('/equipments')
@login_required
def equipment():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        equips = getequips(db)
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    return render_template('equip_list.html', equips=equips, admin=user_id_admin,
                           manager=user_is_manager, title="Список оборудования.")



@app.route('/add-group', methods=["POST", "GET"])
@login_required
def addGroup():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    if request.method == "POST":
        with db:
            name = request.form.get('name')
            type = request.form.get('type')
            if not (name or type):
                flash("Заполните все поля", "error")
            else:
                res = addgroup(name,type, db)
                if not res:
                    flash('Ошибка добавления группы', category='error')
                else:
                    flash('Группа успешно добавлена', category='succes')
            return redirect(url_for('groups'))
    return render_template('add_group.html', admin=user_id_admin, title='Добавление группы.',
                           manager=user_is_manager)


# Отображение клиента, которого вводишь в поиске
@app.route('/client/<int:id_client>')
def showClient(id_client):
    client = None
    if 'current_user' in session:
        check_correst_id = re.findall(r"[^0-9]", str(id_client))
        if check_correst_id:
            flash("Введите корректный id.", "error")
        else:
            db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
            position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
            user_is_manager = True if position_user['position_number'] == 1 else False
            user_id_admin = True if position_user['position_number'] == 3 else False
            with db:
                client = findClientById(id_client, db)
                if not client:
                    flash("Клиент с таким id не найден или не существует.", "error")
                    return redirect(url_for('clients'))

    return render_template('client.html',admin=user_id_admin, client=client, title="Информация о клиенте")





# добавление задания
@app.route('/add-train', methods=["POST", "GET"])
@login_required
def addTrain():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    if request.method == "POST":
        with db:
            date = request.form.get('date')
            start = request.form.get('start')
            finish = request.form.get('finish')
            group = request.form.get('group')
            trainer = request.form.get('trainer')
            description = request.form.get('description')
            if not (date or start or finish or group or trainer or description):
                flash("Заполните все поля", "error")
            else:
                res = addtrain(date, start, finish, group, trainer, description, db)
                if not res:
                    flash('Ошибка добавления тренировки', category='error')
                else:
                    flash('Тренировка успешно добавлена', category='succes')
            return redirect(url_for('index'))
    return render_template('add_train.html', admin=user_id_admin, title='Добавление тренировки',
                           manager=user_is_manager)


@app.route('/add-client', methods=["POST", "GET"])
@login_required
def addClient():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
        groups = getgroups(db)
    if request.method == "POST":
        with db:
            firstname = request.form.get('firstname')
            surname = request.form.get('surname')
            lastname = request.form.get('lastname')
            phone = request.form.get('phone')
            mail = request.form.get('mail')
            address = request.form.get('address')
            date = request.form.get('date')
            group = int(request.form.get('group'))
            if not (firstname or surname or lastname or phone or mail or address or date or group):
                flash("Заполните все поля", "error")
            else:
                res = addclient(firstname, surname, lastname,phone, mail, address,date,group, db)
                if not res:
                    flash('Ошибка добавления клиента.', category='error')
                else:
                    flash('Клиент успешно добавлен.', category='succes')
            return redirect(url_for('clients'))
    return render_template('add_client.html',groups=groups, admin=user_id_admin, title='Добавление клиента.')

# отображение всех доступных заданий для пользователя
@app.route('/index')
@app.route('/')
@login_required
def index():
    if 'current_user' in session:
        db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
        trainings = getTrainingAnounce(db)
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    return render_template('index.html', trainings=trainings,admin = user_id_admin,
                           manager=user_is_manager, title="Список тренировок")


# отображение конкретного задания и его редактирование
@app.route('/task/<int:id_train>', methods=['GET', 'POST'])
@login_required
def showTrain(id_train):
        train = None
        if 'current_user' in session:
            db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
            position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
            user_is_manager = True if position_user['position_number'] == 1 else False
            user_id_admin = True if position_user['position_number'] == 3 else False
            if request.method == "POST":
                check_correst_id = re.findall(r"[^0-9]", str(id_train))
                if check_correst_id:
                    flash("Incorrect id.", "error")
                else:
                    with db:
                        start = request.form.get('start')
                        finish = request.form.get('finish')
                        date = request.form.get('date')
                        group = 'null' if request.form.get('group') == 'None' else \
                            request.form.get('group')
                        trainer = 'null' if request.form.get('trainer') == 'None' else \
                            request.form.get('trainer')
                        description = 'null' if request.form.get('description') == 'None' else \
                            request.form.get('description')
                        if not ( start or finish or date or group or trainer or description):
                            flash("Заполните все поля", "error")
                        else:
                            updateTrain(start,finish,date,group,trainer,description, db,
                                        id_train, user_is_manager, user_id_admin)
                            flash("Тренировка успешно изменена", "success")
                            return redirect(url_for('index'))
            else:
                with db:
                    train = getTrain(id_train, db)

        return render_template('train.html', admin=user_id_admin, training=train, manager=user_is_manager,
                               title="Редактор тренировки")


# выход из профиля
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


# профиль пользователя
@app.route('/profile')
@login_required
def profile():
    db = connection_db(session.get('current_user', SECRET_KEY)[6], session.get('user_password', SECRET_KEY))
    position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
    user_is_manager = True if position_user['position_number'] == 1 else False
    user_id_admin = True if position_user['position_number'] == 3 else False
    return render_template("profile.html", title="Профиль", manager=user_is_manager, admin = user_id_admin)

# генерация отчета по заданиям для конкретного работника в формате csv
@app.route('/train-report', methods=['POST', 'GET'])
def generate_train_report():
    if 'current_user' in session:
        db = connection_db(DB_USER, DB_PASSWORD)
        position_user = getPositionUser(session.get('current_user', SECRET_KEY)[0], db)
        user_is_manager = True if position_user['position_number'] == 1 else False
        user_id_admin = True if position_user['position_number'] == 3 else False
    if request.method == "POST":
        with db:
            start_date = request.form.get('start')
            finish_date = request.form.get('finish')
            path = request.form.get('path')
            if not (path or start_date or finish_date):
                flash("Заполните все поля!", "error")
            else:
                get_report_task(path, start_date, finish_date, db)
                flash("Отчет успешно сформирован по указанному пути.", "success")
                return redirect(url_for('index'))

    return render_template('worker_report.html',admin=user_id_admin, manager=user_is_manager,
                           title="Генерация отчета по тренировкам.")


if __name__ == '__main__':
    app.run()
