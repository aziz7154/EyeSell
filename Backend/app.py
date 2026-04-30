from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, find_user_by_username, create_user, find_user_by_email, create_oauth_user, create_listing, get_listings_by_user, init_listings_table, get_connection
from utils.product_identification import identify_product
from utils.ebay import get_ebay_token, get_ebay
import uuid
from pathlib import Path
import os
import psycopg2
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session, redirect, send_from_directory

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_DOMAIN'] = 'eyesell.org'


UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:5500",
    "http://localhost:5501",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:8000",
    "http://100.28.222.144",
    "http://eyesell.org",
    "https://eyesell.org",
])

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
    init_listings_table()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_ebay_results(ebay_items):
    prices = []
    listings = []
    for item in ebay_items.values():
        try:
            price = float(item["price"].split()[0])
            prices.append(price)
            listings.append({
                "title":     item["title"],
                "price":     price,
                "source":    "eBay",
                "image_url": item.get("image_url", None),
                "item_url":  item.get("item_url", None),
            })
        except (ValueError, KeyError):
            continue
    if not prices:
        return {"price_low": 0, "price_high": 0, "sources": [], "listings": []}
    avg = sum(prices) / len(prices)
    return {
        "price_low":  round(min(prices), 2),
        "price_high": round(max(prices), 2),
        "sources": [{"name": "eBay", "avg_price": round(avg, 2), "count": len(prices)}],
        "listings": listings[:4],
    }


def build_tags(product_name, ebay_items):
    tags = set()
    for word in product_name.split():
        if len(word) > 2:
            tags.add(word)
    for item in ebay_items.values():
        for category in item.get("categories", [])[:2]:
            tags.add(category)
    return list(tags)[:8]


@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
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
        print(f"REGISTRATION ERROR: {e}")
        return jsonify({"error": "Server error during registration"}), 500


@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = find_user_by_username(username)

    if not user or not check_password_hash(user[2], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"]  = user[0]
    session["username"] = user[1]
    return jsonify({"message": f"Welcome back, {user[1]}!", "username": user[1]}), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"loggedIn": False}), 200
    return jsonify({"loggedIn": True, "username": session["username"]}), 200


@app.route("/auth/google")
def google_login():
    redirect_uri = "https://eyesell.org/auth/callback"
    return google.authorize_redirect(redirect_uri)


@app.route("/auth/callback")
def google_callback():
    token     = google.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        return jsonify({"error": "OAuth failed, no user info returned"}), 400

    email    = user_info["email"]
    name     = user_info.get("name", email.split("@")[0])
    user     = find_user_by_email(email)

    if not user:
        user_id  = create_oauth_user(name, email)
        username = name
    else:
        user_id  = user[0]
        username = user[1]

    session["user_id"]  = user_id
    session["username"] = username

    return redirect("https://eyesell.org/dashboard.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use JPG, PNG, or WEBP."}), 400

    ext       = file.filename.rsplit(".", 1)[1].lower()
    image_id  = str(uuid.uuid4())
    save_path = UPLOAD_FOLDER / f"{image_id}.{ext}"
    file.save(save_path)

    try:
        with open(save_path, "rb") as f:
            product_name = identify_product(f)
    except Exception as e:
        return jsonify({"error": f"Vision API error: {str(e)}"}), 500

    if not product_name:
        return jsonify({"error": "Could not identify product. Try a clearer photo."}), 422

    try:
        token      = get_ebay_token()
        ebay_items = get_ebay(token, product_name)
        pricing    = normalize_ebay_results(ebay_items)
        tags       = build_tags(product_name, ebay_items)
    except Exception as e:
        return jsonify({"error": f"eBay API error: {str(e)}"}), 500

    return jsonify({
        "image_id":      image_id,
        "image_url": f"https://eyesell.org/uploads/{image_id}.{ext}",
        "product_name":  product_name,
        "product_model": "",
        "confidence":    0.90,
        "tags":          tags,
        "price_low":     pricing["price_low"],
        "price_high":    pricing["price_high"],
        "sources":       pricing["sources"],
        "listings":      pricing["listings"],
    }), 200


@app.route("/listings", methods=["POST"])
def save_listing():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    data = request.get_json()

    try:
        listing_id = create_listing(
            user_id      = session["user_id"],
            image_id     = data.get("image_id", ""),
            product_name = data["product_name"],
            description  = data.get("description", ""),
            tags         = data.get("tags", ""),
            price_low    = float(data["price_low"]),
            price_high   = float(data["price_high"]),
            price_final  = float(data["price_final"]),
        )
        return jsonify({"id": listing_id, "status": "saved"}), 201
    except Exception as e:
        return jsonify({"error": f"Could not save listing: {str(e)}"}), 500


@app.route("/listings", methods=["GET"])
def get_listings():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    try:
        listings    = get_listings_by_user(session["user_id"])
        total_value = sum(l["price_final"] for l in listings)
        return jsonify({
            "listings": listings,
            "stats": {
                "total_listings": len(listings),
                "total_value":    round(total_value, 2),
                "total_searches": len(listings),
            },
        }), 200
    except Exception as e:
        print(f"LISTINGS ERROR: {e}")
        return jsonify({"error": f"Could not fetch listings: {str(e)}"}), 500


@app.route("/listings/<int:listing_id>", methods=["PUT"])
def update_listing(listing_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE listings
            SET product_name=%s, description=%s, tags=%s, price_final=%s
            WHERE id=%s AND user_id=%s
        """, (
            data.get("product_name"),
            data.get("description", ""),
            data.get("tags", ""),
            float(data.get("price_final", 0)),
            listing_id,
            session["user_id"],
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/listings/<int:listing_id>", methods=["DELETE"])
def delete_listing(listing_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(
            "DELETE FROM listings WHERE id=%s AND user_id=%s",
            (listing_id, session["user_id"])
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
