from sqlalchemy import inspect
from flask import session,render_template, request, flash, redirect, url_for,send_file
from app import app, db
from models import Credential, Customer, Professional, Service,Category,ServiceBooked,IDs,RejectionTracking
import os
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from sqlalchemy.orm import aliased
from datetime import datetime
from sqlalchemy import func,case



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

def book_service(last_booking_id, customer_id, service_id):
    try:
        # Check if the customer has already booked this service
        existing_booking = ServiceBooked.query.filter_by(customer_id=customer_id, service_id=service_id).first()
        print("nothing")
        if existing_booking:
            flash(('danger', 'You have already booked this service!', service_id))
            return
        # Generate the new booking ID once
        new_booking_id = generate_id(last_booking_id)

        # Create new service booking
        newbook = ServiceBooked(
            booking_id=new_booking_id,
            professional_id=None,
            customer_id=customer_id,
            service_id=service_id,
            status='Pending',
            rating_by_user=-1,
            rating_by_professional=-1,
            remarks_by_customer=None,
            remarks_by_professional=None
        )
        
        # Update IDs with the new booking info
        update = IDs(
            booking_id=new_booking_id,
            customer_id=None,
            professional_id=None,
            service_id=None,
            category_id=None,
            rejection_id=None
        )
        
        # Add both entries to the session
        db.session.add(newbook)
        db.session.add(update)
        
        # Commit the transaction
        db.session.commit()
        
        # Flash success message
        flash(('success', 'Service booked successfully', service_id))
    
    except Exception as e:
        # Rollback transaction in case of error
        db.session.rollback()
        
        # Flash error message with the associated service_id
        flash(('danger', f"Error booking service: {str(e)}", None))


