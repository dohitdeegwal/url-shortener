import os
import string
import random
import validators
from flask import Flask, redirect, render_template, request, url_for, flash, session
import pymysql
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)





db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name,cursorclass=pymysql.cursors.DictCursor)
                                
    except pymysql.MySQLError as e:
        print(e)

    return conn


@app.route("/", methods=["GET", "POST"])

def index():       

    if request.method == "POST":

        ourl = request.form.get("ourl")
        valid=validators.url(ourl)

        if valid == True:

            conn = open_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT surl FROM urls WHERE ourl = %s', ourl)
                n = cursor.fetchall()
            conn.close()

            if n:
                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('SELECT surl FROM urls WHERE ourl = %s', ourl)
                    urls = cursor.fetchall()
                conn.close()
                url = urls[0]['surl']
                return render_template("success.html", url=url)

            subs = ourl[-7:]
            conn = open_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT ourl FROM urls WHERE surl = %s', subs)
                m = cursor.fetchall()
            conn.close()

            if m:
                return  render_template("error.html", message="Already Short!")

            else:
                surl = res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7))

                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO  urls (ourl, surl) VALUES (%s, %s)', (ourl, surl))
                conn.commit()
                conn.close()


                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('SELECT surl FROM urls WHERE ourl = %s', ourl)
                    urls = cursor.fetchall()
                conn.close()
                url = urls[0]['surl']
                return render_template("success.html", url=url)

        else:
            return render_template("error.html", message="Invalid URL!")

    else:
        return render_template("index.html")



@app.route('/<surl>')
def redirection(surl):
    
    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT ourl FROM urls WHERE surl = %s', surl)
        urls = cursor.fetchall()
    conn.close()
    if urls:
        url=urls[0]['ourl']
        return redirect(url)


    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT ourl FROM curls WHERE curl = %s', surl)
        urls = cursor.fetchall()
    conn.close()
    if urls:
        url=urls[0]['ourl']
        return redirect(url)
            

    else:
        return render_template("error.html", message ="URL Does Not Exist!")

@app.route('/custom', methods=["GET", "POST"])
def custom():

    if session.get("user_id") is None:
        return redirect("/login")

    if request.method == "POST":

        ourl = request.form.get("ourl")
        curl = request.form.get("curl")
        valid=validators.url(ourl)

        if valid == True:

            conn = open_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT curl FROM curls WHERE ourl = %s', ourl)
                n = cursor.fetchall()
            conn.close()

            if n:
                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('SELECT curl FROM curls WHERE ourl = %s', ourl)
                    urls = cursor.fetchall()
                conn.close()
                url = urls[0]['curl']
                return render_template("success.html", url=url)

            conn = open_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT ourl FROM curls WHERE curl = %s', curl)
                z = cursor.fetchall()
            conn.close()

            if z:
                return render_template("error.html", message="Custom URL Not Available!")
            
            subs = ourl[20:]
            conn = open_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT ourl FROM curls WHERE curl = %s', subs)
                m = cursor.fetchall()
            conn.close()

            if m:
                return  render_template("error.html", message="Already Exists!")

            else:
                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO  curls (ourl, curl, user) VALUES (%s, %s, %s)', (ourl, curl, session["user"]))
                conn.commit()
                conn.close()


                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('SELECT curl FROM curls WHERE ourl = %s', ourl)
                    urls = cursor.fetchall()
                conn.close()
                url = urls[0]['curl']
                return render_template("success.html", url = url)

        else:
            return render_template("error.html", message="Invalid URL!")

    else:
        return render_template("custom.html")

    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")

        # Ensure username was submitted
        if not input_username:
            return render_template("error.html", message ="Enter Valid Username")

        # Ensure password was submitted
        elif not input_password:
            return render_template("error.html", message ="Enter Valid Password")

        # Query database for username
        conn = open_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', input_username)
            username = cursor.fetchall()
        conn.close()


        # Ensure username exists and password is correct
        if len(username) != 1 or not check_password_hash(username[0]["hash"], input_password):
            return render_template("error.html", message ="Invalid Username Or Password!")

        # Remember which user has logged in
        session["user_id"] = username[0]["id"]
        session["user"] =  username[0]["username"]

        # Flash info for the user
        flash(f"Logged in as {input_username}")

        # Redirect user to home page
        return redirect("/custom")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign inputs to variables
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        input_confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not input_username:
            return render_template("error.html", message ="Enter A Username")

        # Ensure password was submitted
        elif not input_password:
            return render_template("error.html", message ="Enter Password")

        # Ensure passwsord confirmation was submitted
        elif not input_confirmation:
            return render_template("error.html", message ="Re-enter Password")
        elif not input_password == input_confirmation:
            return render_template("error.html", message ="Passwords Do Not Match")

        # Query database for username
        conn = open_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', input_username)
            username = cursor.fetchall()
        conn.close()

        # Ensure username is not already taken
        if len(username) == 1:
            return render_template("error.html", message ="Url doesnt exist")

        # Query database to insert new user
        else:
            conn = open_connection()
            with conn.cursor() as cursor:
                new_user = cursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (input_username, generate_password_hash(input_password, method="pbkdf2:sha256", salt_length=8)))
                           
            conn.commit()
            conn.close()                

            if new_user:
                # Keep newly registered user logged in
                session["user_id"] = new_user
                session["user"] = username

            # Flash info for the user
            flash(f"Registered as {input_username}")

            # Redirect user to homepage
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
def password():   
    session.clear()

    if request.method == "POST":

        input_username = request.form.get("username")
        input_password = request.form.get("password")
        new_password = request.form.get("new_password")
        con_password = request.form.get("con_password")

        if not input_username:
            return render_template("error.html", message ="Enter A Username")

        elif not input_password:
            return render_template("error.html", message ="Enter Password")

        conn = open_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', input_username)
            username = cursor.fetchall()
        conn.close()

        if(new_password != con_password):
            return render_template("register.html", message="New Passwords Do Not Match")

        if len(username) == 1:
            if check_password_hash(username[0]["hash"], input_password):
                conn = open_connection()
                with conn.cursor() as cursor:
                    cursor.execute('UPDATE users SET hash = %s WHERE username = %s',(generate_password_hash(new_password, method="pbkdf2:sha256", salt_length=8) ,input_username))
                conn.commit()
                conn.close()    
                return redirect("/custom")
            else:
                return render_template("error.html", message ="Invalid Password!")   
        else:
            return render_template("error.html", message ="Invalid Username!")        
    else:
        return render_template("change.html")
