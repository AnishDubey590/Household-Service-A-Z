from sqlalchemy import inspect
from flask import render_template, request, flash, redirect, url_for
from app import app, db
from models import Credential, Customer, Professional, Service

service_created_id=[1000]
# Utility Functions
def auth(id):
    users = Credential.query.filter_by(User_id=id).first()
    return bool(users)

def generate_service_id(id):
    id=id+1
    return id

# Routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
            username_input = request.form["username"]
            password_input = request.form["pass"]
            user_record = Credential.query.filter_by(User_id=username_input).first()
            if user_record and user_record.password == password_input:
                if user_record.flag == "admin":
                    return redirect(url_for("admin_home"))
                else:
                    flash("Access denied. Admin privileges required.", "error")
            else:
                flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/sign_user", methods=["GET", "POST"])
def signup_user():
    if request.method == 'POST':
        customer_id_input = request.form["customer_id"]
        if not auth(customer_id_input):
            password_input = request.form["password"]
            Confirm_Password_input = request.form["ConfirmPassword"]
            if password_input == Confirm_Password_input:
                full_name_input = request.form["fullname"]
                address_input = request.form["address"]
                pin_input = request.form["pincode"]
                if not full_name_input.strip() or not address_input.strip() or not pin_input.strip():
                    flash("Full name, address, and pin cannot be empty.", "error")
                    return redirect(url_for('signup_user'))
                user_to_credential = Credential(User_id=customer_id_input, password=password_input, flag="customer")
                user_to_customer=Customer(customer_id=customer_id_input,password=password_input,full_name=full_name_input,address=address_input,pin=pin_input)
                
                db.session.add(user_to_credential)
                db.session.commit()
                db.session.add(user_to_customer)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash("Passwords do not match.", "error")
                return redirect(url_for('signup_user'))
        else:
            flash("Username already exists.", "error")
            return redirect(url_for('signup_user'))     
    return render_template("customer_Signup.html")

@app.route("/sign_professional",methods=['POST','GET'])
def signup_professional():
    if request.method == 'POST':
        Professional_id_input = request.form["professional_id"]
        if not auth(Professional_id_input):
            password_input = request.form["password"]
            Confirm_Password_input = request.form["confirmPassword"]
            if password_input == Confirm_Password_input:
                full_name_input = request.form["fullname"]
                address_input = request.form["address"]
                pin_input = request.form["pincode"]
                experience_input=request.form['experience']
                service_input=request.form.get("service_option")
                attach_document_input=request.files.get('attach_document') 
                attach_document_binary=attach_document_input.read()
                if not attach_document_input or attach_document_input.filename == "":
                    flash("Document must be attached.", "error")
                    return redirect(url_for('signup_professor'))
                if not full_name_input.strip() or not address_input.strip() or (pin_input is None or experience_input is None):
                    flash("Full name, address,Experience, and pin cannot be empty.", "error")
                    return redirect(url_for('signup_professional'))
                Professional_to_credential = Credential(User_id=Professional_id_input, password=password_input, flag="professional")
                Professional_to_table=Professional(professional_id=Professional_id_input,document=attach_document_binary,password=password_input,Experience=experience_input,full_name=full_name_input,service_name=service_input,address=address_input,pin=pin_input)
                
                db.session.add(Professional_to_credential)
                db.session.commit()
                db.session.add(Professional_to_table)
                db.session.commit()
                print("oohno")
                return redirect(url_for('login'))
            else:
                print("tu ja re")
                flash("Passwords do not match.", "error")
                return redirect(url_for('signup_professional'))
        else:
            flash("Username already exists.", "error")
            return redirect(url_for('signup_professional'))
    return render_template("Professional_Signup.html")


@app.route("/Admin/home")
def admin_home():
    Service_inspector = inspect(Service)
    Professional_inspector=inspect(Professional)
    heading_Service_names= [column.name for column in Service_inspector.columns]
    heading_Professional_names=[column.name for column in Professional_inspector.columns]
    Services_data=Service.query.all()
    Professionals_data=Professional.query.all()
    return render_template("Admin/home.html",
                           heading_Service_names=heading_Service_names,
                           Services_data=Services_data,
                           heading_Professional_names=heading_Professional_names,
                           Professionals_data=Professionals_data)
@app.route("/Admin/Summary")
def admin_summary():
    return render_template("Admin/Summary.html")

@app.route("/Admin/Service", methods=["POST", "GET"])
def admin_service():
    if request.method == "POST":
        service_created_id[0]=generate_service_id(service_created_id[0])
        service_id_input = service_created_id[0]
        service_name_input = request.form["Service_name"]
        Description_input = request.form["Description"]
        Base_price_input = request.form["Base_Price"]
        
        service_record = Service.query.filter_by(service_id=service_id_input).first()
        if not service_record or service_record.service_name != service_name_input:
            service = Service(service_id=service_id_input, service_name=service_name_input, description=Description_input, base_price=Base_price_input)
            db.session.add(service)
            db.session.commit()
            return redirect(url_for('admin_service'))
    return render_template("Admin/Service.html")

