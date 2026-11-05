"""Generates 3 unique API keys, one per consumer, saved to api_keys.json.
api_keys.json is in .gitignore - NEVER commit it. Share each key privately
(e.g. direct message) with only its own tester."""
import json
import secrets

CONSUMERS = ["consumer_1", "consumer_2", "consumer_3"]

keys = {name: secrets.token_urlsafe(32) for name in CONSUMERS}
with open("api_keys.json", "w") as f:
    json.dump(keys, f, indent=2)

print("Generated api_keys.json. Send each key privately to its consumer:")
for name, key in keys.items():
    print(f"  {name}: {key}")
