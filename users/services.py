import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError

STRIPE_BASE_URL = "https://stripe.com"


def _get_headers():
    return {
        "Authorization": f"Bearer {settings.STRIPE_API_KEY}"
    }


def _handle_stripe_request(method, url, data=None):
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_get_headers(),
            data=data,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        try:
            error_message = exc.response.json().get("error", {}).get("message", str(exc))
        except ValueError:
            error_message = str(exc)
        raise ValidationError({"stripe_error": error_message})
    except requests.RequestException as exc:
        raise ValidationError({"stripe_connection_error": f"Ошибка соединения со Stripe: {str(exc)}"})


def create_stripe_product(name):
    url = f"{STRIPE_BASE_URL}/products"
    result = _handle_stripe_request("POST", url, data={"name": name})
    return result.get("id")


def create_stripe_price(amount, product_id):
    url = f"{STRIPE_BASE_URL}/prices"
    data = {
        "currency": "rub",
        "unit_amount": int(amount * 100),
        "product": product_id,
    }
    result = _handle_stripe_request("POST", url, data=data)
    return result.get("id")


def create_stripe_session(price_id):
    url = f"{STRIPE_BASE_URL}/checkout/sessions"
    data = {
        "success_url": "http://127.0.0",
        "line_items[price]": price_id,
        "line_items[quantity]": 1,
        "mode": "payment",
    }
    result = _handle_stripe_request("POST", url, data=data)
    return result.get("id"), result.get("url")


def retrieve_stripe_session(session_id):
    url = f"{STRIPE_BASE_URL}/checkout/sessions/{session_id}"
    return _handle_stripe_request("GET", url)
