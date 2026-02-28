from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from my app - version 1!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

> Đây là một web server cực kỳ đơn giản, truy cập vào sẽ thấy dòng chữ "Hello from my app - version 1!"

Commit changes.

---

### File 2: `requirements.txt`

Tạo thêm file `requirements.txt` (để Python biết cần cài thư viện gì):
```
flask==3.0.0
