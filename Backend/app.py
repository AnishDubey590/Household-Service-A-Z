#Importing necessary libraries in app.py to create database and templates
from flask import Flask, render_template,request # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from datetime import datetime
import sys

sys.path.insert(4,'E:\clone\Household-Service-A-Z-\Backend/Class')

from Class import authentication_id,customer_add


#Flask is class in python used to setup an web application
app = Flask(__name__) 

#Creating DataBase of name A-Z_household_services
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AZ_household_services.db'


# Setting up tracking changes to off 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# creating an instance of the an app to store database
db = SQLAlchemy(app)

#Main login page
@app.route("/login")
def login():
    return render_template("login.html")


#Customer Signup page
@app.route("/sign_user",methods=["GET","POST"])
def signup_user():
       
    return render_template("customer_Signup.html")


#Professional Login page
@app.route("/sign_professional")
def signup_professor():
    return render_template("Professional_Signup.html")
 

# Calling app to run
if __name__ == "__main__":
    app.run(debug=True, port=5000)
