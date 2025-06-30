# proxy-test-app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy_test_endpoint(path):
    """
    A simple endpoint that returns basic information to acknowledge the request.
    This keeps the response small and fast.
    """
    response_data = {
        "status": "success",
        "message": "Proxy test endpoint is active.",
        "received_path": f"/{path}",
        "method": request.method,
        "headers": dict(request.headers),
        "args": request.args,
        "form": request.form,
        "json": request.json if request.is_json else None
    }
    return jsonify(response_data)

# Remove the if __name__ == '__main__': block completely when using Gunicorn.
# Gunicorn loads the 'app' object directly, so this block is not needed and can cause issues if empty/malformed.
