from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

# Import the initialized database instance from our models package
from models import db
from models.user import User

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Bind the database instance to this specific Flask application
    db.init_app(app)

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            # Read email and password from the form
            email = request.form.get("email")
            password = request.form.get("password")
            
            # Search the user by email
            user = User.query.filter_by(email=email).first()
            
            # If user does not exist, show a friendly error
            if not user:
                return render_template("login.html", error="We couldn't find an account with that email.")
                
            # If user exists, verify password using check_password_hash()
            if not check_password_hash(user.password_hash, password):
                return render_template("login.html", error="Incorrect password. Please try again.")
                
            # If password is correct, store user id in Flask session
            session["user_id"] = user.id
            
            # Redirect to Home page
            return redirect(url_for("home"))
            
        # On GET request, render the login page
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            # Read form data
            full_name = request.form.get("full_name")
            email = request.form.get("email")
            password = request.form.get("password")
            role = request.form.get("role", "user")
            
            # Validate that required fields are not empty
            if not full_name or not email or not password:
                return render_template("register.html", error="Please fill out all required fields.")
                
            # Check whether the email already exists in the database
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template("register.html", error="That email is already registered. Please log in.")
                
            # Hash the password securely using Werkzeug
            hashed_password = generate_password_hash(password)
            
            # Create a new User object
            new_user = User(
                full_name=full_name,
                email=email,
                password_hash=hashed_password,
                role=role
            )
            
            # Save it into SQLite and commit the transaction
            db.session.add(new_user)
            db.session.commit()
            
            # Redirect to Login page after successful registration
            return redirect(url_for("login"))
            
        # On GET request, just render the page
        return render_template("register.html")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()