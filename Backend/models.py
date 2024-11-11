from app import db
from datetime import datetime


# Credentials table
class Credential(db.Model):
    __tablename__ = 'Credential'
    user_id = db.Column(db.String(50), primary_key=True)
    username=db.Column(db.String(50), nullable=False,unique=True)
    password = db.Column(db.String(50), nullable=False)
    flag = db.Column(db.String(10), nullable=False)  # 'customer' or 'professional' or 'Admin'
    status = db.Column(db.String(10 ), nullable=False)  # 'Active' or 'block'
    
    def __init__(self, user_id,username, password, flag, status):
        self.user_id = user_id
        self.username=username
        self.password = password
        self.flag = flag
        self.status = status

# Customer table
class Customer(db.Model):
    __tablename__ = 'Customer'
    customer_id = db.Column(db.String(50), primary_key=True)
    username=db.Column(db.String(50), nullable=False,unique=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact=db.Column(db.Integer(),nullable=True)
    pin = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(10), default='active')  # 'active' or 'blocked'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    requests = db.relationship('ServiceBooked', backref='customer', lazy=True)

    def __init__(self, username,customer_id, password, full_name, address, pin,contact, status='active', registration_date=None):
        if registration_date is None:
            registration_date = datetime.utcnow()
        self.customer_id = customer_id
        self.username=username
        self.password = password
        self.full_name = full_name
        self.contact=contact
        self.address = address
        self.pin = pin
        self.status = status
        self.registration_date = registration_date

# Professional table
class Professional(db.Model):
    __tablename__ = 'Professional'
    professional_id = db.Column(db.String(50), primary_key=True)
    username=db.Column(db.String(50), nullable=False,unique=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    Experience = db.Column(db.String(50), nullable=False)  # Changed to match `experience_input`
    contact_number = db.Column(db.String(15), nullable=True)
    service_name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(10), default='active')  # 'active' or 'blocked'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    services_booked = db.relationship('ServiceBooked', backref='professional', lazy=True)

    def __init__(self, username,professional_id, password, full_name, Experience, contact_number, service_name, document, address, pin, status='active', registration_date=None):
        if registration_date is None:
            registration_date = datetime.utcnow()
        self.username=username    
        self.professional_id = professional_id
        self.password = password
        self.full_name = full_name
        self.Experience = Experience
        self.contact_number = contact_number
        self.service_name = service_name
        self.document = document
        self.address = address
        self.pin = pin
        self.status = status
        self.registration_date = registration_date

# Services table
class Service(db.Model):
    __tablename__ = 'Service'
    service_id = db.Column(db.String(50), primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    service_img=db.Column(db.Text,nullable=True)
    description = db.Column(db.String(200), nullable=False)
    base_price = db.Column(db.Integer(), nullable=False)
    requests = db.relationship('ServiceBooked', backref='service', lazy=True)

    def __init__(self, service_id, service_name, description, base_price):
        self.service_id = service_id
        self.service_name = service_name
        self.description = description
        self.base_price = base_price

# ServiceBooked table to track bookings
class ServiceBooked(db.Model):
    __tablename__ = 'services_booked'
    booking_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('Customer.customer_id'), nullable=False)
    professional_id = db.Column(db.String(50), db.ForeignKey('Professional.professional_id'), nullable=False)
    service_id = db.Column(db.String(50), db.ForeignKey('Service.service_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'pending', 'approved', 'rejected'
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime, nullable=True)  # Date when the service was completed
    rating_by_user = db.Column(db.Integer(), nullable=False)
    rating_by_professional = db.Column(db.Integer(), nullable=False)
    remarks_by_customer = db.Column(db.String(200), nullable=True)  # Notes to the professional from Customer
    remarks_by_professional = db.Column(db.String(200), nullable=True)

    def __init__(self, customer_id, professional_id, service_id, status, rating_by_user, rating_by_professional, remarks_by_customer=None, remarks_by_professional=None, completion_date=None):
        self.customer_id = customer_id
        self.professional_id = professional_id
        self.service_id = service_id
        self.status = status
        self.rating_by_user = rating_by_user
        self.rating_by_professional = rating_by_professional
        self.remarks_by_customer = remarks_by_customer
        self.remarks_by_professional = remarks_by_professional
        self.completion_date = completion_date
class User_id(db.Model):
    __tablename__ = 'User_id'  
    
    id = db.Column(db.Integer, primary_key=True,autoincrement=True) 
    customer_id = db.Column(db.String(50), unique=True)  
    professional_id = db.Column(db.String(50), unique=True)
    service_id=db.Column(db.String(50), unique=True)
    def __init__(self, customer_id, professional_id,service_id):
        self.customer_id = customer_id
        self.professional_id = professional_id
        self.service_id=service_id