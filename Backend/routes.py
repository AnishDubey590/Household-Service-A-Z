from sqlalchemy import inspect
from flask import session,render_template, request, flash, redirect, url_for
from app import app, db
from models import Credential, Customer, Professional, Service, User_id
import os
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from flask import abort

# Utility Functions
def auth(id):
    users = Credential.query.filter_by(username=id).first()
    return bool(users)

def generate_id(last_id):
    constant_part = last_id[:-2]  # Example: "24AZSP" or "24AZSC"
    serial_part = last_id[-2:]    # Example: "A0"

    if serial_part[1] != "9":
        new_serial = serial_part[0] + str(int(serial_part[1]) + 1)
    else:
        new_serial = chr(ord(serial_part[0]) + 1) + "0"

    return constant_part + new_serial

def save_pdf(pdf_content, folder_path, user_id):
    new_filename = f"{user_id}.pdf"
    file_path = os.path.join(folder_path, new_filename)
    with open(file_path, 'wb') as file:
        file.write(pdf_content)
    return file_path

# New Helper Function for Password Hashing and Validation
def hash_password(password):
    return generate_password_hash(password)

def validate_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

def validate_required_fields(fields):
    for field in fields:
        if not field.strip():
            return False
    return True

def redirect_admin_home(admin):
    return()

# Routes
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = request.form["username"]
        password_input = request.form["pass"]
        user_record = Credential.query.filter_by(username=username_input).first()
        session['username']=username_input
        if auth(username_input) :
            if user_record.flag == "admin":
                if(user_record.password==password_input):
                    return redirect(url_for("admin_home"))
                else:
                    flash("Access denied","error")
                    return redirect(url_for('login'))
            elif validate_password(user_record.password, password_input):  
                if user_record.flag == "professional":
                    if(user_record.status=="Approved"):
                        return redirect(url_for('professional_home'))
                    else:
                        flash("Approvel Pending by Admin","error")
                elif user_record.flag == "customer":
                    return redirect(url_for('customer_home'))
                else:
                    flash("Access denied. Admin privileges required.", "error")
                    return redirect(url_for('login'))
            else:
                flash("Password not match.", "error")
                return redirect(url_for('login'))
        else:
            flash("Username Doesn't exists","error") 
            return redirect(url_for('login'))       
    return render_template("login.html")

@app.route("/sign_customer", methods=["GET", "POST"])
def signup_user():
    if request.method == 'POST':
        last_customer_id = db.session.query(User_id.customer_id) \
                            .filter(User_id.customer_id.isnot(None)) \
                            .order_by(User_id.id.desc()) \
                            .first()[0]  
              
        customer_id_input = generate_id(last_customer_id)
        username = request.form["username"]
        if not auth(customer_id_input):
            password_input = request.form["password"]
            Confirm_Password_input = request.form["ConfirmPassword"]
            if password_input == Confirm_Password_input:
                full_name_input = request.form["fullname"]
                contact=request.form["contact"]
                address_input = request.form["address"]
                pin_input = request.form["pincode"]
                if not validate_required_fields([full_name_input, address_input, pin_input]):
                    flash("Full name, address, and pin cannot be empty.", "error")
                    return redirect(url_for('signup_user'))
                
                try:
                    user_to_credential = Credential(
                        user_id=customer_id_input,
                        username=username,
                        status='Active',
                        password=hash_password(password_input),
                        flag="customer"
                    )
                    user_to_customer = Customer(
                        customer_id=customer_id_input,
                        username=username,
                        password=hash_password(password_input),
                        full_name=full_name_input,
                        contact=contact,
                        address=address_input,
                        pin=pin_input
                    )
                    user_to_userid=User_id(
                        customer_id=customer_id_input,
                        professional_id=None,
                        service_id=None
                        
                    )
                    
                    db.session.add(user_to_credential)
                    db.session.add(user_to_customer)
                    db.session.add(user_to_userid)
                    db.session.commit()
                    return redirect(url_for('login'))

                except SQLAlchemyError as e:
                    db.session.rollback()
                    logging.error("Error creating user account", exc_info=True)
                    flash("An error occurred while creating your account. Please try again.", "error")
                    return redirect(url_for('signup_user'))

            else:
                flash("Passwords do not match.", "error")
                return redirect(url_for('signup_user'))
        else:
            flash("Username already exists.", "error")
            return redirect(url_for('signup_user'))

    return render_template("customer_Signup.html")


