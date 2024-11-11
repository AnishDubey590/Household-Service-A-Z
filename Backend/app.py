from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from config import Config 
 


# Initialize the Flask application and the database
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)



# Import routes to register them
from routes import *

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5000)
