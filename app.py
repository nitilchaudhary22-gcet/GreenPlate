from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Import the initialized database instance from our models package
from models import db
from models.user import User
from models.food_donation import FoodDonation
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Bind the database instance to this specific Flask application
    db.init_app(app)

    # Create tables if they do not exist
    with app.app_context():
        db.create_all()

    # Decorator to protect routes that require login
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # If user is not logged in, redirect to login page
            if "user_id" not in session:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function

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
            
            # Redirect users based on their role
            if user.role == "restaurant":
                return redirect(url_for("restaurant_dashboard"))
            elif user.role == "ngo":
                return redirect(url_for("ngo_dashboard"))
            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
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
            role = request.form.get("role")
            
            # Validate that required fields are not empty
            if not full_name or not email or not password or not role:
                return render_template("register.html", error="Please fill out all required fields.")
                
            # Validate role
            allowed_roles = ["restaurant", "ngo"]
            if role not in allowed_roles:
                return render_template("register.html", error="Invalid role selected. Please choose a valid role.")
                
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

    # --- Dashboards ---

    @app.route("/restaurant/dashboard")
    @login_required
    def restaurant_dashboard():
        # Fetch the current logged-in user
        user = User.query.get(session["user_id"])
        
        # Verify role, otherwise redirect to home
        if not user or user.role != "restaurant":
            return redirect(url_for("home"))
            
        total_donations = FoodDonation.query.filter_by(restaurant_id=user.id).count()
        available_donations = FoodDonation.query.filter_by(restaurant_id=user.id, status="available").count()
        claimed_donations = FoodDonation.query.filter_by(restaurant_id=user.id, status="claimed").count()
        picked_up_donations = FoodDonation.query.filter_by(restaurant_id=user.id, status="picked_up").count()
        
        stats = {
            "total": total_donations,
            "available": available_donations,
            "claimed": claimed_donations,
            "picked_up": picked_up_donations
        }
            
        return render_template("restaurant_dashboard.html", user=user, stats=stats)

    @app.route("/restaurant/donate", methods=["GET", "POST"])
    @login_required
    def restaurant_donate():
        # Fetch the current logged-in user
        user = User.query.get(session["user_id"])
        
        # Verify role, only restaurant users can donate food
        if not user or user.role != "restaurant":
            return redirect(url_for("home"))
            
        if request.method == "POST":
            # Read form data
            food_name = request.form.get("food_name")
            quantity = request.form.get("quantity")
            food_type = request.form.get("food_type")
            expiry_time_str = request.form.get("expiry_time")
            description = request.form.get("description")
            
            # Validation
            if not food_name or not quantity or not expiry_time_str:
                return render_template("donate_food.html", error="Please provide food name, quantity, and expiry time.", user=user)
                
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return render_template("donate_food.html", error="Quantity must be greater than 0.", user=user)
            except ValueError:
                return render_template("donate_food.html", error="Please enter a valid number for quantity.", user=user)
                
            try:
                # Parse HTML5 datetime-local format (YYYY-MM-DDTHH:MM)
                expiry_time = datetime.strptime(expiry_time_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                return render_template("donate_food.html", error="Invalid expiry time format.", user=user)
                
            # If a food type was provided, we can prepend it to the description
            if food_type:
                description = f"[{food_type}] {description if description else ''}".strip()
                
            # Create a FoodDonation object
            new_donation = FoodDonation(
                food_name=food_name,
                quantity=quantity,
                expiry_time=expiry_time,
                description=description,
                restaurant_id=user.id
            )
            
            # Save it into SQLite and commit the transaction
            db.session.add(new_donation)
            db.session.commit()
            
            # Redirect to Restaurant Dashboard after successful donation
            return redirect(url_for("restaurant_dashboard"))
            
        # On GET request, render the donation form
        return render_template("donate_food.html", user=user)

    @app.route("/restaurant/my-donations")
    @login_required
    def restaurant_my_donations():
        # Fetch the current logged-in user
        user = User.query.get(session["user_id"])
        
        # Verify role, only restaurant users can view this page
        if not user or user.role != "restaurant":
            return redirect(url_for("home"))
            
        # Fetch donations belonging to the logged-in restaurant
        # Best practice: use filter_by for exact matches and order by ID or date
        donations = FoodDonation.query.filter_by(restaurant_id=user.id).order_by(FoodDonation.id.desc()).all()
        
        # Render the template and pass the donations list
        return render_template("my_donations.html", user=user, donations=donations)

    @app.route("/restaurant/donation/<int:donation_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_restaurant_donation(donation_id):
        # Fetch the current logged-in user
        user = User.query.get(session["user_id"])
        
        # Verify role, only restaurant users can edit
        if not user or user.role != "restaurant":
            return redirect(url_for("home"))
            
        # Fetch the donation using get_or_404
        donation = FoodDonation.query.get_or_404(donation_id)
        
        # Verify ownership: only the owner can edit their own donation
        if donation.restaurant_id != session["user_id"]:
            return redirect(url_for("restaurant_my_donations"))
            
        if request.method == "POST":
            # Read form data
            food_name = request.form.get("food_name")
            quantity = request.form.get("quantity")
            expiry_time_str = request.form.get("expiry_time")
            description = request.form.get("description")
            
            # Validation
            if not food_name or not quantity or not expiry_time_str:
                return render_template("edit_donation.html", donation=donation, user=user, error="Please provide food name, quantity, and expiry time.")
                
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return render_template("edit_donation.html", donation=donation, user=user, error="Quantity must be greater than 0.")
            except ValueError:
                return render_template("edit_donation.html", donation=donation, user=user, error="Please enter a valid number for quantity.")
                
            try:
                # Parse HTML5 datetime-local format (YYYY-MM-DDTHH:MM)
                expiry_time = datetime.strptime(expiry_time_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                return render_template("edit_donation.html", donation=donation, user=user, error="Invalid expiry time format.")
                
            # Update the existing object fields
            donation.food_name = food_name
            donation.quantity = quantity
            donation.expiry_time = expiry_time
            if description is not None:
                donation.description = description
            
            # Save using db.session.commit() only
            db.session.commit()
            
            # Redirect back to my_donations
            return redirect(url_for("restaurant_my_donations"))
            
        # On GET request, render the edit form with the pre-filled donation
        return render_template("edit_donation.html", donation=donation, user=user)

    @app.route("/restaurant/donation/<int:donation_id>/delete", methods=["POST"])
    @login_required
    def delete_restaurant_donation(donation_id):
        # Fetch the current logged-in user
        user = User.query.get(session["user_id"])
        
        # Verify role, only restaurant users can delete
        if not user or user.role != "restaurant":
            return redirect(url_for("home"))
            
        # Fetch the donation using get_or_404
        donation = FoodDonation.query.get_or_404(donation_id)
        
        # Verify ownership: only the owner can delete their own donation
        if donation.restaurant_id != session["user_id"]:
            return redirect(url_for("restaurant_my_donations"))
            
        # Delete the object from the database and commit
        db.session.delete(donation)
        db.session.commit()
        
        # Redirect back to my_donations
        return redirect(url_for("restaurant_my_donations"))

    @app.route("/ngo/dashboard")
    @login_required
    def ngo_dashboard():
        user = User.query.get(session["user_id"])
        
        if not user or user.role != "ngo":
            return redirect(url_for("home"))
            
        available_donations = FoodDonation.query.filter_by(status="available").count()
        my_claims = FoodDonation.query.filter_by(ngo_id=user.id, status="claimed").count()
        picked_up = FoodDonation.query.filter_by(ngo_id=user.id, status="picked_up").count()
        
        stats = {
            "available": available_donations,
            "my_claims": my_claims,
            "picked_up": picked_up
        }
            
        return render_template("ngo_dashboard.html", user=user, stats=stats)

    @app.route("/ngo/donations", methods=["GET"])
    @login_required
    def ngo_donations():
        user = User.query.get(session["user_id"])
        
        # Verify role, only ngo users can view available donations
        if not user or user.role != "ngo":
            return redirect(url_for("home"))
            
        # Fetch only available donations, ordered by newest first
        donations = FoodDonation.query.filter_by(status="available").order_by(FoodDonation.id.desc()).all()
        
        return render_template("ngo_donations.html", user=user, donations=donations)

    @app.route("/ngo/donation/<int:donation_id>/claim", methods=["POST"])
    @login_required
    def ngo_claim_donation(donation_id):
        user = User.query.get(session["user_id"])
        
        # Verify role, only ngo users can claim
        if not user or user.role != "ngo":
            return redirect(url_for("home"))
            
        # Ensure the donation exists
        donation = FoodDonation.query.get_or_404(donation_id)
        
        # Atomically update the donation if it is still available
        updated_rows = FoodDonation.query.filter_by(
            id=donation_id, 
            status="available"
        ).update({"status": "claimed", "ngo_id": user.id})
        
        if updated_rows == 1:
            db.session.commit()
            flash("You have successfully claimed the donation!", "success")
        else:
            db.session.rollback()
            flash("Sorry, this donation has already been claimed or is unavailable.", "danger")
            
        return redirect(url_for("ngo_donations"))

    @app.route("/ngo/my-claims", methods=["GET"])
    @login_required
    def ngo_my_claims():
        user = User.query.get(session["user_id"])
        
        # Verify role, only ngo users can view claims
        if not user or user.role != "ngo":
            return redirect(url_for("home"))
            
        # Fetch claims made by the current NGO, newest first
        claims = FoodDonation.query.filter_by(ngo_id=user.id).order_by(FoodDonation.id.desc()).all()
        
        return render_template("ngo_my_claims.html", user=user, claims=claims)

    @app.route("/ngo/donation/<int:donation_id>/pickup", methods=["POST"])
    @login_required
    def ngo_pickup_donation(donation_id):
        user = User.query.get(session["user_id"])
        
        # Verify role, only ngo users can mark as picked up
        if not user or user.role != "ngo":
            return redirect(url_for("home"))
            
        # Secure conditional update
        # Ensures donation belongs to the current NGO and is in 'claimed' status
        updated_rows = FoodDonation.query.filter_by(
            id=donation_id,
            status="claimed",
            ngo_id=user.id
        ).update({"status": "picked_up"})
        
        if updated_rows == 1:
            db.session.commit()
            flash("Donation marked as picked up successfully.", "success")
        else:
            db.session.rollback()
            flash("This donation cannot be marked as picked up.", "danger")
            
        return redirect(url_for("ngo_my_claims"))

    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        user = User.query.get(session["user_id"])
        
        if not user or user.role != "admin":
            return redirect(url_for("home"))
            
        return render_template("admin_dashboard.html", user=user)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()