@app.route("/sign_professional", methods=['POST', 'GET'])
def signup_professional():
    if request.method == 'POST':
        last_Professional_id = db.session.query(User_id.professional_id) \
                            .filter(User_id.professional_id.isnot(None)) \
                            .order_by(User_id.id.desc()) \
                            .first()[0]
        Professional_id = generate_id(last_Professional_id)
        username = request.form["username"]
        if not auth(username):
            password_input = request.form["password"]
            Confirm_Password_input = request.form["confirmPassword"]
            if password_input == Confirm_Password_input:
                full_name_input = request.form["fullname"]
                address_input = request.form["address"]
                pin_input = request.form["pincode"]
                experience_input = request.form['experience']
                Contact_number_input = request.form['contact_number']
                service_input = request.form.get("service_option")
                attach_document_input = request.files.get('attach_document')

                if not attach_document_input or attach_document_input.filename == "":
                    flash("Document must be attached.", "error")
                    return redirect(url_for('signup_professional'))

                if not validate_required_fields([full_name_input, address_input, pin_input, experience_input]):
                    flash("Full name, address, Experience, and pin cannot be empty.", "error")
                    return redirect(url_for('signup_professional'))

                try:
                    pdf_content = attach_document_input.read()
                    attach_document_url = save_pdf(pdf_content, "E:\\clone\\Household-Service-A-Z-\\Backend\\instance\\Documents", Professional_id)

                    Professional_to_credential = Credential(
                        user_id=Professional_id,
                        username=username,
                        status="Pending",
                        password=hash_password(password_input),
                        flag="professional"
                    )

                    Professional_to_table = Professional(
                        professional_id=Professional_id,
                        username=username,
                        status="Pending",
                        contact_number=Contact_number_input,
                        document=attach_document_url,
                        password=hash_password(password_input),
                        Experience=experience_input,
                        full_name=full_name_input,
                        service_name=service_input,
                        address=address_input,
                        pin=pin_input
                    )

                    Userid = User_id(
                        professional_id=Professional_id,
                        customer_id=None,
                        service_id=None)

                    db.session.add(Professional_to_credential)
                    db.session.add(Professional_to_table)
                    db.session.add(Userid)
                    db.session.commit()

                    return redirect(url_for('login'))

                except SQLAlchemyError as e:
                    db.session.rollback()
                    logging.error("Error creating professional account", exc_info=True)
                    flash("An error occurred while creating your account. Please try again.", "error")
                    return redirect(url_for('signup_professional'))
            else:
                flash("Passwords do not match.", "error")
                return redirect(url_for('signup_professional'))
        else:
            flash("Username already exists.", "error")
            return redirect(url_for('signup_professional'))
    
    Service_names = [service[0] for service in db.session.query(Service.service_name).all()]
    return render_template("Professional_Signup.html",
                           Services_names=Service_names)


@app.route("/Admin/home")
def admin_home():
    Service_inspector = inspect(Service)
    Professional_inspector=inspect(Professional)
    heading_Service_names= [column.name for column in Service_inspector.columns]
    heading_Professional_names=['full_name','Experience','service_name']
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
        try:
            # Fetch last service ID and generate new ID
            last_service_id = db.session.query(User_id.service_id) \
                                .filter(User_id.service_id.isnot(None)) \
                                .order_by(User_id.id.desc()) \
                                .first()[0]
            service_id_input = generate_id(last_service_id)
            service_name_input = request.form.get("Service_name", "").strip()
            description_input = request.form.get("Description", "").strip()
            base_price_input = request.form.get("Base_Price", "").strip()

            # Validate all required fields
            if not service_name_input:
                flash("Service Name is required.", "warning")
                return render_template("Admin/Service.html")
            if not base_price_input:
                flash("Base Price is required.", "warning")
                return render_template("Admin/Service.html")
            if not description_input:
                flash("Description is required.", "warning")
                return render_template("Admin/Service.html")

            # Create and add new records if validation passes
            service = Service(
                service_id=service_id_input,
                service_name=service_name_input,
                description=description_input,
                base_price=base_price_input
            )
            user_id_update = User_id(
                customer_id=None, 
                professional_id=None, 
                service_id=service_id_input
            )

            db.session.add(service)
            db.session.add(user_id_update)
            db.session.commit()
            flash("Service added successfully!", "success")
            return redirect(url_for('admin_service'))

        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.expire_all()  # Clear uncommitted session states
            flash("An error occurred while adding the service. Please try again.", "danger")
            print(f"Error: {e}")

    return render_template("Admin/Service.html")

@app.route("/Admin/Search")
def admin_search():
    return render_template("Admin/Search.html")

@app.route("/Professional/home")
def professional_home():
    username=session['username']
    users = Credential.query.filter_by(user_id=username).first()
    
    return render_template("Admin/home.html")

@app.route("/Customer/home")
def customer_home():
    Service_names = [service[0] for service in db.session.query(Service.service_name).all()]
    print(Service_names)
    return render_template('Customer/home.html',Service_names=Service_names)

@app.route('/Customer/summary')
def customer_summary():
    return render_template('Customer/summary.html')

@app.route('/Customer/search')
def customer_search():
    return render_template('Customer/search.html')
