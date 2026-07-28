from flask import Flask, render_template

# Import the initialized database instance from our models package
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Bind the database instance to this specific Flask application
    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()