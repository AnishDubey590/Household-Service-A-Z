# Importing the app, db, and the Credential model
import sys


sys.path.insert(2,'E:\clone\Household-Service-A-Z-\Backend')

from Backend.app import db,Credential,app
# Creating  the app context to work with the db
with app.app_context():
    # Checking if admin already  credential exists
    if not Credential.query.filter_by(User_id="Admin").first():
        # Create a new admin credential
        admin_user = Credential(User_id="Admin", password="Admin",flag="admin")
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user added successfully!")
    else:
        print("Admin user already exists.")
