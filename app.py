from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from transformers import pipeline
import stripe
import os

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # replace with a strong key in production
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User database model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    uses = db.Column(db.Integer, default=0)
    subscribed = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database if it doesn't exist
if not os.path.exists('users.db'):
    with app.app_context():
        db.create_all()

# Load the summarization model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Serve your frontend HTML
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Signup endpoint
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

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials."}), 401

    login_user(user)
    return jsonify({"message": "Logged in successfully."})

# Logout endpoint
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."})

# Summarization endpoint with usage limits
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

    summary_result = summarizer(text, max_length=150, min_length=40, do_sample=False)
    summary = summary_result[0]['summary_text']

    user.uses += 1
    db.session.commit()

    return jsonify({"summary": summary})

# Stripe checkout endpoint
@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'AI Summarizer Subscription',
                    },
                    'unit_amount': 500,  # $5.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )
        return jsonify({'checkout_url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500

# Success endpoint: mark user as subscribed
@app.route('/success')
def success():
    user = current_user
    if user.is_authenticated:
        user.subscribed = True
        db.session.commit()
    return "<h2>Payment successful! You are now subscribed.</h2>"

# Cancel endpoint
@app.route('/cancel')
def cancel():
    return "<h2>Payment canceled. Please try again.</h2>"

if __name__ == '__main__':
    app.run(debug=True)
