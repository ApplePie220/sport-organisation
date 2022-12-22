import random

from mimesis import Person, Address, Generic
from mimesis.locales import Locale
import psycopg2
import datetime as DT
import pandas as pd

def connect():
    try:
        # подключаемся к бд
        connection = psycopg2.connect(
            host='localhost',
            user='postgres',
            password='74NDF*305c',
            database='sportorg'
        )
        return connection
    except Exception as e:
        print(e)

person = Person(locale=Locale.RU)
de = Address(locale=Locale.RU)
generic = Generic(Locale.RU)
db = connect()
for i in range(1,300):
    with db.cursor() as cursor:
        firstname = person.first_name()
        lastname = person.last_name()
        surname = person.surname()
        phone = person.telephone(mask='8##########')
        email = person.email(domains=['example.com'])
        date = generic.datetime.date()
        address = "г. " + de.city() + ", " + de.address()
        group = random.randint(1,5)
        cursor.execute("CALL add_client_transaction(%s,%s,%s,%s,%s,%s,%s)",
                       (firstname, lastname,surname,phone,email, address, date, group))
        db.commit()

db.close()


