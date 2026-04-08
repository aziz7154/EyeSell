# EyeSell
### Smart Pricing. Easy Selling.

EyeSell is an AI-powered product listing assistant that turns a photo into a ready-to-post resale listing. Upload an image, and EyeSell identifies the product, pulls real-time price data from platforms like eBay, Craigslist, and Facebook Marketplace, and generates a complete listing with title, description, tags, and price range — all in seconds.

Built for CEG 7370 – Distributed Computing at Wright State University.

**Team:** David Tincher, Aziz Saleh, Jake Hamblin

---

## Features

- Image-based product identification — upload a photo or use your camera
- Reverse image search via Google Custom Search API
- Real-time price aggregation from eBay, Craigslist, and Facebook Marketplace
- Auto-generated listings with title, description, tags, and price range
- Cloud-deployed on AWS EC2 with Nginx reverse proxy and SSL via Certbot
- PostgreSQL for user accounts and saved listings

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Django REST Framework |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL |
| Cloud | AWS EC2, Nginx, Certbot (SSL) |
| AI / Search | Google Custom Search JSON API |
| Storage | Local file storage (S3 optional) |
| Version Control | GitHub |

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/aziz7154/EyeSell.git
cd EyeSell

# Create and activate virtual environment
py -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=eyesell_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
```

## Project Structure

```
EyeSell/
├── eyesell_backend/        # Django project settings
├── api/                    # Core app (views, models, serializers)
├── static/                 # Frontend HTML/CSS/JS
├── media/                  # Uploaded images
├── requirements.txt
├── .env                    # Not committed
├── .gitignore
└── README.md
```

---
