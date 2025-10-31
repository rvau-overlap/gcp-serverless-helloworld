from flask import Flask, request, send_from_directory, jsonify
from markupsafe import escape
import os

# Disable Flask's default static file serving
app = Flask(__name__, static_folder=None)

@app.route('/api/userinfo')
def get_user_info():
    """API endpoint to return user information"""
    user_agent = escape(request.headers.get('User-Agent', 'Unknown'))
    
    # Get the real IP address (considering proxy headers)
    # Note: In Cloud Run, X-Forwarded-For is set by the platform and can be trusted
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ip_address = escape(forwarded_for.split(',')[0].strip())
    else:
        ip_address = escape(request.remote_addr or 'Unknown')
    
    return jsonify({
        'userAgent': str(user_agent),
        'ipAddress': str(ip_address)
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """Serve the React application and its static assets"""
    build_folder = os.path.join(os.path.dirname(__file__), 'frontend', 'build')
    
    # If path is empty or root, serve index.html
    if path == '':
        return send_from_directory(build_folder, 'index.html')
    
    # send_from_directory has built-in protection against path traversal
    # Try to serve the requested file
    try:
        return send_from_directory(build_folder, path)
    except:
        # For client-side routing, return index.html for unknown routes
        return send_from_directory(build_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)