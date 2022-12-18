from FDataBase import *
from flask_login import UserMixin  # уже в себе реализует is_authenticated, is_anonumoys, is_active


# Создаем пользователя в сессии
class UserLogin(UserMixin):
    def from_DB(self, user_id, db):
        self.__user = getUser(user_id, db)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['employee_number'])

    def getName(self):
        return self.__user['employee_name'] if self.__user else "Без имени (ты кто)"

    def getEmail(self):
        return self.__user['employee_email'] if self.__user else "Без почты (почему..)"

    def getPhone(self):
        return self.__user['employee_phone'] if self.__user else "Без телефона (треш)"

    def getRoleId(self):
        return self.__user['position_id'] if self.__user else "Нет должности (странно)"
