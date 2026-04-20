import re
from io import BytesIO
from typing import BinaryIO
from google.cloud import vision
from google.oauth2 import service_account
from collections import Counter

def identify_product(uploaded_file: BinaryIO) -> str | None:
    """Identify an item from an image using multiple Vision features

    Args:
        uploaded_file: A readable binary file-like object containing the image

    Returns:
        A string (or none) of most likely name from image
    """

    # Get credentials from file
    credentials = service_account.Credentials.from_service_account_file(
        "vision_account.json"
    )

    # Convert credentials to API connection
    client = vision.ImageAnnotatorClient(credentials=credentials)

    # Read image
    content = uploaded_file.read()

    # Convert image to Vision image
    image = vision.Image(content=content)

    # Multiple API requests to identify image
    text_response = client.text_detection(image=image)
    web_response = client.web_detection(image=image)
    logo_response = client.logo_detection(image=image)
    label_response = client.label_detection(image=image)

    # For each response, throw error if API returned one
    for response in (
        text_response,
        web_response,
        logo_response,
        label_response,
    ):
        if response.error.message:
            raise Exception(response.error.message)

    # Get text extracted from image
    extracted_text = (
        # Strip description text
        text_response.text_annotations[0].description.strip()

        # Set if exists
        if text_response.text_annotations
        else ""
    )

    # Get best guesses from image
    best_guesses = [
        guess.label for guess in web_response.web_detection.best_guess_labels
    ]

    # Get web entities from image
    web_entities = [
        entity.description
        for entity in web_response.web_detection.web_entities
        if entity.description and entity.score >= 0.7
    ]

    # Get page titles from image
    page_titles = [
        page.page_title
        for page in web_response.web_detection.pages_with_matching_images[:5]
        if page.page_title
    ]

    # Get logos from image
    logos = [
        logo.description
        for logo in logo_response.logo_annotations
    ]

    # Get labels from image
    labels = [
        label.description
        for label in label_response.label_annotations[:5]
    ]

    # Convert candidates to be ranked by likelihood
    candidates = normalize_candidates(
        extracted_text=extracted_text,
        best_guesses=best_guesses,
        web_entities=web_entities,
        page_titles=page_titles,
        logos=logos,
        labels=labels,
    )

    # Return the ranked candidates
    return choose_best_name({
        "name": candidates[0] if candidates else None,
        "candidates": candidates,
        "text": extracted_text,
        "best_guesses": best_guesses,
        "web_entities": web_entities,
        "page_titles": page_titles,
        "logos": logos,
        "labels": labels,
    })

def normalize_candidates(extracted_text: list[str], best_guesses: list[str], web_entities: list[str], page_titles: list[str], logos: list[str], labels: list[str]) -> list[str]:
    """Normalize candidates from Vision API return

    Args:
        extracted_text: A list of strings containing the extracted text from image
        best_guesses: A list of strings containing the best general guesses from image
        web_entities: A list of strings containing the web entities from image
        page_titles: A list of strings containing the page titles from image
        logos: A list of strings containing the logos from image
        labels: A list of strings containing the labels from image

    Returns:
        A list of normalized items
    """

    # Initialize array
    candidates = []

    # If there is text that was able to be extracted
    if extracted_text:
        # Get lines
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]

        # Connect lines
        if lines:
            candidates.append(" ".join(lines[:2]))

    # If page titles exist, add as possibilities
    candidates.extend(page_titles)

    # If web entites exist, add as possibilities
    candidates.extend(web_entities)

    # If best guesses exist, add as possibilities
    candidates.extend(best_guesses)

    # Add logos to possibilities
    if logos and labels:
        candidates.append(f"{logos[0]} {' '.join(labels[:2])}")

    # Remove duplicates from array
    seen = set()
    ranked = []
    for candidate in candidates:
        normalized = candidate.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ranked.append(candidate)

    # Return the ranked candidates
    return ranked

def clean_text(text: str) -> str:
    """Santize text from Vision API return

    Args:
        text: String to santize

    Returns:
        Santized string
    """

    # Convert text to lower
    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text) 

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Return that text
    return text


def is_garbage(text: str) -> bool:
    """Filter out garbage candidates from Vision API return

    Args:
        text: Text to identifty if garbage

    Returns:
        If the string is garbage
    """

    # If string is empty, return garbage
    if not text:
        return True

    # If string is too small or large, return garbage
    if len(text) < 3 or len(text) > 120:
        return True

    # If string is mostly numbers or symbols, return garbage
    if sum(c.isalpha() for c in text) < len(text) * 0.5:
        return True

    # If string looks weird (no spaces or weird chunks)
    if len(text.split()) == 1 and len(text) > 15:
        return True

    # If no conditions met, return false
    return False


def extract_text_candidates(text_block: str) -> list[str]:
    """Extract likely setups for text blocks

    Args:
        text_block: A string that contains a text block to be split into it's likely candidates

    Returns:
        A list of strings with the likely correct splitting
    """

    # If string is empty, return nothing
    if not text_block:
        return []

    # Go through each text_block line and split and strip
    lines = [line.strip() for line in text_block.splitlines() if line.strip()]

    # Combine first lines
    candidates = []
    if len(lines) >= 2:
        candidates.append(f"{lines[0]} {lines[1]}")

    # Add lines to array
    candidates.extend(lines[:3])

    # Return candidates
    return candidates


def choose_best_name(result: dict) -> str | None:
    """Choose the best name from Vision API result

    Args:
        result: A dictionary of all items

    Returns:
        A string (or nothing) of the most likely name
    """

    # Initialze an array
    candidates = []

    # Text from product (most likely candidate)
    text_candidates = extract_text_candidates(result.get("text", ""))
    candidates.extend(text_candidates)

    # Page titles (highly likely)
    candidates.extend(result.get("page_titles", []))

    # Web entities (brand names, so very likely)
    candidates.extend(result.get("web_entities", []))

    # Best guesses (fail over, extremely general and inaccurate)
    candidates.extend(result.get("best_guesses", []))

    # Filter all candidates
    filtered = []

    # Loop through each candidate
    for c in candidates:
        # Strip
        c = c.strip()

        # Figure out if garbage
        if not is_garbage(c):
            filtered.append(c)

    # If everything was garbage, return none
    if not filtered:
        return None

    # Normalize inputs
    normalized = [clean_text(c) for c in filtered]

    # Get frequency
    counts = Counter(normalized)

    # Pick the most common result
    best_norm = counts.most_common(1)[0][0]

    # Return the cleanest original version of it
    for original in filtered:
        if clean_text(original) == best_norm:
            return original

    # Return most likely name
    return filtered[0]

# def test_identify_product(image_path: str):
#     with open(image_path, "rb") as f:
#         file_like = BytesIO(f.read())

#     return identify_product(file_like)

# Test API response
#print(test_identify_product("testing_product.jpg"))