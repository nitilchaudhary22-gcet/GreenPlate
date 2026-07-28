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

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/register")
    def register():
        return render_template("register.html")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()