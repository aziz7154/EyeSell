import requests
import base64
import os
from dotenv import load_dotenv

# TODO remove as likely not necessary
load_dotenv()

def get_ebay_token() -> str:
    """Get an eBay token from environment credentials

    Returns:
        A string containing the access token
    """

    # Set credentials
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    # Encode credentials
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # URL to send authorization request to
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    # Set headers
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Set scope
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    # Send request
    response = requests.post(url, headers=headers, data=data)

    # Get data
    token_data = response.json()

    # Return access token
    return token_data["access_token"]

def search_ebay_api(token: str, product_name: str) -> dict:
    """Raw search eBay Search API for product

    Args:
        token: A token to the eBay API (obtained through get_ebay_token())
        product_name: The name of the product to search for

    Returns:
        A dictionary of the raw API return
    """

    # URL to send request to
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
    }

    # Look for product name and top 10 results
    params = {
        "q": product_name,
        "limit": 10
    }

    # Send request to API and fetch reply
    res = requests.get(url, headers=headers, params=params)

    # Convert API reply to JSON
    data = res.json()

    # Return the data
    return data

def get_ebay(token: str, product_name: str) -> dict:
    """Search eBay Search API for product 

    Args:
        token: A token to the eBay API (obtained through get_ebay_token())
        product_name: The name of the product to search for

    Returns:
        A dictionary containing the title, price, condition, and categories of top 10 eBay
        browse API returns
    """

    # Get raw eBay API search
    results = search_ebay_api(token, product_name)

    # Key words to filter by (ignore short words like a and the
    key_words = [w.lower() for w in product_name.split() if len(w) > 3]

    # Set dictionary of items
    items = {}
    count = 1

    # Loop through each item
    for item in results.get('itemSummaries', []):
        title_lower = item['title'].lower()

        # Skip listings that don't contain any keyword from the product name
        if key_words and not any(w in title_lower for w in key_words):
            continue

        # Make item a dictionary
        items[count] = {}

        # Set attributes
        items[count]['title'] = item['title']
        items[count]['price'] = item['price']['value'] + " " + item['price']['currency']
        items[count]['condition'] = item.get('condition', 'Not specified')
        items[count]['categories'] = []
        items[count]['images'] = []

        # Add main image
        if 'image' in item:
            items[count]['images'].append(item["image"]["imageUrl"])
            items[count]['image_url'] = item["image"]["imageUrl"]

        # Loop through additional images
        for img in item.get('additionalImages', []):
            items[count]['images'].append(img['imageUrl'])

        # Set each category 
        for category in item.get('categories', []):
            items[count]['categories'].append(category['categoryName'])

        count += 1

    return items