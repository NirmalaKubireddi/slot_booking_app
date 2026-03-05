from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nirmala@87905",
    database="slot_booking"
)

cursor = conn.cursor()

# ----------------------
# ADMIN PAGE
# ----------------------

@app.route('/admin')
def admin():

    if 'user' not in session:
        return redirect('/')

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

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

    query = "DELETE FROM bookings WHERE id=%s"
    cursor.execute(query, (id,))
    conn.commit()

    return redirect('/admin')

# ----------------------
# LOGIN PAGE
# ----------------------

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        query = "SELECT * FROM users WHERE email=%s AND password=%s"
        cursor.execute(query,(email,password))
        user = cursor.fetchone()

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

        query = "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)"
        cursor.execute(query,(name,email,password))
        conn.commit()

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

    cursor.execute("SELECT COUNT(*) FROM bookings")
    booked_slots = cursor.fetchone()[0]

    available_slots = max_slots - booked_slots

    return render_template(
        "index.html",
        available_slots=available_slots
    )

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

    query = "INSERT INTO bookings (name,email,slot_date,slot_time) VALUES (%s,%s,%s,%s)"
    cursor.execute(query,(name,email,date,time))
    conn.commit()

    return redirect('/booked')

# ----------------------
# BOOKED SLOTS
# ----------------------

@app.route('/booked')
def booked():

    if 'user' not in session:
        return redirect('/')

    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()

    return render_template("booked.html", bookings=data)

# ----------------------
# LOGOUT
# ----------------------

@app.route('/logout')
def logout():

    session.pop('user',None)
    return redirect('/')

# ----------------------

if __name__ == "__main__":
    app.run(debug=True)