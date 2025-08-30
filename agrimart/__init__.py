from flask import Flask

def create_app():
    # Point Flask to the project-level static directory
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    
    # Set a secret key for sessions
    app.secret_key = 'agrimart-secret-key-2024'
    
    from . import routes  # import routes AFTER app is created
    routes.init_app(app)  # call function to register routes
    
    return app
