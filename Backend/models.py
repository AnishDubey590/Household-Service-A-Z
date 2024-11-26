from app import db
from datetime import datetime

# Category table
class Category(db.Model):
    __tablename__ = 'Category'
    category_id = db.Column(db.String(50), primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    category_description = db.Column(db.String(200), nullable=True)
    services = db.relationship('Service', backref='category', lazy=True)

    def __init__(self, category_id, category_name, category_description):
        self.category_id = category_id
        self.category_name = category_name
        self.category_description = category_description

# Service table
class Service(db.Model):
    __tablename__ = 'Service'
    service_id = db.Column(db.String(50), primary_key=True)
    service_name = db.Column(db.String(100), nullable=False, unique=True)
    service_description = db.Column(db.String(200), nullable=False)
    base_price = db.Column(db.Integer(), nullable=False)
    category_id = db.Column(db.String(50), db.ForeignKey('Category.category_id'), nullable=False)
    requests = db.relationship('ServiceBooked', backref='service', lazy=True)

    def __init__(self, service_id, service_name, service_description, base_price, category_id):
        self.service_id = service_id
        self.service_name = service_name
        self.service_description = service_description
        self.base_price = base_price
        self.category_id = category_id

# Credential table
class Credential(db.Model):
    __tablename__ = 'Credential'
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    flag = db.Column(db.String(10), nullable=False)  # 'customer', 'professional', or 'admin'
    status = db.Column(db.String(10), nullable=False)  # 'active' or 'blocked'

    def __init__(self, user_id, username, password, flag, status='active'):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.flag = flag
        self.status = status

# Customer table
class Customer(db.Model):
    __tablename__ = 'Customer'
    customer_id = db.Column(db.String(50),  db.ForeignKey('Credential.user_id'),primary_key=True)
    username=db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(15), nullable=True)
    pin = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(10), default='active')
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    requests = db.relationship('ServiceBooked', backref='customer', lazy=True)

    def __init__(self,username, customer_id, full_name, address, pin, contact=None, status='active', registration_date=None):
        self.customer_id = customer_id
        self.username=username
        self.full_name = full_name
        self.address = address
        self.pin = pin
        self.contact = contact
        self.status = status
        self.registration_date = registration_date or datetime.utcnow()

# Professional table
class Professional(db.Model):
    __tablename__ = 'Professional'
    professional_id = db.Column(db.String(50),db.ForeignKey('Credential.user_id'), primary_key=True, )
    username=db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    contact_number = db.Column(db.String(15), nullable=True)
    service_name = db.Column(db.String(100), nullable=False)
    service_id=db.Column(db.String(50),nullable=False)
    document = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(10), default='active')
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    services_booked = db.relationship('ServiceBooked', backref='professional', lazy=True)

    def __init__(self,username,service_id, professional_id, full_name, experience, service_name, document, address, pin, contact_number=None, status='active', registration_date=None):
        self.professional_id = professional_id
        self.username=username
        self.full_name = full_name
        self.experience = experience
        self.service_id=service_id
        self.contact_number = contact_number
        self.service_name = service_name
        self.document = document
        self.address = address
        self.pin = pin
        self.status = status
        self.registration_date = registration_date or datetime.utcnow()

# ServiceBooked table
class ServiceBooked(db.Model):
    __tablename__ = 'services_booked'
    booking_id = db.Column(db.String(50), primary_key=True)
    customer_id = db.Column(db.String(50), db.ForeignKey('Customer.customer_id'), nullable=False)
    professional_id = db.Column(db.String(50), db.ForeignKey('Professional.professional_id'), nullable=True)
    service_id = db.Column(db.String(50), db.ForeignKey('Service.service_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False,primary_key=True)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    completion_date = db.Column(db.DateTime, nullable=True)
    rating_by_user = db.Column(db.Integer(), nullable=True)
    rating_by_professional = db.Column(db.Integer(), nullable=True)
    remarks_by_customer = db.Column(db.String(200), nullable=True)
    remarks_by_professional = db.Column(db.String(200), nullable=True)


    def __init__(self, booking_id, customer_id, service_id, status, professional_id=None, rating_by_user=None, rating_by_professional=None, remarks_by_customer=None, remarks_by_professional=None, completion_date=None):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.professional_id = professional_id
        self.service_id = service_id
        self.status = status
        self.rating_by_user = rating_by_user
        self.rating_by_professional = rating_by_professional
        self.remarks_by_customer = remarks_by_customer
        self.remarks_by_professional = remarks_by_professional
        self.completion_date = completion_date

class RejectionTracking(db.Model):
    __tablename__ = 'RejectionTracking'
    booking_id = db.Column(db.String(50), db.ForeignKey('services_booked.service_id'), primary_key=True)
    professional_id = db.Column(db.String(50), db.ForeignKey('Professional.professional_id'), primary_key=True)
    
    rejection_id=db.Column(db.String(50),primary_key=True)
    def __init__(self,booking_id,professional_id,rejection_id):
        self.booking_id=booking_id
        self.professional_id=professional_id
        self.rejection_id=rejection_id

class IDs(db.Model):
    __tablename__ = 'IDs'  
    id = db.Column(db.Integer, primary_key=True,autoincrement=True) 
    customer_id = db.Column(db.String(50), unique=True)  
    professional_id = db.Column(db.String(50), unique=True)
    service_id=db.Column(db.String(50), unique=True)
    booking_id=db.Column(db.String(50), unique=True) 
    category_id=db.Column(db.String(50))
    rejection_id=db.Column(db.String(50),unique=True)
    def __init__(self, customer_id, professional_id,rejection_id,service_id,booking_id,category_id):
        self.customer_id = customer_id
        self.professional_id = professional_id
        self.service_id=service_id
        self.booking_id=booking_id
        self.category_id=category_id
        self.rejection_id=rejection_id