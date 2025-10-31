from flask import Flask, request
from markupsafe import escape
import os

app = Flask(__name__)

@app.route('/')
def hello():
    user_agent = escape(request.headers.get('User-Agent', 'Unknown'))
    
    # Get the real IP address (considering proxy headers)
    # Note: In Cloud Run, X-Forwarded-For is set by the platform and can be trusted
    if request.headers.get('X-Forwarded-For'):
        ip_address = escape(request.headers.get('X-Forwarded-For').split(',')[0].strip())
    else:
        ip_address = escape(request.remote_addr)
    
    return f"""
    <html>
    <head>
        <title>Hello World</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #4285f4;
            }}
            .info {{
                margin: 10px 0;
                padding: 10px;
                background-color: #f8f9fa;
                border-left: 4px solid #4285f4;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello, world!</h1>
            <div class="info">
                <strong>Your User Agent:</strong><br>
                {user_agent}
            </div>
            <div class="info">
                <strong>Your IP Address:</strong><br>
                {ip_address}
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
