import sys

sys.path.insert(0,'E:\clone\Household-Service-A-Z-\Backend')

from Backend.Main import app, db

with app.app_context():
    print("Entering app context")
    db.create_all()
    print("Database created!")