# Routes
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = request.form["username"]
        password_input = request.form["pass"]
        user_record = Credential.query.filter_by(username=username_input).first()
        
        if auth(username_input) :
            session['user_id']=user_record.user_id
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
                    if(user_record.status=="active"):
                        return redirect(url_for('customer_home'))
                    else:
                        flash("Admin has Blocked you.","error")
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
        last_customer_id = db.session.query(IDs.customer_id) \
                            .filter(IDs.customer_id.isnot(None)) \
                            .order_by(IDs.id.desc()) \
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
                        full_name=full_name_input,
                        contact=contact,
                        address=address_input,
                        pin=pin_input
                    )
                    user_to_userid=IDs(
                        customer_id=customer_id_input,
                        professional_id=None,
                        service_id=None,
                        booking_id=None,
                        category_id=None,
                        rejection_id=None
                        
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
        last_Professional_id = db.session.query(IDs.professional_id) \
                            .filter(IDs.professional_id.isnot(None)) \
                            .order_by(IDs.id.desc()) \
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
                    service_id=db.session.query(Service.service_id).filter_by(service_name=service_input)
                    pdf_content = attach_document_input.read()
                    attach_document_url = save_pdf(pdf_content,"Backend\instance\Documents",Professional_id)

                    Professional_to_credential = Credential(
                        
                        user_id=Professional_id,
                        username=username,
                        status="Pending",
                        password=hash_password(password_input),
                        flag="professional"
                    )
                    db.session.add(Professional_to_credential)
                    db.session.commit()
                    professional_id_input = Professional_to_credential.user_id
                    Professional_to_table = Professional(
                        professional_id=professional_id_input,
                        username=username,
                        status="Pending",
                        service_id=service_id,
                        contact_number=Contact_number_input,
                        document=attach_document_url,
                        experience=experience_input,
                        full_name=full_name_input,
                        service_name=service_input,
                        address=address_input,
                        pin=pin_input
                    )

                    Userid = IDs(
                        professional_id=Professional_id,
                        customer_id=None,
                        service_id=None,
                        booking_id=None,
                        category_id=None,
                        rejection_id=None
                        )

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

@app.route("/Admin/home",methods=['POST',"GET"])
def admin_home():
    # Fetch joined data from Category and Service tables with restricted columns
    joined_data = (
        db.session.query(
            Category.category_name,
            Category.category_description.label("category_description"),
            Service.service_name,
            Service.service_id,
            Service.service_description.label("service_description"),
            Service.base_price
        )
        .join(Service, Category.category_id == Service.category_id)
        .all()
    )

    # Fetch professional data with restricted columns
    Professionals_data = Professional.query.with_entities(
        Professional.professional_id,
        Professional.full_name,
        Professional.contact_number,
        Professional.experience,
        Professional.document,
        Professional.service_name,
        Professional.status
    ).all()
    
    customer_data = Customer.query.with_entities(
        Customer.customer_id,
        Customer.full_name,
        Customer.contact,
        Customer.status
    ).all()
    
    service_requests = db.session.query(
        ServiceBooked.booking_id.label('id'),
        ServiceBooked.request_date,
        ServiceBooked.status,
        Professional.full_name.label('professional_name')
    ).outerjoin(
        Professional, ServiceBooked.professional_id == Professional.professional_id
    ).all()
    # Pass data to the template
    return render_template(
        "Admin/home.html",
        joined_data=joined_data,
        Professionals_data=Professionals_data,
        customer_data=customer_data,
        service_requests=service_requests
    )

@app.route('/admin/update_status', methods=['POST', 'GET'])
def update_status():
    professional_id = request.form['professional_id']
    new_status = request.form['status']
    
    # Find the professional record by id
    professional = Professional.query.get(professional_id)
    professional_cre=Credential.query.get(professional_id)
    
    if professional:
        # Update the professional status
        professional.status = new_status
        professional_cre.status=new_status
        db.session.commit()  # Commit the changes to the database
        
        flash(f"Status updated to {new_status} successfully.", "success")
    else:
        flash("Professional not found.", "danger")
    
    # Redirect to the home page after update (or wherever you want to send the user)
    return redirect(url_for('admin_home'))  # Redirect to the home route

@app.route('/view_document/<professional_id>')
def view_document(professional_id):
    professional = Professional.query.filter_by(professional_id=professional_id).first()
    return send_file("E:\clone\Household-Service-A-Z-\Backend\instance\Documents\24ASZPA2.pdf", mimetype='application/pdf', as_attachment=False)



@app.route("/admin/summary")
def admin_summary():
    # Fetch overall customer ratings for professionals
    professional_ratings = db.session.query(
        Professional.professional_id.label("professional_id"),
        Professional.full_name.label("professional_name"),
        db.func.avg(
            case(
                [(ServiceBooked.rating_by_user.isnot(None), ServiceBooked.rating_by_user)],
                else_=None  # Exclude null ratings
            )
        ).label("average_rating"),
        db.func.count(ServiceBooked.rating_by_user).label("rating_count")  # Count valid ratings
    ).join(ServiceBooked, Professional.professional_id == ServiceBooked.professional_id, isouter=True) \
     .group_by(Professional.professional_id, Professional.full_name).all()

    # Fetch customer data with service request counts and number of ratings given
    customer_summary = db.session.query(
        Customer.customer_id.label("customer_id"),
        Customer.full_name.label("customer_name"),
        db.func.count(ServiceBooked.booking_id).label("service_requests_count"),  # Count service requests
        db.func.count(
            case(
                [(ServiceBooked.rating_by_user.isnot(None), ServiceBooked.rating_by_user)],
                else_=None  # Count only valid ratings
            )
        ).label("ratings_given")  # Count ratings given by customer
    ).join(ServiceBooked, Customer.customer_id == ServiceBooked.customer_id, isouter=True) \
     .group_by(Customer.customer_id, Customer.full_name).all()

    # Fetch customer service request summary
    service_summary = db.session.query(
        ServiceBooked.status,
        db.func.count(ServiceBooked.booking_id).label("request_count")
    ).group_by(ServiceBooked.status).all()

    return render_template(
        "Admin/Summary.html",
        professional_ratings=professional_ratings,
        service_summary=service_summary,
        customer_summary=customer_summary  # Pass customer summary data
    )




@app.route("/Admin/Service", methods=["POST", "GET"])
def admin_service():
    # Check if we need to display the new category input field
    add_new_category = request.args.get('add_new_category', False)  # Get the query parameter
    
    if request.method == "POST":
        try:
            last_service_id = db.session.query(IDs.service_id) \
                .filter(IDs.service_id.isnot(None)) \
                .order_by(IDs.id.desc()) \
                .first()[0]
            last_category_id = db.session.query(IDs.category_id) \
                .filter(IDs.category_id.isnot(None)) \
                .order_by(IDs.id.desc()) \
                .first()[0]
            category_id_input = generate_id(last_category_id)
            service_id_input = generate_id(last_service_id)

            new_category_name = request.form.get('new_category_name')
            selected_category = request.form.get('category_name')
            category_description = request.form.get("category_description")
            service_name_input = request.form["Service_name"]
            description_input = request.form["Description"]
            base_price_input = request.form["Base_Price"]

            # Validation: Only one category option should be filled
            if not (new_category_name or selected_category):
                flash("Service Category is required.", "warning")
                return render_template("Admin/Service.html", add_new_category=add_new_category)

            if not service_name_input:
                flash("Service Name is required.", "warning")
                return render_template("Admin/Service.html", add_new_category=add_new_category)

            if not base_price_input:
                flash("Base Price is required.", "warning")
                return render_template("Admin/Service.html", add_new_category=add_new_category)
            
            if new_category_name:  # Add new category logic
                # Check if the new category already exists
                existing_category = Category.query.filter_by(category_name=new_category_name).first()
                if existing_category:
                    flash("Category already exists.", "warning")
                    return render_template("Admin/Service.html", add_new_category=True)
                
                # Add new category
                category = Category(
                    category_id=category_id_input,
                    category_name=new_category_name,
                    category_description=category_description
                )
                db.session.add(category)
                db.session.commit()
                category_id_input = category.category_id  # Get the new category's ID
            else:  # Use selected existing category
                category = Category.query.filter_by(category_name=selected_category).first()
                category_id_input = category.category_id

            # Create and add the service
            service = Service(
                category_id=category_id_input,
                service_id=service_id_input,
                service_name=service_name_input,
                service_description=description_input,
                base_price=base_price_input
            )

            user_id_update = IDs(
                customer_id=None,
                professional_id=None,
                service_id=service_id_input,
                booking_id=None,
                category_id=category_id_input,
                rejection_id=None
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

    category_names = [category[0] for category in db.session.query(Category.category_name).all()]
    return render_template("Admin/Service.html", category_names=category_names, add_new_category=add_new_category)


@app.route("/Admin/Search", methods=["POST", "GET"])
def admin_search():
    service_requests = []  # Default to an empty list for template consistency

    if request.method == "POST":
        # Get search parameters from the form
        search_type = request.form.get("search_type")
        search_query = request.form.get("search_query", "").strip()

        # Handle search by service name
        if search_type == "service_name":
            service_requests = db.session.query(
                ServiceBooked.booking_id,
                Service.service_name,
                Service.service_id,
                Professional.professional_id,
                ServiceBooked.request_date,
                Professional.full_name.label("professional_name"),
                ServiceBooked.status
            ).join(Service, ServiceBooked.service_id == Service.service_id) \
             .outerjoin(Professional, ServiceBooked.professional_id == Professional.professional_id) \
             .filter(Service.service_name.like(f"%{search_query}%")).all()

        # Handle search by professional name
        elif search_type == "professional_name":
            service_requests = db.session.query(
                ServiceBooked.booking_id,
                Service.service_name,
                Service.service_id,
                Professional.professional_id,
                ServiceBooked.request_date,
                Professional.full_name.label("professional_name"),
                ServiceBooked.status
            ).join(Service, ServiceBooked.service_id == Service.service_id) \
             .outerjoin(Professional, ServiceBooked.professional_id == Professional.professional_id) \
             .filter(Professional.professional_id.like(f"%{search_query}%")).all()

    return render_template("Admin/Search.html", service_requests=service_requests)



@app.route("/Professional/home", methods=["GET", "POST"])
def professional_home():
    # Check if the user_id exists in the session
    if 'user_id' not in session:
        flash("Please log in to access your account.")
        return redirect(url_for('login'))

    professional_id = session['user_id']  # Extract professional ID from session
    professional_data = db.session.query(Professional).filter_by(professional_id=professional_id).first()
    full_name=professional_data.full_name
    print(professional_id)
    # Create aliases for the Customer and Professional tables
    customer_alias = aliased(Customer)
    professional_alias = aliased(Professional)

    customer_book_data = (
        db.session.query(
            customer_alias.full_name.label("customer_full_name"),
            customer_alias.contact.label("customer_contact"),
            customer_alias.address.label("customer_address"),
            customer_alias.pin.label("customer_pin"),
            ServiceBooked.professional_id.label("professional_id"),            
            ServiceBooked.status.label("request_status"),
            ServiceBooked.booking_id.label("booked_service_id"),
        )
        # Join ServiceBooked to Customer
        .join(ServiceBooked, ServiceBooked.customer_id == customer_alias.customer_id)
        # Join ServiceBooked to Professional
        .join(professional_alias, ServiceBooked.service_id == professional_alias.service_id)
        # Filter by the logged-in professional
        .filter(professional_alias.professional_id == professional_id)
        .all()
    )
    rejection_entry_data=db.session.query(RejectionTracking).all()
    
    print(customer_book_data)
    # POST Handling for Accept/Reject actions
    if request.method == "POST":
        
        booking_id = request.form.get('service_id')
        action = request.form.get('action')  # 'Accept' or 'Reject'
        print(booking_id,action)
        # Validate inputs
        if not booking_id or not action:
            flash("Invalid action.")
            return redirect(url_for('professional_home'))

        # Get the service request
        service_request = ServiceBooked.query.filter_by(booking_id=booking_id).first()
        if service_request:
            try:
                if action == "Accept" :
                    service_request.status = "Accepted"
                    service_request.professional_id = professional_id
                elif action == "Reject":
                    last_rejection_id=db.session.query(IDs.rejection_id) \
                            .filter(IDs.rejection_id.isnot(None)) \
                            .order_by(IDs.id.desc()) \
                            .first()[0]
                    rejection_entry=RejectionTracking(
                        booking_id=service_request.booking_id,
                        professional_id=professional_id,
                        rejection_id=generate_id(last_rejection_id)
                    ) 
                    reject_data= IDs(
                        customer_id=None,
                        professional_id=None,
                        service_id=None,
                        booking_id=None,
                        category_id=None,
                        rejection_id=generate_id(last_rejection_id)
                    )
                      
                    print(professional_id,last_rejection_id,service_request.booking_id)
                    
                    db.session.add(rejection_entry)

                db.session.commit()
                flash("Action recorded successfully.")
            except Exception as e:
                db.session.rollback()
                flash("An error occurred. Please try again.")
                print(e)

        return redirect(url_for('professional_home'))
    print(customer_book_data[0].professional_id,professional_id)
    # Render the professional homepage
    return render_template("Professional/home.html", customer_book_data=customer_book_data,professional_id=professional_id,full_name=full_name,rejection_entry_data=rejection_entry_data)





@app.route("/Customer/home", methods=["POST", "GET"])
def customer_home():
    customer_id = session['user_id']

    if request.method == "POST":
        # Handle service booking
        if "service_id" in request.form:  # Booking a service
            last_booking_id = db.session.query(IDs.booking_id) \
                                .filter(IDs.booking_id.isnot(None)) \
                                .order_by(IDs.id.desc()) \
                                .first()[0]
            service_id = request.form["service_id"]
            book_service(last_booking_id, customer_id, service_id)
        
        # Handle closing service
        if "close_service_id" in request.form:  # Closing a service
            close_service_id = request.form["close_service_id"]
            service_booked = ServiceBooked.query.filter_by(
                booking_id=close_service_id, customer_id=customer_id
            ).first()
            if service_booked:
                service_booked.status = "Closed"
                db.session.commit()

    # Fetch the customer details using the session username
    user_record = Customer.query.filter_by(customer_id=customer_id).first()

    # Fetch service history
    service_history = db.session.query(
        Service.service_name,
        Professional.full_name.label("professional_name"),
        Professional.contact_number,
        ServiceBooked.status,
        ServiceBooked.booking_id
    ).join(ServiceBooked, Service.service_id == ServiceBooked.service_id) \
     .join(Professional, ServiceBooked.professional_id == Professional.professional_id, isouter=True) \
     .filter(ServiceBooked.customer_id == customer_id).all()

    if "category_id" in request.args:  # If a category is selected
        category_id = request.args.get("category_id")
        
        # Fetch services for the selected category
        services = Service.query.filter_by(category_id=category_id).all()
        
        # Fetch the selected category details
        selected_category = Category.query.filter_by(category_id=category_id).first()
        return render_template(
            "Customer/home.html",
            fullname=user_record.full_name,
            services=services,
            selected_category=selected_category,
            service_history=service_history
        )
    else:  # Default view showing all categories
        categories = Category.query.all()
        return render_template(
            "Customer/home.html",
            fullname=user_record.full_name,
            categories=categories,
            service_history=service_history
        )




@app.route('/categories')
def categories():
    # Fetch all categories
    categories = Category.query.all()  # Assuming you have a Category model
    return render_template('categories.html', categories=categories)

@app.route('/services/<int:category_id>')
def services(category_id):
    # Fetch services for the selected category
    services = Service.query.filter_by(category_id=category_id).all()
    return render_template('services.html', services=services)


@app.route('/Customer/summary')
def customer_summary():
    return render_template('Customer/summary.html')

@app.route('/Customer/search')
def customer_search():
    return render_template('Customer/search.html')


@app.route('/Admin/update_service', methods=["POST", "GET"])
def admin_update_service():
    if request.method == "POST":
        # Get and clean input from form
        Service_name = request.form.get('service_option').strip()  # Strip spaces and convert to lowercase
        description = request.form['Description']
        Base_price = request.form['Base_Price']
        image = request.files.get('image')

        # Debugging: Print the submitted and processed service name
        print(f"Service name submitted: {Service_name}")

        # Fetch the service record to update, making the query case-insensitive
        service_record = Service.query.filter_by(service_name=Service_name).first()

        # Debugging: Print the result of the query
        print(f"Service name in database: {service_record.service_name if service_record else 'None'}")

        if service_record:
            service_record.description = description
            service_record.base_price = Base_price

            # Commit the changes to the database
            db.session.commit()

            flash('Service updated successfully!', 'success')
            return redirect(url_for("admin_update_service"))
        else:
            flash('Service not found!', 'danger')
            return redirect(url_for("admin_update_service"))

    # Fetch all available service names for the dropdown or selection list
    Service_names = [service[0] for service in db.session.query(Service.service_name).all()]
        
    # Render the page with the list of service names
    return render_template('Admin/update_service.html', Service_names=Service_names)

@app.route('/Admin/customer_status',methods=["POST","GET"])
def customer_status():
    customer_id = request.form['customer_id']
    new_status = request.form['status']
    
    # Find the customer record by id
    customer = Customer.query.get(customer_id)
    customer_cre=Credential.query.get(customer_id)
    
    if customer:
        # Update the professional status
        customer.status = new_status
        customer_cre.status=new_status
        db.session.commit()  # Commit the changes to the database
        
        flash(f"Status updated to {new_status} successfully.", "success")
    else:
        flash("customer not found.", "danger")
    
    # Redirect to the home page after update (or wherever you want to send the user)
    return redirect(url_for('admin_home'))

@app.route("/Customer/rating/<booking_id>", methods=['POST', 'GET'])
def professional_rating(booking_id):
    if request.method == "POST":
        # Fetch form data
        service_rating = request.form.get('service_rating')
        service_remarks = request.form.get('service_remarks')

        # Fetch the corresponding service request
        service_request = ServiceBooked.query.filter_by(booking_id=booking_id).first()

        if service_request:
            # Update the service request with rating and remarks
            service_request.rating_by_user = service_rating
            service_request.remarks_by_customer = service_remarks
            service_request.status = "Closed"
            service_request.submission_date = datetime.utcnow()
            
            # Commit changes to the database
            db.session.commit()
            flash("Thank you for your feedback!", "success")
            return redirect(url_for('customer_home'))
        else:
            flash("Invalid service request.", "danger")
            return redirect(url_for('customer_home'))

    # Fetch service details for the GET request to display the rating form
    service_request = db.session.query(
        ServiceBooked.booking_id,
        Service.service_name,
        Service.service_id,
        Professional.professional_id,
        ServiceBooked.request_date,
        Professional.full_name.label("professional_name"),
        Professional.contact_number
    ).join(Service, ServiceBooked.service_id == Service.service_id) \
     .outerjoin(Professional, ServiceBooked.professional_id == Professional.professional_id) \
     .filter(ServiceBooked.booking_id == booking_id).first()

    # If no service request found, redirect to customer home
    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for('customer_home'))

    # Render the rating form
    return render_template("Customer/rating.html", service_request=service_request)

