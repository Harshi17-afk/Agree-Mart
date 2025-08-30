from flask import render_template, request, redirect, url_for, flash, session, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random
import string
from datetime import datetime, timedelta
from config import Config
from agrimart.sms_service import sms_service
# Firebase removed

# Load environment variables
load_dotenv()

users = []
user_sessions = {}
otp_storage = {}

def init_app(app):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/home")
    def home():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            login_type = request.form.get("login_type")
            identifier = request.form.get("identifier")
            
            if not identifier:
                flash("Please enter your email or phone number", "error")
                return render_template("login.html")
            
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=Config.OTP_LENGTH))
            otp_storage[identifier] = {
                'otp': otp,
                'timestamp': datetime.now(),
                'attempts': 0
            }
            
            if login_type == "email":
                # Send OTP via email
                if send_otp_email(identifier, otp):
                    session['pending_login'] = identifier
                    session['login_type'] = 'email'
                    flash(f"OTP sent to {identifier}", "success")
                    return redirect(url_for("verify_otp"))
                else:
                    # Development fallback: show OTP so user can proceed
                    session['pending_login'] = identifier
                    session['login_type'] = 'email'
                    flash("Email sending failed. Using development fallback.", "warning")
                    flash(f"Your OTP (dev): {otp}", "success")
                    return redirect(url_for("verify_otp"))
            else:
                # Send OTP via SMS using SMS service
                if sms_service.send_otp_sms(identifier, otp):
                    session['pending_login'] = identifier
                    session['login_type'] = 'phone'
                    flash(f"OTP sent to {identifier}", "success")
                    return redirect(url_for("verify_otp"))
                else:
                    flash("Failed to send OTP. Please try again.", "error")
            
        return render_template("login.html")

    @app.route("/verify_otp", methods=["GET", "POST"])
    def verify_otp():
        if 'pending_login' not in session:
            return redirect(url_for("login"))
        
        if request.method == "POST":
            otp = request.form.get("otp")
            identifier = session['pending_login']
            
            if verify_otp_code(identifier, otp):
                # OTP verified, create or get user
                user = get_or_create_user(identifier, session.get('login_type'))
                session['user_id'] = user['id']
                session['user_email'] = user.get('email')
                session['user_phone'] = user.get('phone')
                session.pop('pending_login', None)
                session.pop('login_type', None)
                
                flash("Login successful! Welcome back!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid OTP. Please try again.", "error")
        
        return render_template("verify_otp.html")

    @app.route("/dashboard")
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for("login"))
        
        user = get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for("login"))
        
        return render_template("dashboard.html", user=user)

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out successfully", "success")
        return redirect(url_for("login"))

    @app.route("/profile")
    def profile():
        if 'user_id' not in session:
            return redirect(url_for("login"))
        
        user = get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for("login"))
        
        return render_template("profile.html", user=user)

    @app.route("/update_profile", methods=["POST"])
    def update_profile():
        if 'user_id' not in session:
            return redirect(url_for("login"))
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        if not user:
            session.clear()
            return redirect(url_for("login"))
        
        # Update user profile
        user['name'] = request.form.get('name', user['name'])
        user['phone'] = request.form.get('phone', user['phone'])
        user['location'] = request.form.get('location', user.get('location', ''))
        user['farm_type'] = request.form.get('farm_type', user.get('farm_type', ''))
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    @app.route("/add_user", methods=["GET", "POST"])
    def add_user():
        if request.method == "POST":
            farmer_name = request.form["farmer_name"]
            mobile_number = request.form["mobile_number"]
            crop_type = request.form["crop_type"]
            crop_description = request.form["crop_description"]
            
            # Store user data
            user_data = {
                "name": farmer_name,
                "mobile": mobile_number,
                "type": crop_type,
                "description": crop_description
            }
            users.append(user_data)
            
            # Send email
            try:
                send_farmer_email(user_data)
                flash("Farmer added successfully! Email sent.", "success")
            except Exception as e:
                flash(f"Farmer added but email failed: {str(e)}", "warning")
            
            return redirect(url_for("list_users"))
        return render_template("add_user.html")

    @app.route("/users")
    def list_users():
        return render_template("users.html", users=users)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/test_email")
    def test_email():
        """Test email functionality"""
        test_data = {
            "name": "Test Farmer",
            "mobile": "1234567890",
            "type": "Crop",
            "description": "Test email functionality"
        }
        
        result = send_farmer_email(test_data)
        if result:
            return "✅ Test email sent successfully! Check your inbox and console."
        else:
            return "❌ Test email failed! Check console for detailed error messages."

    @app.route("/test_sms")
    def test_sms():
        """Test SMS functionality"""
        test_phone = request.args.get('phone', '1234567890')
        test_otp = '123456'
        
        result = sms_service.send_otp_sms(test_phone, test_otp)
        if result:
            return f"✅ Test SMS sent successfully to {test_phone}! Check console for details."
        else:
            return f"❌ Test SMS failed! Check console for detailed error messages."

    # Firebase routes removed

