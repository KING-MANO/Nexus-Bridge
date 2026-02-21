import http.server
import socketserver
import os
import socket
import urllib.parse
import html
from http import cookies
import io
import qrcode
import zipfile
import time
import threading

PORT = 8000

USERNAME = "admin"
PASSWORD = "nexus123"
SESSION_COOKIE = "nexus_session"
SESSION_TIMEOUT = 1800  # 30 minutes
sessions = {}

print("=== NEXUS BRIDGE : LAPTOP ➜ PHONE FILE ACCESS ===")
ROOT = input("Enter drive or folder to share (example: D:/ or C:/Users): ").strip()

if not os.path.exists(ROOT):
    print("Path not found!")
    exit()

os.chdir(ROOT)

current_root = [ROOT] 


FOLDER_SVG = '''<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="48" height="48" rx="12" fill="#6366f1"/><path d="M10 36V14a2 2 0 0 1 2-2h8l2 4h14a2 2 0 0 1 2 2v18a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2z" fill="#fff"/></svg>'''

def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False

def make_qr_code(data):
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

def render_page(path, files, rel_path="", error=""):
    cards = ""
    for name in files:
        if name.startswith("."):
            continue
        full = os.path.join(path, name)
        # Compute the relative path from the root for navigation and zip
        if rel_path:
            rel = f"{rel_path}/{name}"
        else:
            rel = name
        link = urllib.parse.quote(rel)

        if os.path.isdir(full):
            cards += f"""
            <div class="card folder">
                <div class="card-icon">
                    {FOLDER_SVG}
                </div>
                <div class="card-content">
                    <a href="/{link}/" class="card-title">{name}</a>
                    <div class="card-subtitle">Folder</div>
                </div>
                <form action="/{link}/" method="get" style="margin:0;display:inline;">
                    <button type="submit" class="card-action">Open</button>
                </form>
                <form action="/zip" method="post" style="display:inline;">
                    <input type="hidden" name="folder" value="{html.escape(rel)}">
                    <button type="submit" class="card-action" style="margin-left:8px;background:linear-gradient(135deg,#10b981,#059669);color:#fff;">
                        <i class="fas fa-file-archive"></i> Download as ZIP
                    </button>
                </form>
            </div>
            """
        else:
            size = os.path.getsize(full) / 1024
            size_text = f"{size:.1f} KB" if size < 1024 else f"{size/1024:.1f} MB"
            cards += f"""
            <div class="card file">
                <div class="card-icon">📄</div>
                <div class="card-content">
                    <span class="card-title">{name}</span>
                    <div class="card-subtitle">{size_text}</div>
                </div>
                <a href="/{link}" download class="download-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    Download
                </a>
            </div>
            """
    qr_html = f'<div style="text-align:center;margin:24px 0;"><img src="/qr.png" alt="QR Code" style="width:180px;height:180px;"><div style="color:#94a3b8;margin-top:8px;">Scan this QR code with your phone to open: <b>http://{IP}:{PORT}</b></div></div>'

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nexus Bridge</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #8b5cf6;
    --background: #0f172a;
    --surface: #1e293b;
    --surface-light: #334155;
    --text: #f8fafc;
    --text-secondary: #94a3b8;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --border: #475569;
    --shadow: rgba(0, 0, 0, 0.3);
}}

body {{
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    padding: 20px;
    position: relative;
    overflow-x: hidden;
}}

body::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
    z-index: -1;
}}

.container {{
    max-width: 900px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}

.header {{
    background: linear-gradient(135deg, var(--surface) 0%, rgba(30, 41, 59, 0.8) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px var(--shadow);
}}

.header-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.logo i {{
    font-size: 2rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.path-container {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: rgba(15, 23, 42, 0.7);
    border-radius: 12px;
    margin-bottom: 16px;
    border: 1px solid var(--border);
}}

.path-label {{
    color: var(--text-secondary);
    font-size: 0.875rem;
    font-weight: 500;
}}

.path-value {{
    color: var(--text);
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.875rem;
    word-break: break-all;
    flex: 1;
}}

.change-root-form {{
    display: flex;
    gap: 12px;
    margin-top: 16px;
}}

.change-root-form input {{
    flex: 1;
    padding: 14px 18px;
    background: rgba(15, 23, 42, 0.7);
    border: 2px solid var(--border);
    border-radius: 12px;
    color: var(--text);
    font-size: 0.95rem;
    transition: all 0.3s ease;
}}

.change-root-form input:focus {{
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}}

.change-root-form button {{
    padding: 14px 28px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: none;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 140px;
    justify-content: center;
}}

.change-root-form button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}}

.error-box {{
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideDown 0.3s ease;
}}

@keyframes slideDown {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.error-box i {{
    color: var(--error);
    font-size: 1.25rem;
}}

.content-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    margin-top: 24px;
}}

