# Task 3 - Authentication & Authorization (JWT)
```
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5002
./test_curl.sh       # runs the full demo
```
Demo users (classroom only): admin / admin123 (admin), employee / emp123 (employee). Passwords are stored hashed.

| Endpoint | employee | admin |
|---|---|---|
| POST /login | yes | yes |
| GET /employees, /employees/<id> | yes | yes |
| POST / PUT / DELETE /employees | 403 | yes |

- Authentication = who are you? No/invalid token or bad login -> **401**
- Authorization = what may you do? Valid user, wrong role -> **403**

Demo video: (add file or link here)
