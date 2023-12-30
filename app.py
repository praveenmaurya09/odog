from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime
import re
# from passlib.hash import bcrypt
from flask_bcrypt import Bcrypt

import mysql.connector

app = Flask(__name__)
app.secret_key = 'your secret key'

flask_bcrypt = Bcrypt(app)
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "09041997",
    database = "odog"
)

mycursor = mydb.cursor()

@app.route('/')
def first():
    return render_template('index.html')

@app.route

@app.route('/create_goal', methods = ['POST'])
def create():
    data = request.json
    if "goal" not in data or "description" not in data:
        return jsonify({"message":"Please fill all the details"}), 400
    current_datetime = datetime.now()
    
    query = "select * from Goals where DATE(Date) = %s"
    values = (current_datetime.date(),)
    mycursor.execute(query, values)
    result = mycursor.fetchone()

    if result is not None:
        return jsonify({"message":"Goal Available For This Date"}), 400 

    goal = data['goal']
    description = data['description']
    

    query = "insert into Goals (Date, Goal, Description) Values (%s, %s, %s)"
    values = (current_datetime, goal, description)
    mycursor.execute(query, values)

    mydb.commit()

    return jsonify({"Message": "Goal Created Successfully"})

from datetime import datetime, timedelta

@app.route('/delete_expired_tasks', methods=['GET'])
def delete_expired_tasks():
    # import pdb
    # pdb.set_trace()
    query = "SELECT Date FROM goals"
    mycursor.execute(query)
    date = mycursor.fetchone()

    if date:
        stored_date = date[0] 
        current_datetime = datetime.now()

        time_difference = current_datetime - stored_date

        # Check if the difference is more than 24 hours
        if time_difference > timedelta(hours=24):
            delete_query = "DELETE FROM goals"
            mycursor.execute(delete_query)
            mydb.commit()
            return jsonify({"message": "Expired task deleted successfully"})
        else:
            return jsonify({"message": "Task is not yet expired"})

    return jsonify({"message": "No date found"})

    # query = "select date from goals"
    # mycursor.execute(query)
    # date = mycursor.fetchone()
    # current_datetime = datetime.now()
    # if date:
    #     if date <= current_datetime:
    #         query = "delete from goals"
    #         mycursor.execute(query)
    #     return jsonify({"message":"Task Deleted Succeesfully"})


     
        
    # threshold = datetime.now() - timedelta(hours=24)
    
    # query = "DELETE FROM Goals WHERE Date < %s"
    # values = (threshold.date(),)
    # mycursor.execute(query, values)
    # mydb.commit()



    return jsonify({"Message": "Expired tasks deleted successfully"})

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # hashed_password = bcrypt.hash(password)
        # hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')

        query = "select * from accounts where username = %s"
        values = (username,)
        mycursor.execute(query, values)
        account = mycursor.fetchone()
        if account:
            return jsonify({"message":"Account Already Exist"}), 400
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            return jsonify({'message':msg})
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
            return jsonify({'message':msg})
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
            return jsonify({'message':msg})

        query = "insert into accounts (email, username, password) Values (%s, %s, %s)"
        values = (email, username, password)
        mycursor.execute(query, values)
        mydb.commit()
        return jsonify({"message":"User registered Successfully"}), 200

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        query = "select * from accounts where username = %s and password = %s"
        values = (username, password)
        mycursor.execute(query, values)
        account = mycursor.fetchone()

        if account is None:
            return jsonify({"Message": "User Doesn't Exist"})

        session['loggedin'] = True
        session['id'] = account[0]
        session['username'] = account[1]
        return redirect(url_for('home'))

        # user = {'emailOrPhone':result[0], 'name':result[1], 'password':result[2]}

        # hashed_password_from_db = user['password']

        # # if bcrypt.checkpw(password, hashed_password_from_db):
        # if flask_bcrypt.check_password_hash(hashed_password_from_db, password):
        #     return jsonify({"message":"Login Successful"})
        # else:
        #     return jsonify({"message":"Invalid Password"})


    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return redirect(url_for('login'))


@app.route('/get_goal/<string:date>', methods = ["GET"])
def get_goal(date):
    query = "select * from Goals where Date = %s"
    values = (date,)
    mycursor.execute(query, values)
    result = mycursor.fetchone()

    if not result:
        return jsonify({"message":"Goal Not Available For The Entered Date"}), 200

    goal, description = result[1:3] 
    return jsonify({'Date':date, 'Goal':goal, "Description":description}), 200


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return jsonify({'message':"Welcome Home"})
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)

# CREATE TABLE IF NOT EXISTS `accounts` (
# 	`id` int(11) NOT NULL AUTO_INCREMENT,
#   	`username` varchar(50) NOT NULL,
#   	`password` varchar(255) NOT NULL,
#   	`email` varchar(100) NOT NULL,
#     PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;