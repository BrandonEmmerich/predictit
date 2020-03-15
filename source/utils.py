import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2
from psycopg2 import extras
import requests
import smtplib
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

def send_email(subject, body, recipient):
	'''Send email from a gmail account'''

	fromaddr = private.EMAIL_FROM_ADDRESS
	toaddr = recipient
	msg = MIMEMultipart('alternative', None, [MIMEText(body, 'html', 'utf-8')])
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = subject

	body = body

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, private.EMAIL_PASSWORD)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
