from app import db

#Credentials table 
class Credential(db.Model):
    User_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    flag = db.Column(db.String(10), nullable=False)

#Customer details table
class Customer(db.Model):
    customer_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)

#Professional details table
class Professional(db.Model):
    professional_id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    Experience=db.Column(db.String(50),nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    document = db.Column(db.LargeBinary, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin = db.Column(db.Integer(), nullable=False)

#services of app
class Service(db.Model):
    service_id = db.Column(db.String(50), primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
