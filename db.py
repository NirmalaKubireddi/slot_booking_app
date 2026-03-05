import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nirmala@87905",
    database="slot_booking"
)

cursor = db.cursor(dictionary=True)