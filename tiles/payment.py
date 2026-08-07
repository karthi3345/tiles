"""
Razorpay client wrapper — thin singleton around the razorpay Python SDK.

Reads credentials from env (set via Django settings / .env).
Never expose the secret to the browser — only the key_id is safe for frontend.
"""
import os
import razorpay


_client = None


def get_razorpay_client():
    """Return a lazily-initialised Razorpay client (singleton)."""
    global _client
    if _client is None:
        key_id = os.getenv('RAZORPAY_KEY_ID', '')
        key_secret = os.getenv('RAZORPAY_KEY_SECRET', '')
        if not key_id or not key_secret:
            raise RuntimeError(
                'Razorpay credentials not configured. '
                'Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in .env'
            )
        _client = razorpay.Client(auth=(key_id, key_secret))
    return _client


def create_razorpay_order(amount_paise, currency='INR', receipt=None):
    """
    Create a Razorpay order on the server.

    Args:
        amount_paise: int — amount in paise (e.g. ₹100 = 10000)
        currency: str — currency code (default INR)
        receipt: str — optional receipt / order reference

    Returns:
        dict — Razorpay order dict with id, amount, currency, status
    """
    client = get_razorpay_client()
    data = {
        'amount': int(amount_paise),
        'currency': currency,
    }
    if receipt:
        data['receipt'] = receipt
    return client.order.create(data=data)


def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify the payment signature returned by Razorpay Checkout.

    Uses HMAC SHA256 — the Razorpay standard verification flow.
    Raises razorpay.errors.SignatureVerificationError on mismatch.

    Returns:
        True on success, raises on failure.
    """
    client = get_razorpay_client()
    client.utility.verify_payment_signature({
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature,
    })
    return True
