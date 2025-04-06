import requests

with open("backend/test/test.docx", "rb") as f:
    files = {'file': f}
    response = requests.post("http://127.0.0.1:5088/api/interviews/upload", files=files)

print(response.status_code)
print(response.json())