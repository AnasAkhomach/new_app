import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_api_call_with_retry(url, headers, data, max_retries=3, backoff_factor=1):
    """
    Makes an API call with retry logic for handling transient failures.
    
    Args:
        url (str): The URL of the API endpoint.
        headers (dict): Headers to be sent with the request.
        data (dict): The JSON payload for the request.
        max_retries (int): Maximum number of retries before giving up.
        backoff_factor (float): Factor by which to multiply the delay between each retry.
        
    Returns:
        requests.Response: The response object from the requests library.
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Will raise an HTTPError for 4XX/5XX responses
            return response
        except requests.exceptions.HTTPError as e:
            # Log HTTP errors (e.g., 404, 500) but do not retry
            logger.error(f"HTTPError encountered: {e}. No retry.")
            raise
        except requests.exceptions.RequestException as e:
            # Log other errors (e.g., connection issues) and retry
            logger.warning(f"RequestException encountered: {e}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                sleep_time = backoff_factor * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error("Max retries reached. Giving up.")
                raise
    raise Exception("API call failed after maximum retries.")
