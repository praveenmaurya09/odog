from flask import Flask, request, jsonify, render_template
from datetime import datetime
# from passlib.hash import bcrypt
from flask_bcrypt import Bcrypt

import mysql.connector

app = Flask(__name__)

flask_bcrypt = Bcrypt(app)
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "09041997",
    database = "odog"
)

mycursor = mydb.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_goal', methods = ['POST'])
def create():
    data = request.json
    if "goal" not in data or "description" not in data:
        return jsonify({"message":"Please fill all the details"}), 400
    current_datetime = datetime.now()
    
    query = "select * from Goals where Date = %s"
    values = (current_datetime,)
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

@app.route('/delete_expired_tasks', methods=['GET'])
def delete_expired_tasks():
    # Calculate the time threshold (24 hours ago)
    threshold = datetime.now() - timedelta(hours=24)
    
    query = "DELETE FROM Goals WHERE Date < %s"
    values = (threshold.date(),)
    mycursor.execute(query, values)
    mydb.commit()

    return jsonify({"Message": "Expired tasks deleted successfully"})

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        # hashed_password = bcrypt.hash(password)
        hashed_password = flask_bcrypt.generate_password_hash(password).decode('utf-8')

        query = "select * from users where email = %s"
        values = (emailOrPhone,)
        mycursor.execute(query, values)
        result = mycursor.fetchone()
        if result:
            return jsonify({"message":"emailOrPhone Already Exist"}), 400

        query = "insert into users (email, name, password) Values (%s, %s, %s)"
        values = (emailOrPhone, name, hashed_password)
        mycursor.execute(query, values)
        mydb.commit()
        return jsonify({"message":"User registered Successfully"}), 200

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        emailOrPhone = request.form['emailOrPhone']
        password = request.form['password']
        query = "select * from users where email = %s"
        values = (emailOrPhone,)
        mycursor.execute(query, values)
        result = mycursor.fetchone()

        if result is None:
            return jsonify({"Message": "User Doesn't Exist"})

        user = {'emailOrPhone':result[0], 'name':result[1], 'password':result[2]}

        hashed_password_from_db = user['password']

        # if bcrypt.checkpw(password, hashed_password_from_db):
        if flask_bcrypt.check_password_hash(hashed_password_from_db, password):
            return jsonify({"message":"Login Successful"})
        else:
            return jsonify({"message":"Invalid Password"})


    return render_template('login.html')

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


if __name__ == "__main__":
    app.run(debug=True)