#!/bin/bash
# Needs: python app.py running on port 5002. Uses python3 to pull the token from JSON.
B=http://127.0.0.1:5002
J="Content-Type: application/json"
tok() { python3 -c "import sys,json;print(json.load(sys.stdin)['token'])"; }

echo "=== AUTHENTICATION ==="
echo "-- No token -> 401"
curl -s $B/employees; echo
echo "-- Wrong password -> 401"
curl -s -X POST $B/login -H "$J" -d '{"username":"admin","password":"wrong"}'; echo

ADMIN=$(curl -s -X POST $B/login -H "$J" -d '{"username":"admin","password":"admin123"}' | tok)
EMP=$(curl -s -X POST $B/login -H "$J" -d '{"username":"employee","password":"emp123"}' | tok)

echo; echo "=== AUTHORIZATION ==="
echo "-- Employee views -> 200"
curl -s $B/employees -H "Authorization: Bearer $EMP"; echo
echo "-- Employee tries to add -> 403"
curl -s -X POST $B/employees -H "$J" -H "Authorization: Bearer $EMP" -d '{"name":"Hacker","position":"X","salary":1}'; echo
echo "-- Employee tries to delete -> 403"
curl -s -X DELETE $B/employees/1 -H "Authorization: Bearer $EMP"; echo

echo; echo "=== ADMIN ==="
echo "-- Admin adds -> 201"
curl -s -X POST $B/employees -H "$J" -H "Authorization: Bearer $ADMIN" -d '{"name":"Omar","position":"Tester","salary":90000}'; echo
echo "-- Admin updates -> 200"
curl -s -X PUT $B/employees/1 -H "$J" -H "Authorization: Bearer $ADMIN" -d '{"name":"Ali Khan","position":"Senior Developer","salary":150000}'; echo
echo "-- Admin deletes -> 200"
curl -s -X DELETE $B/employees/2 -H "Authorization: Bearer $ADMIN"; echo
