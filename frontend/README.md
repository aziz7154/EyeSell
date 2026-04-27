# EyeSell
### Smart Pricing. Easy Selling.

EyeSell is an AI-powered product listing assistant that turns a photo into a ready-to-post resale listing. Upload an image, and EyeSell identifies the product using Google Cloud Vision API, pulls real-time price data from platforms like eBay, Craigslist, and Facebook Marketplace, and generates a complete listing with title, description, tags, and price range — all in seconds.

Built for CEG 7370 – Distributed Computing at Wright State University.

**Team:** David Tincher, Aziz Saleh, Jake Hamblin

---

## Features

- Image-based product identification via Google Cloud Vision API
- Real-time price aggregation from eBay, Craigslist, Facebook Marketplace, Amazon, and Etsy
- Auto-generated listings with title, description, tags, and price range
- User accounts and saved listings via PostgreSQL
- Google OAuth login support
- Cloud-deployed on AWS EC2 with Nginx reverse proxy and SSL via Certbot

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask, Flask-CORS, Authlib |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL (psycopg2) |
| Cloud | AWS EC2, Nginx, Certbot (SSL) |
| AI / Vision | Google Cloud Vision API |
| Search / Pricing | Google Custom Search JSON API |
| Auth | Session-based + Google OAuth |
| Version Control | GitHub |

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### Installation

```bash
git clone https://github.com/aziz7154/EyeSell.git
cd EyeSell

py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file inside the `Backend/` folder:

```
SECRET_KEY=your-flask-secret-key
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/eyesell_db
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_VISION_API_KEY=your-vision-api-key
GOOGLE_API_KEY=your-custom-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

### Database Setup

```bash
psql -U postgres -c "CREATE DATABASE eyesell_db;"
```

The users table is created automatically when the Flask server starts.

### Run the Development Server

```bash
cd Backend
python app.py
```

Backend: `http://127.0.0.1:5000`
Frontend: open `frontend/index.html` with Live Server in VS Code (`http://127.0.0.1:5500`)

---

## Project Structure

```
EyeSell/
├── Backend/
│   ├── app.py            # Flask routes and auth
│   └── db.py             # PostgreSQL helpers
├── frontend/
│   ├── api.js            # All API calls, Auth, Store
│   ├── upload.js         # Upload page logic
│   ├── results.js        # Results page rendering
│   ├── generate.js       # Listing generator logic
│   ├── dashboard.js      # Dashboard rendering
│   ├── index.html        # Landing page
│   ├── login.html        # Login / sign up
│   ├── upload.html       # Image upload
│   ├── results.html      # Pricing results
│   ├── generate.html     # Listing generator
│   ├── dashboard.html    # User dashboard
│   └── shared.css        # Shared styles
├── requirements.txt
├── .gitignore
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Create account (username, email, password) |
| POST | `/login` | Authenticate (username + password) |
| POST | `/logout` | End session |
| GET | `/me` | Check session status |
| GET | `/auth/google` | Redirect to Google OAuth |
| GET | `/auth/callback` | Google OAuth callback |
| POST | `/upload` | Upload image, save to disk |
| POST | `/analyze` | Run Google Cloud Vision API |
| POST | `/search` | Fetch pricing via Google Custom Search API |
| POST | `/listings` | Save a listing to database |
| GET | `/listings` | Get all listings for current user |

---

## Frontend Mock Mode

Test the full UI without a running backend:

```js
window.EYESELL_USE_MOCK = true;   // api.js — default, uses fake data
window.EYESELL_USE_MOCK = false;  // switch to real Flask backend
```

---

## License

Academic project — Wright State University, Spring 2026.
