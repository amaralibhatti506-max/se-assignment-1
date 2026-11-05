import hmac
import json
import os
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)
KEYS_FILE = os.environ.get("KEYS_FILE", "api_keys.json")


def load_keys():
    if not os.path.exists(KEYS_FILE):
        raise SystemExit("api_keys.json missing. Run: python generate_keys.py")
    with open(KEYS_FILE) as f:
        return json.load(f)  # {consumer_name: key}


def find_consumer(supplied):
    """Constant-time comparison; returns consumer name or None."""
    found = None
    for name, key in load_keys().items():
        if hmac.compare_digest(supplied.encode(), key.encode()):
            found = name
    return found


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        supplied = request.headers.get("X-API-Key")
        if not supplied:
            return jsonify({"error": "Missing API key. Send X-API-Key header."}), 401
        consumer = find_consumer(supplied)
        if not consumer:
            return jsonify({"error": "Invalid API key."}), 403
        request.consumer = consumer
        return fn(*args, **kwargs)

    return wrapper


@app.post("/process")
@require_api_key
def process():
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("text"), str):
        return jsonify({"error": "JSON body with string field 'text' required"}), 400
    text = data["text"]
    return jsonify(
        {
            "consumer": request.consumer,
            "original": text,
            "processed": text.upper(),
            "length": len(text),
        }
    )


if __name__ == "__main__":
    load_keys()
    app.run(debug=True, port=5001)
