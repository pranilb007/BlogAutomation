# app.py
import os, io, shutil, random, string
from uuid import uuid4
from flask import Flask, request, redirect, render_template_string, flash, session, url_for, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import create_blog_via_api_with_docx_refactored as importer

import subprocess
import threading
import updater

# Run updater in background
def background_update_check():
    if updater.check_for_update():
        print("Update downloaded, will apply on next restart.")

threading.Thread(target=background_update_check, daemon=True).start()


# --- Load .env ---
load_dotenv()
DRUPAL_USERNAME = os.getenv("DRUPAL_USERNAME")
DRUPAL_PASSWORD = os.getenv("DRUPAL_PASSWORD")
DRUPAL_BASE_URL = os.getenv("DRUPAL_BASE_URL")

# --- Upload settings ---
UPLOAD_BASE   = os.path.join(os.path.dirname(__file__), "uploads")
DOCS_DIR      = os.path.join(UPLOAD_BASE, "docs")
ALLOWED_DOC_EXT = {"docx"}
ALLOWED_IMG_EXT = {"jpg", "jpeg", "png", "gif"}
os.makedirs(DOCS_DIR, exist_ok=True)

# --- Flask app ---
app = Flask(__name__)
# Read SECRET from environment for production safety. If not set, fall back to a random key for dev.
# Set FLASK_SECRET in your .env (recommended) or in the container environment to keep sessions secure.
app.secret_key = os.getenv("FLASK_SECRET") or os.urandom(24)

# --- CAPTCHA config ---
CAPTCHA_LENGTH = 5
CAPTCHA_WIDTH  = 150
CAPTCHA_HEIGHT = 50
FONT_PATH = os.path.join(os.path.dirname(__file__), "static/fonts/Roboto-Bold.ttf")  # optional custom TTF font path