.card {{
    background: linear-gradient(135deg, var(--surface) 0%, rgba(30, 41, 59, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}}

.card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
}}

.card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 12px 32px var(--shadow);
    border-color: var(--primary);
}}

.card.folder:hover {{
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, var(--surface) 100%);
}}

.card.file:hover {{
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, var(--surface) 100%);
}}

.card-icon {{
    font-size: 2rem;
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(99, 102, 241, 0.1);
    border-radius: 12px;
    flex-shrink: 0;
}}

.folder .card-icon {{
    background: rgba(99, 102, 241, 0.15);
    color: var(--primary);
}}

.file .card-icon {{
    background: rgba(139, 92, 246, 0.15);
    color: var(--secondary);
}}

.card-content {{
    flex: 1;
    min-width: 0;
}}

.card-title {{
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    display: block;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none;
}}

.card-subtitle {{
    font-size: 0.875rem;
    color: var(--text-secondary);
}}

.card-action, .download-btn {{
    padding: 10px 18px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: none;
    border-radius: 10px;
    color: white;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    flex-shrink: 0;
}}

.card-action:hover, .download-btn:hover {{
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3);
}}

.download-btn {{
    background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
}}

.download-btn:hover {{
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
}}

.empty-state {{
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: var(--text-secondary);
}}

.empty-state i {{
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.5;
}}

.empty-state h3 {{
    font-size: 1.5rem;
    margin-bottom: 10px;
    color: var(--text);
}}

@media (max-width: 768px) {{
    .content-grid {{
        grid-template-columns: 1fr;
    }}
    
    .header-top {{
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
    }}
    
    .change-root-form {{
        flex-direction: column;
    }}
    
    .change-root-form button {{
        width: 100%;
    }}
    
    .card {{
        flex-direction: column;
        text-align: center;
        gap: 12px;
    }}
    
    .card-content {{
        width: 100%;
    }}
}}

