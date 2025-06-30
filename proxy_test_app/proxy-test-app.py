# proxy-test-app.py
from flask import Flask, jsonify, request
import time
import ipaddress # To validate IP addresses

app = Flask(__name__)

# Helper to get the actual client IP (remote address)
def get_client_ip(req):
    """
    Attempts to get the real client IP address,
    considering potential proxies that add X-Forwarded-For or similar headers.
    """
    # Check for common headers set by proxies
    x_forwarded_for = req.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For can be a comma-separated list. The client's IP is usually the first one.
        ips = [ip.strip() for ip in x_forwarded_for.split(',')]
        # Filter out private IPs if possible, or just take the first public one
        for ip_str in ips:
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                # If it's a public IP, assume it's the client's.
                # This is a simplification; a truly robust check is harder.
                if not ip_obj.is_private:
                    return ip_str
            except ValueError:
                continue # Not a valid IP
        # Fallback to the first IP even if private/invalid for now
        return ips[0] if ips else req.remote_addr
    
    # Fallback to standard remote address if no X-Forwarded-For
    return req.remote_addr

# Helper to determine anonymity level
def determine_anonymity(req, proxy_ip):
    """
    Determines proxy anonymity based on headers and perceived IP.
    """
    # Get potentially revealing headers
    via_header = req.headers.get('Via')
    x_forwarded_for = req.headers.get('X-Forwarded-For')
    
    # If the perceived client IP is different from the direct connection IP,
    # and especially if X-Forwarded-For or Via headers are present and reveal
    # the original client's IP, it's transparent or anonymous.
    
    # Direct client IP (the one connecting to this server)
    connecting_ip = req.remote_addr

    if via_header or (x_forwarded_for and x_forwarded_for != connecting_ip):
        # If Via header is present or X-Forwarded-For is present and
        # reveals something other than the direct connecting IP, it's transparent.
        # This implies your actual IP is likely passed along.
        return "transparent"
    
    # If connecting_ip is different from the perceived proxy_ip (from the URL test),
    # but no revealing headers are passed, it's generally considered anonymous.
    # The proxy changed your IP but didn't explicitly say so.
    if proxy_ip and connecting_ip != proxy_ip: # This requires comparing with the proxy's IP in the test request
        return "anonymous"
    
    # If only the proxy's IP is seen and no revealing headers, it's elite.
    # This is a more challenging state to detect purely from the server side without
    # additional information about the client's original IP.
    # For a simple test, if no revealing headers are present, we assume elite or high anonymity.
    # The distinction between 'anonymous' and 'elite' often comes from whether the proxy
    # stripped *all* identifying headers, including X-Forwarded-For and Remote-Addr spoofing.
    # For this endpoint, if no XFF/Via are present, it's at least anonymous.
    return "elite" # Assuming no revealing headers means elite/highly anonymous

# Helper to simulate speed (this is the trickiest part for a simple endpoint)
def determine_speed(latency_ms):
    """
    Determines proxy speed based on measured latency.
    These are example thresholds; adjust as needed.
    """
    if latency_ms < 200:
        return "fast"
    elif latency_ms < 800:
        return "medium"
    else:
        return "slow"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy_test_endpoint(path):
    """
    A simple endpoint that returns detailed information about the incoming request,
    including inferred proxy attributes.
    """
    # Capture start time as early as possible
    start_time = time.time()

    # Get the IP address that directly connected to this Flask app
    connecting_ip = request.remote_addr

    # Attempt to derive the 'client' IP, which might be the true client or another proxy hop
    client_ip_from_headers = get_client_ip(request)

    # Calculate latency (approximate - from request start to this point in code)
    # The true network latency is measured on the client (UltiDork) side.
    # This server-side 'latency' mostly indicates processing time on the server.
    # For speed, rely more on the client-side measurement (UltiDork's ProxyTester).
    server_processing_latency_ms = (time.time() - start_time) * 1000

    # Determine anonymity level based on observed headers and connecting IP
    # We pass 'connecting_ip' as the 'proxy_ip' for anonymity determination
    # because this is the IP that *this server* directly sees from the proxy.
    anonymity_level = determine_anonymity(request, connecting_ip)
    
    # For 'speed', it's best determined client-side. We can only give a default or
    # return the server processing latency if needed, but it won't reflect network speed accurately.
    # Let's provide a placeholder for speed that you can map on client-side with actual RTT.
    # We will use the client-side calculated latency in ProxyTester for speed.
    
    response_data = {
        "status": "success",
        "message": "Proxy test endpoint is active and providing details.",
        "received_path": f"/{path}",
        "method": request.method,
        "headers_received": dict(request.headers), # Headers the endpoint saw
        "connecting_ip": connecting_ip,          # IP that connected to this server
        "client_ip_from_headers": client_ip_from_headers, # Inferred client IP
        "anonymity_level": anonymity_level,      # Inferred anonymity
        "server_processing_latency_ms": server_processing_latency_ms, # Time on server side
        "args": request.args,
        "form": request.form,
        "json_body": request.json if request.is_json else None
        # IMPORTANT: 'latency_ms' and 'speed' should primarily be calculated on the client side (ProxyTester)
        # However, we can add a 'speed_hint' here based on server processing or a fixed value.
        # "speed_hint": determine_speed(server_processing_latency_ms) # If you want to guess speed server-side
    }
    return jsonify(response_data)

# Remove the if __name__ == '__main__': block completely when using Gunicorn.
# Gunicorn loads the 'app' object directly, so this block is not needed and can cause issues if empty/malformed.
