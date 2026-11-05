#!/bin/bash
# Usage: ./test_curl.sh <API_KEY>   (each tester uses their own key)
URL=http://127.0.0.1:5001/process
KEY="$1"

echo "--- Valid key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -H "X-API-Key: $KEY" -d '{"text":"hello rootsoftware"}'
echo; echo "--- Invalid key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -H "X-API-Key: wrong-key" -d '{"text":"hello"}'
echo; echo "--- Missing key ---"
curl -s -X POST $URL -H "Content-Type: application/json" -d '{"text":"hello"}'
echo
