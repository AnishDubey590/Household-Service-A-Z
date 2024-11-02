#Importing necessary libraries in app.py to create database and templates
from flask import Flask, render_template,request,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

#Flask is class in python used to setup an web application
app = Flask(__name__) 
app.secret_key = '1212121212121'  


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///A-Z Services.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

                    
def auth(id):
    users = Credential.query.filter_by(User_id=id).first()
    if(users):
        return True
    else:
        return False
                    

#credential 
class Credential(db.Model):
    User_id=db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    flag=db.Column(db.String(10),nullable=False)

# Customer model
class Customer(db.Model):
    customer_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)

# Professional model
class Professional(db.Model):
    professional_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    service_name=db.Column(db.String(100), nullable=False)
    document = db.Column(db.LargeBinary, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)
    
    
# Service model
class Service(db.Model):
    service_id = db.Column(db.String(50), primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    description=db.Column(db.String(200), nullable=False)
    base_price = db.Column(db.Float, nullable=False)


#Main login page

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = request.form["username"]
        password_input = request.form["pass"]
        
        # Check if the user exists and retrieve user details
        user_record = Credential.query.filter_by(User_id=username_input).first()
        
        # Validate the user's existence and credentials
        if user_record and user_record.password == password_input:
            # Check for admin privileges
            if user_record.flag == "admin":
                return redirect(url_for("admin_home"))
            else:
                flash("Access denied. Admin privileges required.", "error")
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")



#Customer Signup page
@app.route("/sign_user",methods=["GET","POST"])
def signup_user():
    if request.method=='POST':
            customer_id=request.form["customer_id"]
            if(not auth(customer_id)):
                passw=request.form["password"]
                Confirm_Password=request.form["ConfirmPassword"]
                if(passw==Confirm_Password):
                    full_name=request.form["fullname"]
                    address=request.form["address"]
                    pin=request.form["pincode"]  
                    user= Credential(User_id=customer_id, password=passw,flag="customer")
                    db.session.add(user)
                    db.session.commit()
                    print("Sucessfully added")
                else:
                    flash("Passwords do not match.", "error")
                    return redirect(url_for('signup_user'))
            else:
                flash("Username Already exist ", "error")
                return redirect(url_for('signup_user'))
            print("Sucessfully added????")        
    return render_template("customer_Signup.html")


#Professional Login page
@app.route("/sign_professional")
def signup_professor():
    return render_template("Professional_Signup.html")
 
@app.route("/Admin/home")
def admin_home():
    return render_template("Admin/home.html")

@app.route("/Admin/Summary")
def admin_summary():
    return render_template("Admin/Summary.html")


# Calling app to run
if __name__ == "__main__":
    app.run(debug=True, port=5000)

