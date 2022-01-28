import sqlite3
from config import *


def check_user_presence(chat_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE vk_id = '{chat_id}';")
    res = cur.fetchall()
    return len(res) == 1


def create_user(chat_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO users(vk_id) VALUES('{chat_id}');""")
    conn.commit()
    return True

def get_status(chat_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT status FROM users WHERE vk_id = '{chat_id}';")
    res = cur.fetchall()
    return res[0][0]

def get_data(chat_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT data FROM users WHERE vk_id = '{chat_id}';")
    res = cur.fetchall()
    return res[0][0]

def set_status(chat_id, status):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"""UPDATE users SET status = '{status}' WHERE vk_id = '{chat_id}' """)
    conn.commit()
    return True

def set_data(chat_id, data):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"""UPDATE users SET data = '{data}' WHERE vk_id = '{chat_id}' """)
    conn.commit()
    return True

def get_all_cities():
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM cities;")
    res = cur.fetchall()
    return res

def get_flights(departure_city_id, destination_city_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM flights WHERE departure_city_id = '{departure_city_id}' AND destination_city_id = '{destination_city_id}';")
    res = cur.fetchall()
    return res

def get_city_name(city_id):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT name FROM cities WHERE id = '{city_id}';")
    res = cur.fetchall()
    return res[0][0]

def get_flight(flight_number):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM flights WHERE flight = '{flight_number}';")
    res = cur.fetchall()
    return res[0]

def get_last_flight():
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM flights;")
    res = cur.fetchall()
    return res[-1]

def check_flight_presence(flight):
    conn = sqlite3.connect(BD_FILE_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM flights WHERE flight = '{flight}';")
    res = cur.fetchall()
    return len(res) == 1