@media (max-width: 480px) {{
    body {{
        padding: 12px;
    }}
    
    .header {{
        padding: 20px;
    }}
    
    .logo {{
        font-size: 1.5rem;
    }}
    
    .card {{
        padding: 16px;
    }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="header-top">
            <div class="logo">
                <i class="fas fa-bridge"></i>
                Nexus Bridge
            </div>
            <div class="path-container">
                <span class="path-label">Current Location:</span>
                <span class="path-value">{path}</span>
            </div>
            <form action="/logout" method="get" style="margin-left:auto;">
                <button type="submit" class="card-action" style="background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;">
                    <i class="fas fa-sign-out-alt"></i> Sign Out
                </button>
            </form>
            <form action="/exit" method="get" style="margin-left:12px;">
                <button type="submit" class="card-action" style="background:linear-gradient(135deg,#0ea5e9,#0369a1);color:#fff;">
                    <i class="fas fa-power-off"></i> Exit
                </button>
            </form>
        </div>
        
        <form class="change-root-form" method="POST">
            <input type="text" name="newroot" placeholder="Enter new directory path (e.g., C:/Users, D:/Documents)" required>
            <button type="submit">
                <i class="fas fa-folder-open"></i>
                Change Directory
            </button>
        </form>
    </div>
    
    {f'<div class="error-box"><i class="fas fa-exclamation-circle"></i><div>{html.escape(error)}</div></div>' if error else ''}
    
    <div class="content-grid">
        {cards if cards else '''
        <div class="empty-state">
            <i class="fas fa-folder-open"></i>
            <h3>No Items Found</h3>
            <p>This directory appears to be empty</p>
        </div>
        '''}
    </div>
    {qr_html}
</div>
</body>
</html>
"""

def render_login_page(error=None):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Login - Nexus Bridge</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #8b5cf6;
    --background: #0f172a;
    --surface: #1e293b;
    --surface-light: #334155;
    --text: #f8fafc;
    --text-secondary: #94a3b8;
    --error: #ef4444;
    --border: #475569;
    --shadow: rgba(0, 0, 0, 0.3);
}}

body {{
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    position: relative;
    overflow: hidden;
}}

body::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.2) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%);
    z-index: -1;
}}

.login-container {{
    width: 100%;
    max-width: 440px;
    position: relative;
    z-index: 1;
}}

.login-header {{
    text-align: center;
    margin-bottom: 40px;
}}

.logo {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 20px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.logo i {{
    font-size: 3rem;
}}

.tagline {{
    color: var(--text-secondary);
    font-size: 1.1rem;
    line-height: 1.6;
}}

.login-box {{
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 48px 40px;
    box-shadow: 0 20px 60px var(--shadow);
    animation: fadeIn 0.6s ease-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.login-title {{
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 32px;
    text-align: center;
    color: var(--text);
}}

.error-box {{
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideDown 0.3s ease;
}}

.error-box i {{
    color: var (--error);
    font-size: 1.25rem;
    flex-shrink: 0;
}}

.error-box div {{
    flex: 1;
}}

@keyframes slideDown {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.input-group {{
    margin-bottom: 24px;
    position: relative;
}}

.input-label {{
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: var(--text);
    font-size: 0.95rem;
}}

.input-with-icon {{
    position: relative;
}}

.input-icon {{
    position: absolute;
    left: 18px;
    top: 50%;
    transform: translateY(-50%);
    color: var (--text-secondary);
    font-size: 1.1rem;
    z-index: 1;
}}

.input-field {{
    width: 100%;
    padding: 18px 18px 18px 52px;
    background: rgba(15, 23, 42, 0.7);
    border: 2px solid var(--border);
    border-radius: 14px;
    color: var(--text);
    font-size: 1rem;
    transition: all 0.3s ease;
}}

.input-field:focus {{
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}}

.input-field::placeholder {{
    color: var(--text-secondary);
}}

.login-button {{
    width: 100%;
    padding: 18px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: none;
    border-radius: 14px;
    color: white;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-top: 32px;
}}

.login-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 100%);
}}

.login-button:active {{
    transform: translateY(0);
}}

.login-footer {{
    text-align: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--text-secondary);
    font-size: 0.9rem;
}}

.login-footer strong {{
    color: var(--primary);
}}

@media (max-width: 480px) {{
    .login-box {{
        padding: 32px 24px;
    }}
    
    .logo {{
        font-size: 2rem;
    }}
    
    .logo i {{
        font-size: 2.5rem;
    }}
    
    .login-title {{
        font-size: 1.5rem;
    }}
    
    .input-field {{
        padding: 16px 16px 16px 48px;
    }}
}}
</style>
</head>
<body>
<div class="login-container">
    <div class="login-header">
        <div class="logo">
            <i class="fas fa-bridge"></i>
            Nexus Bridge
        </div>
        <p class="tagline">Secure File Access & Transfer Between Devices</p>
    </div>
    
    <form class="login-box" method="POST">
        <h2 class="login-title">
            <i class="fas fa-lock" style="margin-right: 12px;"></i>
            Secure Login
        </h2>
        
        {f'''
        <div class="error-box">
            <i class="fas fa-exclamation-circle"></i>
            <div>{html.escape(error)}</div>
        </div>
        ''' if error else ''}
        
        <div class="input-group">
            <label class="input-label">Username</label>
            <div class="input-with-icon">
                <i class="fas fa-user input-icon"></i>
                <input type="text" name="username" placeholder="Enter your username" required autofocus class="input-field">
            </div>
        </div>
        
        <div class="input-group">
            <label class="input-label">Password</label>
            <div class="input-with-icon">
                <i class="fas fa-key input-icon"></i>
                <input type="password" name="password" placeholder="Enter your password" required class="input-field">
            </div>
        </div>
        
        <button type="submit" class="login-button">
            <i class="fas fa-sign-in-alt"></i>
            Login to Nexus Bridge
        </button>
        
        <div class="login-footer">
            <p><strong>Default Credentials:</strong> admin / nexus123</p>
        </div>
    </form>
</div>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def is_authenticated(self):
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            c = cookies.SimpleCookie(cookie_header)
            if SESSION_COOKIE in c:
                sid = c[SESSION_COOKIE].value
                if sid in sessions:
                    # Check session timeout
                    if time.time() - sessions[sid] < SESSION_TIMEOUT:
                        sessions[sid] = time.time()  # refresh
                        return True
                    else:
                        del sessions[sid]
        return False

    def do_GET(self):
        if is_online():
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write("""
            <html><head><title>Offline Mode Only</title></head>
            <body style='background:#0f172a;color:#fff;font-family:Segoe UI;text-align:center;padding:60px;'>
            <h1>Nexus Bridge works only in offline mode</h1>
            <p>Please disconnect from the internet and try again.</p>
            </body></html>
            """.encode())
            return
        if self.path.startswith("/qr.png"):
            url = f"http://{IP}:{PORT}"
            img = make_qr_code(url)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(img)
            return
        if self.path.startswith("/zip/"):
            # Not used, ZIP download is POST only
            self.send_error(404)
            return
        if self.path.startswith("/exit"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write("""
            <html><head><title>Exit Nexus Bridge</title></head>
            <body style='background:#0f172a;color:#fff;font-family:Segoe UI;text-align:center;padding:60px;'>
            <h1>Nexus Bridge has been closed.</h1>
            <p>You can now safely close this browser tab.</p>
            <script>setTimeout(()=>{window.close();},2000);</script>
            </body></html>
            """.encode())

            import threading
            threading.Thread(target=self.server.shutdown).start()
            return
        if self.path.startswith("/login"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(render_login_page().encode())
            return
        if self.path.startswith("/logout"):
            self.send_response(302)
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
            self.send_header("Location", "/login")
            self.end_headers()
            return
        if not self.is_authenticated():
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return

        parsed = urllib.parse.urlparse(self.path)
        rel_path = urllib.parse.unquote(parsed.path.lstrip("/"))
        fs_path = os.path.normpath(os.path.join(current_root[0], rel_path))

        # Prevent directory traversal
        if not fs_path.startswith(os.path.abspath(current_root[0])):
            self.send_error(403)
            return

        if os.path.isdir(fs_path):
            try:
                files = os.listdir(fs_path)
            except:
                files = []
            page = render_page(fs_path, files, rel_path=rel_path)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(page.encode())
            return
        if os.path.isfile(fs_path):
            return super().do_GET()
        self.send_error(404)

    def do_POST(self):
        if is_online():
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write("""
            <html><head><title>Offline Mode Only</title></head>
            <body style='background:#0f172a;color:#fff;font-family:Segoe UI;text-align:center;padding:60px;'>
            <h1>Nexus Bridge works only in offline mode</h1>
            <p>Please disconnect from the internet and try again.</p>
            </body></html>
            """.encode())
            return
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/zip":
            folder = None
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode()
            params = urllib.parse.parse_qs(data)
            folder = params.get('folder', [''])[0]
            folder_path = os.path.normpath(os.path.join(current_root[0], folder))
            # Prevent directory traversal
            if not folder_path.startswith(os.path.abspath(current_root[0])):
                self.send_error(403)
                return
            if os.path.isdir(folder_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{os.path.basename(folder_path)}.zip"')
                self.end_headers()
                # Stream the zip file directly to the client
                with zipfile.ZipFile(self.wfile, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            absfile = os.path.join(root, file)
                            relfile = os.path.relpath(absfile, folder_path)
                            with open(absfile, 'rb') as f:
                                zf.writestr(relfile, f.read())
                return
            else:
                self.send_error(404)
                return
        if parsed.path.startswith("/login"):
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode()
            params = urllib.parse.parse_qs(data)
            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]
            if username == USERNAME and password == PASSWORD:
                sid = str(time.time())
                sessions[sid] = time.time()
                self.send_response(302)
                self.send_header("Set-Cookie", f"{SESSION_COOKIE}={sid}; Path=/; HttpOnly")
                self.send_header("Location", "/")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(render_login_page("Invalid credentials").encode())
        elif parsed.path == "/":
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode()
            params = urllib.parse.parse_qs(data)
            newroot = params.get('newroot', [''])[0].strip()
            if newroot and os.path.exists(newroot) and os.path.isdir(newroot):
                current_root[0] = newroot
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
            else:
                try:
                    files = os.listdir(current_root[0])
                except:
                    files = []
                page = render_page(current_root[0], files, error="Invalid path or not a directory!")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(page.encode())
        else:
            self.send_error(404)

def udp_discovery_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", 37020))
    while True:
        data, addr = s.recvfrom(1024)
        if data == b'NEXUS_DISCOVER':
            s.sendto(f"NEXUS_BRIDGE:{IP}:{PORT}".encode(), addr)

discovery_thread = threading.Thread(target=udp_discovery_server, daemon=True)
discovery_thread.start()

IP = get_ip()
print("\n" + "="*60)
print("🚀 NEXUS BRIDGE SERVER STARTED")
print("="*60)
print(f"📡 Server IP: {IP}")
print(f"🔗 Port: {PORT}")
print(f"📂 Root Directory: {ROOT}")
print("="*60)
print("\n📱 Access on your phone browser:")
print(f"   👉 http://{IP}:{PORT}")
print("\n⚡ Modern UI Enabled")
print("🎨 Gradient Backgrounds & Animations")
print("📱 Fully Responsive Design")
print("="*60 + "\n")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    httpd.serve_forever()