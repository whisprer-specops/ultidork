from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/api/test')
def test_proxy():
    proxy = request.args.get("ip")
    if not proxy:
        return "Missing IP", 400

    test_url = "http://httpbin.org/ip"
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        r = requests.get(test_url, proxies=proxies, timeout=5)
        if r.status_code == 200:
            return "OK", 200
        else:
            return "FAIL", 502
    except:
        return "FAIL", 504

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
