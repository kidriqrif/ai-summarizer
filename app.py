from flask import render_template, send_from_directory
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fs7p75td'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User database model with usage tracking and subscription flag
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    uses = db.Column(db.Integer, default=0)
    subscribed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize the database if not exist
if not os.path.exists('users.db'):
    with app.app_context():
        db.create_all()

# Load summarization model once (Hugging Face)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Signup API
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(email=email, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully."})

# Login API
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    print(f"Login attempt for: {email}")  # debug
    user = User.query.filter_by(email=email).first()
    if user:
        print("User found")
        if check_password_hash(user.password, password):
            print("Password correct, logging in")
            login_user(user)
            return jsonify({"message": "Logged in successfully."})
    print("Login failed")
    return jsonify({"error": "Invalid credentials."}), 401

# Logout API
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."})

# Summarize API (only for logged in users)
@app.route('/summarize', methods=['POST'])
@login_required
def summarize():
    data = request.json
    text = data.get('text', '')

    if not text.strip():
        return jsonify({"error": "No text provided"}), 400

    free_limit = 5
    user = current_user

    if not user.subscribed and user.uses >= free_limit:
        return jsonify({"error": "Free usage limit reached. Please subscribe to continue."}), 403

    # Summarize text using Hugging Face model
    summary_result = summarizer(text, max_length=150, min_length=40, do_sample=False)
    summary = summary_result[0]['summary_text']

    # Update usage count
    user.uses += 1
    db.session.commit()

    return jsonify({"summary": summary})

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')
if __name__ == '__main__':
    app.run(debug=True)