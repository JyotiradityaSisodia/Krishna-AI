import requests

res = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"message": "wake mode"}
)

print(res.json())