def generate_captcha_text(length=CAPTCHA_LENGTH):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_captcha_image(text):
    """Generate a CAPTCHA image using Pillow"""
    img = Image.new('RGB', (CAPTCHA_WIDTH, CAPTCHA_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Optional: use custom font if available
    try:
        font = ImageFont.truetype(FONT_PATH or "Roboto-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()

    # Draw random noise lines
    for _ in range(6):
        start = (random.randint(0, CAPTCHA_WIDTH), random.randint(0, CAPTCHA_HEIGHT))
        end = (random.randint(0, CAPTCHA_WIDTH), random.randint(0, CAPTCHA_HEIGHT))
        draw.line([start, end], fill=(random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)), width=2)

    # Draw CAPTCHA text with random position/rotation
    for i, char in enumerate(text):
        x = 20 + i * 22
        y = random.randint(5, 15)
        draw.text((x, y), char, font=font, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)))

    # Add random dots
    for _ in range(200):
        draw.point((random.randint(0, CAPTCHA_WIDTH), random.randint(0, CAPTCHA_HEIGHT)),
                   fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img

@app.route("/captcha")
def captcha():
    """Serve a dynamic CAPTCHA image"""
    captcha_text = generate_captcha_text()
    session["captcha"] = captcha_text
    img = generate_captcha_image(captcha_text)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# --- HTML Templates ---
LOGIN_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login - Blog Automation</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <script src="{{ url_for('static', filename='main.js') }}"></script>
</head>
<body>
    <div class="login-container">
        <h1>Log_In</h1>
       <form method="post" onsubmit="return validateLoginForm()">
    <div class="login-form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" class="login-input"
               placeholder="Enter Your Username" minlength="3">
        <span class="error-message" id="username-error"></span>
    </div>
    
    <div class="login-form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" class="login-input"
               placeholder="Enter Your Password" minlength="6">
        <span class="error-message" id="password-error"></span>
    </div>

    <div class="login-form-group">
        <label for="captcha_input">Enter CAPTCHA:</label>
        <div class="captcha-box">
            <img id="captcha_img" src="{{ url_for('captcha') }}" alt="CAPTCHA">
            <button type="button" class="refresh-btn" onclick="refreshCaptcha()">🔄</button>
            <input type="text" id="captcha_input" name="captcha_input" class="login-input"
               placeholder="Enter CAPTCHA" >
        </div>
        
        <span class="error-message" id="captcha-error"></span>
    </div>

    <button type="submit" class="login-btn">Login</button>
</form>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="login-messages">
                    <ul>
                    {% for m in messages %}
                        <li>{{ m }}</li>
                    {% endfor %}
                    </ul>
                </div>
            {% endif %}
        {% endwith %}

        <script>
            function refreshCaptcha() {
                const img = document.getElementById('captcha_img');
                img.src = '{{ url_for('captcha') }}?t=' + new Date().getTime();
            }
        </script>
    </div>
</body>
</html>
"""

FORM_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEP - Blog Automation - Upload File</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>BlogFlow - Blog Automation Tool</h1>
        <p class="description">Upload your blog’s .docx file & images to create blog post</p>

        <form method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label for="docx">Document File (.docx)</label>
                <input type="file" id="docx" name="docx" accept=".docx" required>
            </div>

            <div class="form-group">
                <label for="images">Images (Multiple allowed)</label>
                <input type="file" id="images" name="images" multiple accept="image/*">
            </div>

            <button type="submit" class="submit-btn">Create Blog Post</button>
        </form>

        <p class="text-right mt-4"><a href="{{ url_for('logout') }}">Logout</a></p>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="messages">
                    <ul>
                    {% for m in messages %}
                        <li>{{ m }}</li>
                    {% endfor %}
                    </ul>
                </div>
            {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""

SUCCESS_HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success - Blog Created</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="result-container">
        {% if result.success %}
            <div class="success-header">✅ {{ result.message }}</div>
            
            <div class="info-grid">
                {% for key, value in result.data.items() %}
                    {% if value is mapping %}
                        {% for k, v in value.items() %}
                            <div class="info-label">{{ k.replace('_', ' ').title() }}:</div>
                            <div class="info-value">{{ v }}</div>
                        {% endfor %}
                    {% elif value is not iterable or value is string %}
                        <div class="info-label">{{ key.replace('_', ' ').title() }}:</div>
                        <div class="info-value">{{ value }}</div>
                    {% endif %}
                {% endfor %}
            </div>
        {% else %}
            <div class="error-header">❌ {{ result.message }}</div>
            
            {% if result.data.errors %}
                <div class="error-box">
                    {% for err in result.data.errors %}
                        <div class="error-item">
                            <div class="error-title">• {{ err.title }}</div>
                            {% if err.detail %}
                                <div class="error-detail">{{ err.detail }}</div>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
            {% elif result.data.raw_response %}
                <div class="error-box">
                    <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ result.data.raw_response }}</pre>
                </div>
            {% endif %}
        {% endif %}
        
        <div class="action-buttons">
            <a href="{{ url_for('upload') }}" class="btn btn-primary">Upload Another Blog</a>
            <a href="{{ url_for('logout') }}" class="btn btn-secondary">Logout</a>
        </div>
    </div>
</body>
</html>
"""

# --- Helper ---
def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def upload():
    # --- Login required ---
    if not session.get("logged_in"):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user_captcha = request.form.get("captcha_input", "").strip().upper()
            stored_captcha = session.get("captcha", "").upper()

            if user_captcha != stored_captcha:
                flash("❌ Invalid CAPTCHA. Please try again.")
                return render_template_string(LOGIN_HTML)

            if username == DRUPAL_USERNAME and password == DRUPAL_PASSWORD:
                session["logged_in"] = True
                flash("✅ Login successful")
                return redirect("/")
            else:
                flash("Invalid credentials")
                return render_template_string(LOGIN_HTML)
        return render_template_string(LOGIN_HTML)

    # --- File upload logic ---
    if request.method == "POST":
        docx_file = request.files.get("docx")
        if not docx_file or not allowed_file(docx_file.filename, ALLOWED_DOC_EXT):
            flash("Invalid or missing .docx file")
            return redirect(request.url)

        docx_name = secure_filename(docx_file.filename)
        docx_path = os.path.join(DOCS_DIR, docx_name)
        docx_file.save(docx_path)

        run_id = str(uuid4())
        run_images_dir = os.path.join(UPLOAD_BASE, "images", run_id)
        os.makedirs(run_images_dir, exist_ok=True)

        files = request.files.getlist("images")
        for f in files:
            if f and f.filename and allowed_file(f.filename, ALLOWED_IMG_EXT):
                f.save(os.path.join(run_images_dir, secure_filename(f.filename)))

        try:
            resp = importer.create_blog(docx_path, run_images_dir)
            result = importer.format_blog_response(resp)
            return render_template_string(SUCCESS_HTML, result=result)
        except Exception as e:
            result = {
                "success": False,
                "message": "An exception occurred",
                "data": {"raw_response": str(e)}
            }
            return render_template_string(SUCCESS_HTML, result=result)
        finally:
            shutil.rmtree(run_images_dir, ignore_errors=True)

    return render_template_string(FORM_HTML)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("Logged out successfully")
    return redirect("/")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000, debug=True)

if __name__ == "__main__":
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(target=open_browser).start()

    app.run(host="127.0.0.1", port=8000, debug=False)
