from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "secret123"

# ----------------------
# DATABASE CONNECTION
# ----------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME")
        )
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to database:", e)
        return None

# ----------------------
# ADMIN PAGE
# ----------------------
@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_bookings=total_bookings,
        bookings=bookings
    )

# ----------------------
# DELETE BOOKING
# ----------------------
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/admin')

# ----------------------
# LOGIN PAGE
# ----------------------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email,password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['user'] = user[0]
            return redirect('/index')
        else:
            return "Invalid Login"

    return render_template("login.html")

# ----------------------
# SIGNUP PAGE
# ----------------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            return "Database connection failed"

        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/')

    return render_template("signup.html")

# ----------------------
# BOOKING PAGE
# ----------------------
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect('/')

    max_slots = 10
    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings")
    booked_slots = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    available_slots = max_slots - booked_slots
    return render_template("index.html", available_slots=available_slots)

# ----------------------
# BOOK SLOT
# ----------------------
@app.route('/book', methods=['POST'])
def book():
    if 'user' not in session:
        return redirect('/')

    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    time = request.form['time']

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (name,email,slot_date,slot_time) VALUES (%s,%s,%s,%s)", (name,email,date,time))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/booked')

# ----------------------
# BOOKED SLOTS
# ----------------------
@app.route('/booked')
def booked():
    if 'user' not in session:
        return redirect('/')

    conn = get_db_connection()
    if not conn:
        return "Database connection failed"

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("booked.html", bookings=data)

# ----------------------
# LOGOUT
# ----------------------
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)