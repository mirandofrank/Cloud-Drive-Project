from flask import Flask, render_template, redirect, request, session, flash
import pymysql
from wtforms import Form, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from config import *
import gc
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = 'hjkdjeuqoe157!@'

#Connecting to MySQL instance RDS
try:
    db = pymysql.connect(
        host = customhost,
        port = 3306,
        user = customuser,
        password = custompass,
        db = customdb
    )
except Exception as e:
    print(str(e))


class RegistrationForm(Form):
    fname    = TextField('First name', [validators.Length(min=1, max=30)])
    lname    = TextField('Last name', [validators.Length(min=1, max=30)])
    email    = TextField('Email address', [validators.Length(min=6, max=50)])
    username = TextField('Username', [validators.Length(min=4, max=100)])
    password = PasswordField('Password', [validators.Required(),
                                          validators.EqualTo('confirm', message="Password must match")])
    confirm  = PasswordField('Repeat Password')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            first_name  = form.fname.data
            last_name   = form.lname.data
            email       = form.email.data
            usr_name    = form.username.data
            passwd      = sha256_crypt.encrypt((str(form.password.data)))

            #Checking for duplicate username
            cursor = db.cursor()
            x = cursor.execute("SELECT * FROM User_info WHERE username=(%s)", (usr_name))
            cursor.close()
            if int(x) > 0:
                flash("That username is already taken. Please choose another")
                return render_template('register.html', form=form)
            else:
                cursor = db.cursor()
                cursor.execute("INSERT INTO User_info (username, password, email, fname, lname) VALUES (%s, %s, %s, %s, %s)",
                                (usr_name, passwd, email, first_name, last_name))
                db.commit()
                cursor.close()
                gc.collect()
                # session['logged_in'] = True
                # session['username'] = usr_name
                # return redirect('/')
                flash("You have successfully registered your account")
                return redirect('/login')
        return render_template('register.html', form=form)
    except Exception as e:
        return(str(e))

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect('/login')
    return wrap

@app.route('/logout')
@login_required
def logout():
    session.clear()
    gc.collect()
    flash("You have been logged out")
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error = ''
    try:
        if request.method == 'POST':
            cursor = db.cursor()
            username = request.form['username']
            data = cursor.execute("SELECT * FROM User_info WHERE username = (%s)", (username))
            data = cursor.fetchone()
            cursor.close()

            if sha256_crypt.verify(request.form['password'], data[2]):
                app.logger.info('Yes6')
                session['logged_in'] = True
                session['username'] = username
                session['fname'] = data[4]
                flash("You are now logged in")
                return redirect('/dashboard')
            else:
                app.logger.info('No')
                error = "Invalid credentials. Please try again."
        gc.collect()
        return render_template('login.html', error=error)
    except Exception as e:
        error = str(e)
        return render_template('login.html', error=error)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if "username" and "fname" in session:
        username = session['username']
        fname = session['fname']
        return render_template('/dashboard.html', username=username, name=fname)
    else:
        return render_template('/login')

@app.route('/dashboard/change_password/<string:username>', methods = ['GET', 'POST'])
@login_required
def change_password(username):
    error = ''
    try:
        if request.method == 'POST':
            #Getting the password for comparison
            cursor = db.cursor()
            data   = cursor.execute("SELECT * FROM User_info WHERE username = (%s)", (username))
            data   = cursor.fetchone()
            cursor.close()

            if sha256_crypt.verify(request.form['password'], data[2]):
                cursor = db.cursor()
                password = sha256_crypt.encrypt((str(request.form['new_password'])))
                data = cursor.execute("UPDATE User_info SET password = (%s) WHERE username = (%s)", (password, username))
                db.commit()
                cursor.close()
                flash("You have successfully changed your password")
                return redirect('/dashboard')
            else:
                error = "Invalid credentials. Please try again"
        gc.collect()
        return render_template('change_password.html', error=error, username=username)
    except Exception as e:
        error = str(e)
        return render_template('change_password.html', error=error, username=username)



if __name__ == "__main__":
    app.run(debug=True)
