# Importing the app, db, and the Credential model
import sys

sys.path.insert(2, 'E:\\clone\\Household-Service-A-Z-\\Backend')

from routes import db, Credential, IDs, app

# Creating the app context to work with the db
with app.app_context():
    # Checking if admin credential already exists
    if not Credential.query.filter_by(user_id="Admin").first():
        # Create a new admin credential and a starting customer ID
        admin_user = Credential(user_id="24ASZAdmin", username="Admin", password="Admin", flag="admin", status='admin_only')
        first_customer_id = IDs(customer_id="24ASZCA0", professional_id="24ASZPA0",service_id="24ASZSA0",booking_id="24ASZBA0")

        # Add both instances to the session
        db.session.add_all([admin_user, first_customer_id])
        db.session.commit()
        print("Admin user added successfully!")
    else:
        print("Admin user already exists.")
