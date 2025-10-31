from flask import Flask, request, send_from_directory, jsonify
from markupsafe import escape
import os

app = Flask(__name__, static_folder='frontend/build', static_url_path='')

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

@app.route('/')
def serve_react_app():
    """Serve the React application"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files from React build"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # For client-side routing, return index.html for unknown routes
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)