import requests

def send_tarot_reading(generated_cards: list, interpretation: str, language: str, intent: str, api_url: str) -> dict:
    """
    Sends a GET request to the specified API endpoint with query parameters.

    Args:
        generated_cards (list): List of generated tarot cards.
        interpretation (str): Interpretation of the reading.
        language (str): Language of the response.
        intent (str): Intent of the user's query.
        api_url (str): The API endpoint URL.

    Returns:
        dict: Response from the API.
    """
    try:
        # Prepare query parameters
        params = {
            "generated_cards": ",".join(generated_cards),
            "interpretation": interpretation,
            "language": language,
            "intent": intent
        }

        # Send GET request
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        # Return JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending tarot reading: {e}")
        return {"error": str(e)}
