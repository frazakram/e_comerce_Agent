# Import the Flask application instance
from application import app as application

# For compatibility with different WSGI servers
app = application

if __name__ == "__main__":
    application.run()
