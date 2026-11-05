# Task 2 - API keys (X-API-Key)
```
pip install -r requirements.txt
python generate_keys.py      # creates api_keys.json (git-ignored, do not commit)
python app.py                # http://127.0.0.1:5001
./test_curl.sh <KEY>         # each tester runs this with their own key
```
Manual cURL:
```
curl -X POST http://127.0.0.1:5001/process -H "Content-Type: application/json" \
     -H "X-API-Key: <KEY>" -d '{"text":"hello"}'
```
- Valid key -> 200 with uppercase text
- Missing key -> 401, invalid key -> 403

Keys are shared privately with 3 testers (never committed or shown in public screenshots).
Demo video: (add file or link here)
