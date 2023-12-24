from flask import Flask, request, jsonify, render_template
from datetime import date
from passlib.hash import bcrypt

import mysql.connector

app = Flask(__name__)

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

@app.route('/')
@app.route('/create_goal', methods = ['POST'])
def create():
    data = request.json
    if "goal" not in data or "description" not in data:
        return jsonify({"message":"Please fill all the details"}), 400
    today_date = date.today()
    
    query = "select * from Goals where Date = %s"
    values = (today_date,)
    mycursor.execute(query, values)
    result = mycursor.fetchone()

    if result is not None:
        return jsonify({"message":"Goal Available For This Date"}), 400

    goal = data['goal']
    description = data['description']
    

    query = "insert into Goals (Date, Goal, Description) Values (%s, %s, %s)"
    values = (today_date, goal, description)
    mycursor.execute(query, values)

    mydb.commit()

    return jsonify({"Message": "Goal Created Successfully"})

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        hashed_password = bcrypt.hash(password)

        query = "select * from users where email = %s"
        values = (email,)
        mycursor.execute(query, values)
        result = mycursor.fetchone()
        if result:
            return jsonify({"message":"Email Already Exist"}), 400

        query = "insert into users (email, name, password) Values (%s, %s, %s)"
        values = (email, name, hashed_password)
        mycursor.execute(query, values)
        mydb.commit()
        return jsonify({"message":"User registered Successfully"}), 200

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        pass
        
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