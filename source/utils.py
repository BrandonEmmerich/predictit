import datetime
import psycopg2
from psycopg2 import extras
import requests
import time
import uuid

import private

def generate_run_id():
    return int(time.time())

def generate_uuid():
    return str(uuid.uuid4())

def bundled_data(date_added, run_id):
    row = {
        'date_added': date_added,
        'run_id': run_id,
    }
    return row

def right_now():
    return datetime.datetime.now()

def write_to_database(row, insert_query):
    with psycopg2.connect(private.AWS_CONNECTION_STRING) as conn:
        try:
            cur = conn.cursor()
            cur.execute(insert_query, row)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)

def get_list_from_db(query):
    with psycopg2.connect(private.AWS_CONNECTION_STRING) as conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            tuples = cur.fetchall()

        except Exception as e:
            conn.rollback()
            print(e)

    return [tuple[0] for tuple in tuples]

def get_object_from_db(query):
    with psycopg2.connect(private.AWS_CONNECTION_STRING) as conn:
        try:
            cur = conn.cursor()
            cur.execute(query)
            object = cur.fetchone()[0]

        except Exception as e:
            conn.rollback()
            print(e)

    return object

def get_authorization_token():
    data = {
        'email': private.PREDICTIT_EMAIL,
        'password': private.PREDICTIT_PASSWORD,
        'grant_type': 'password',
        'rememberMe': 'true'
    }
    response = requests.post('https://www.predictit.org/api/Account/token', data=data)
    access_token = response.json()['access_token']
    return access_token
