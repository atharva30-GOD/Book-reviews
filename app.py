import os
import sys
from flask import Flask, session, render_template, request, flash, redirect, url_for, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
##ha=MgagfeBj79vIX8CMJCkA
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/loginpage")
def show_login():

    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    session.clear()
    user_name = request.form.get("username")
    pass_word= request.form.get("password")
    confirm = request.form.get("confirm")

    #if not user_name:
    A = user_name.strip()
    B = pass_word.strip()
    C = confirm.strip()
     #   flash(u'Provide a username','error')
    #if not pass_word :
     #   flash(u'Provide a password','error')
    #if not confirm:
     #   flash(u'Provide a confirmation passwor','error')    
    if B != C :
        return render_template("error2.html",message="Passwords dont match")

    userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                        {"username":A}).fetchone()

    # Check if username already exist
    if userCheck: 
        return render_template("error2.html", message="Username already exist")

    hashedPassword = generate_password_hash(B, method='pbkdf2:sha256', salt_length=8)

    db.execute("INSERT INTO users(username,pass)  VALUES (:username, :password)",
                            {"username":A, 
                             "password":hashedPassword})
    db.commit()
    ##flash('Account created', 'info')
    return render_template("login.html")


        
@app.route("/login",methods=["POST"])
def login():
    session.clear()
    if request.method == "POST" :
        name = request.form.get("username")
        pass_word = request.form.get("password")

        res = db.execute("SELECT * FROM users where username=:username",
                                {"username":name}).fetchone()

        if not check_password_hash(res[2],pass_word):
            message="Wrong Username/Password Bruh!"
            return render_template("error2.html",message=message)
        
        session["id"] = int(res[0])
        session["name"] = str(res[1])
    
        return render_template("search.html",name=session["name"])
    else :
        return render_template("login.html")

@app.route("/search",methods=["GET"])
def search():
    ##books={} 
    if request.args.get("search") is None :
        return render_template("error.html",message = "Enter Something to search!!")
    res1 = "%"+ request.args.get("search") +"%"

    rows = db.execute("SELECT * FROM books WHERE isbn LIKE :res1 OR \
                                author LIKE :res1 OR \
                                title LIKE :res1 OR \
                                yr LIKE :res1",
                                {"res1":res1})
                    
    if rows.rowcount == 0:
        return render_template("error.html", message=request.args.get("search"))

    #print(rows, file=sys.stderr)
    res2 = rows.fetchall()
    #print(res2, file=sys.stderr)
    return render_template("results.html",books=res2,msg=request.args.get("search")) 
    ##books=[]

@app.route("/searchpage")
def show_search():
    
    return render_template("search.html",name=session["name"])

@app.route("/book/<string:isbn>")
def book(isbn):

    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn})
    res = rows.fetchone()

    return render_template ("book.html",books=res)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")

@app.route("/reviews/<string:isbn>")
def reviews(isbn):
    rate = int(request.args.get("rating"))
    view = str(request.args.get("review"))
    

    uid = session["id"]
    #check if already reviewed 
    row = db.execute("SELECT id FROM reviews WHERE u_id = :uid AND book_id = :isbn",
                                    {"uid":uid,
                                    "isbn":isbn
                                    }) 
    
    #if row.rowcount == 1:
     #   return render_template("")
    db.execute("INSERT INTO reviews(u_id, book_id, rating, review) VALUES(:u_id,:book_id,:rate,:review)",
                                {"u_id":uid,
                                "book_id":isbn,
                                "rate":rate,
                                "review":view
                                })
    
    db.commit()
    ##A = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":isbn})

    ##ratings = A.fetchall()
    B = db.execute("SELECT users.username, rating, review FROM users INNER JOIN reviews ON users.id = reviews.u_id AND book_id = :isbn",{"isbn":isbn})

    names = B.fetchall()

    C = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn})

    res = C.fetchall() 
    ##GOODREADS API

    key = os.getenv("GOODREADS_KEY")

    req = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})
   
    response = req.json()
    avg_rating = response['books'][0]['average_rating']
    return render_template("rating.html",names=names, books=res, avg_rating=avg_rating)

@app.route("/seereviews/<string:isbn>")
def seereviews(isbn):

    uid = session["id"]

    C = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn})

    res = C.fetchall() 
   
    B = db.execute("SELECT users.username, rating, review FROM users INNER JOIN reviews ON users.id = reviews.u_id AND book_id = :isbn",{"isbn":isbn})

    names=[]
    if B.rowcount >=1 :
        names = B.fetchall()

    #GOODREADS API
    key = os.getenv("GOODREADS_KEY")

    req = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})
   
    response = req.json()
    avg_rating = response['books'][0]['average_rating']
    if len(names)==0:
        return render_template("rating2.html", books=res, avg_rating=avg_rating)
    else:
        return render_template("rating.html",names=names, books=res, avg_rating=avg_rating)     
   