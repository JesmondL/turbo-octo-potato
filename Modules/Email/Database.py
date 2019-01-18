# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error

db_path = '/home/pi/turbo-octo-potato/Modules/lite.db'
def create_table():
    """ create a database connection to a sqlite database """
    try:
        # connect to a database
        conn = sqlite3.connect(db_path)
    except Error as e:
        print (e)
    finally:
        # create a cursor obj
        cur = conn.cursor()
        #write and SQL query
        cur.execute("CREATE TABLE store (item TEXT, quantity INTEGER, price REAL)")
        # commit changes
        conn.commit()
        # close datebase connection
        conn.close()

def insert_table(item, quantity, price):
    """ insert rows into table """
    try:
        # connect to a database
        conn = sqlite3.connect(db_path)
    except Error as e:
        print (e)
    finally:    
        # create a cursor obj
        cur = conn.cursor()
        #write and SQL query, use ? to prevent SQL injection
        cur.execute("INSERT INTO store VALUES (?,?,?)",(item, quantity, price))
        # commit changes
        conn.commit()
        # close datebase connection
        conn.close()

def view_table():
    """ view the whole table """
    try:
        # connect to a database
        conn = sqlite3.connect(db_path)
    except Error as e:
        print (e)
    finally:  
        cur = conn.cursor()
        cur.execute("SELECT * FROM store")
        rows = cur.fetchall()
        conn.close()
        return rows # list obj

create_table()
insert_table("Wine glass", 100, 12.50)
print(view_table())