def send_otp_email(email, otp):
    """Send OTP via email"""
    sender_email = Config.GMAIL_EMAIL
    sender_password = Config.GMAIL_PASSWORD
    
    subject = "Your Agrimart Login OTP"
    body = f"""
    Hello!
    
    Your OTP for Agrimart login is: {otp}
    
    This OTP is valid for 10 minutes.
    If you didn't request this, please ignore this email.
    
    Best regards,
    Agrimart Team
    """
    
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        text = message.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        
        print(f"✅ OTP email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send OTP email: {str(e)}")
        return False



def verify_otp_code(identifier, otp):
    """Verify OTP"""
    if identifier not in otp_storage:
        return False
    
    otp_data = otp_storage[identifier]
    
    # Check if OTP is expired
    if datetime.now() - otp_data['timestamp'] > timedelta(minutes=Config.OTP_EXPIRY_MINUTES):
        del otp_storage[identifier]
        return False
    
    # Check attempts
    if otp_data['attempts'] >= Config.MAX_OTP_ATTEMPTS:
        del otp_storage[identifier]
        return False
    
    otp_data['attempts'] += 1
    
    if otp_data['otp'] == otp:
        del otp_storage[identifier]
        return True
    
    return False

def get_or_create_user(identifier, login_type):
    """Get existing user or create new one"""
    # Check if user exists
    for user in users:
        if user.get('email') == identifier or user.get('phone') == identifier:
            return user
    
    # Create new user
    new_user = {
        'id': len(users) + 1,
        'name': 'New User',
        'email': identifier if login_type == 'email' else None,
        'phone': identifier if login_type == 'phone' else None,
        'created_at': datetime.now().isoformat(),
        'location': '',
        'farm_type': '',
        'is_verified': True
    }
    
    users.append(new_user)
    return new_user

def get_user_by_id(user_id):
    """Get user by ID"""
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

def send_farmer_email(user_data):
    """Send farmer details to mhharshith9@gmail.com"""
    # Your Gmail credentials
    sender_email = "mhharshith9@gmail.com"
    sender_password = os.getenv('GMAIL_PASSWORD', 'Harshith@#123')  # Use environment variable for security
    receiver_email = "mhharshith9@gmail.com"
    
    # Email content
    subject = f"New Farmer Registration - {user_data['name']}"
    
    body = f"""
    New Farmer Registration Details:
    
    Name: {user_data['name']}
    Mobile: {user_data['mobile']}
    Type: {user_data['type']}
    Description: {user_data['description']}
    
    This information was submitted through the Agrimart website.
    """
    
    try:
        print(f"🔐 Attempting to send email to {receiver_email}")
        print(f"📧 Using sender: {sender_email}")
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        print("📡 Connecting to Gmail SMTP...")
        # Connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        print("🔑 Attempting login...")
        server.login(sender_email, sender_password)
        print("✅ Login successful!")
        
        # Send email
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {receiver_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("💡 Solution: Enable 2FA and use App Password instead of regular password")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False