from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed to use sessions

def init_sqlite_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT, password TEXT)')
    print("Table created successfully")
    conn.close()

init_sqlite_db()

@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user:
                # If the username exists, check the password
                if check_password_hash(user[3], password):
                    session['username'] = user[1]
                    return redirect(url_for('dashboard'))
                else:
                    # Password is incorrect
                    flash("Incorrect password. Please try again.", "error")
            else:
                # Username does not exist
                flash("Username does not exist. Please sign up.", "error")
                
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])

            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
                conn.commit()
                flash("User successfully registered!")
                return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash("Error occurred: " + str(e))
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/guest/')
def guest_login():
    session['username'] = 'Guest'
    return redirect(url_for('dashboard'))

@app.route('/dashboard/')
def dashboard():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for('login'))

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
