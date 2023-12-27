from flask import Flask, request, jsonify, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message":"Welcome To ODOG"})

@app.route('/create_goal', methods = ['POST'])
def goal():
    return jsonify({"Message": "Goal Created Successfully"})


if __name__ == "__main__":
    app.run(debug=True)