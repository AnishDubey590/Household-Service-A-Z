from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI']="sqlite://A-Z_household_services.db"
app.config['SQLALCHEMY_TRACK_MODIDFICATIONS']=False
db = SQLAlchemy()
class Customer(db.Model):
    customer_id=db.Column(db.String(50) ,primary_key=True)
    password=db.Column(db.String(50), nullable=False)
    full_name=db.Column(db.String(50),nullable=False)
    address=db.Column(db.String(200),nullable=False)
    pin=db.Column(db.Integer(),nullable=False)
    


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sign_user")
def signup_user():
    return render_template("customer_Signup.html")

@app.route("/sign_professional")
def signup_professor():
    return render_template("Professional_Signup.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
