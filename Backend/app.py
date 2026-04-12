from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, find_user_by_username, create_user, find_user_by_email, create_oauth_user
import os
import psycopg2
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")

CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://127.0.0.1:5500"])

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

with app.app_context():
    init_db()


#Route for registering a user 
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    try:
        user_id = create_user(username, email, generate_password_hash(password))
        return jsonify({"message": "Account created successfully", "user_id": user_id}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Username or email already exists"}), 409
    except Exception as e:
        return jsonify({"error": "Server error during registration"}), 500


#Route for user login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = find_user_by_username(username)

    if not user or not check_password_hash(user[2], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user[0]
    session["username"] = user[1]
    return jsonify({"message": f"Welcome back, {user[1]}!", "username": user[1]}), 200


# Route for user loggin out
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# Route for the dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401
    return jsonify({"message": f"Hello, {session['username']}!"}), 200

# Route for checking if user is logged in
@app.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"loggedIn": False}), 200
    return jsonify({"loggedIn": True, "username": session["username"]}), 200

# Route for redirecting user to google Oauth
@app.route("/auth/google")
def google_login():
    redirect_uri = "http://127.0.0.1:5000/auth/callback"
    return google.authorize_redirect(redirect_uri)

# Route for redirecting google back to EyeSell
@app.route("/auth/callback")
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        return jsonify({"error": "OAuth failed, no user info returned"}), 400

    email = user_info["email"]
    name  = user_info.get("name", email.split("@")[0])

    # Find or create the user
    user = find_user_by_email(email)
    if not user:
        user_id = create_oauth_user(name, email)
        username = name
    else:
        user_id  = user[0]
        username = user[1]

    session["user_id"] = user_id
    session["username"] = username

    # Redirects back to frontend
    return redirect("http://127.0.0.1:5500/frontend/index.html")



if __name__ == "__main__":
    app.run(debug=True)


