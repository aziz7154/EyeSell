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

    # Set dictionary of items
    items = {}

    # Loop through each item
    for i, item in enumerate(results['itemSummaries'], start=1):
        # Make item a dictionary
        items[i] = {}
        
        # Set attributes
        items[i]['title'] = item['title']
        items[i]['price'] = item['price']['value'] + " " + item['price']['currency']
        items[i]['condition'] = item['condition']
        items[i]['categories'] = []
        items[i]['images'] = []

        # Add main image
        items[i]['images'].append(item["image"]["imageUrl"])

        # Loop through additional images
        for img in item['additionalImages']:
            items[i]['images'].append(img['imageUrl'])
        
        # Set each category
        for category in item['categories']:
            items[i]['categories'].append(category['categoryName'])

    # Return the items
    return items