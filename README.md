# Blog Automation (Flask) — Docker instructions

This repository contains a small Flask app to upload .docx and images and create blog posts via Drupal JSON:API.

What I changed for Docker:
- Added `requirements.txt` (project dependencies)
- Added a `Dockerfile` and `.dockerignore`
- Added `.env.example` with required environment variables
- `app.py` now reads `FLASK_SECRET` from the environment (do not keep a hard-coded secret in production)

Before you build
1. Copy `.env.example` to `.env` and set the values:

```
DRUPAL_BASE_URL=https://your-drupal-site.example
DRUPAL_USERNAME=your_username
DRUPAL_PASSWORD=your_password
FLASK_SECRET=replace-with-a-secure-secret
```

2. Ensure `uploads/` exists locally (it will be mounted into the container to persist uploaded files):

PowerShell:

```powershell
# from project root
if (-not (Test-Path uploads)) { New-Item -ItemType Directory uploads }
if (-not (Test-Path uploads\docs)) { New-Item -ItemType Directory uploads\docs }
if (-not (Test-Path uploads\images)) { New-Item -ItemType Directory uploads\images }
```

Build the Docker image (PowerShell)

```powershell
# Build image from project root
docker build -t blog-automation .
```

Run the container (PowerShell)

```powershell
# Mount local uploads so files persist. Use --env-file to pass .env into the container
docker run -p 8000:8000 -v "${PWD}\\uploads:/app/uploads" --env-file .env blog-automation
```

Notes:
- The app listens on port 8000 (container and host mapping above).
- Use a strong `FLASK_SECRET` value in production (at least 32 random characters). Alternatively, set it in your hosting platform or Docker secrets.
- If running on Docker Desktop for Windows, the `${PWD}` expansion in PowerShell resolves to the absolute path of the current folder. If using WSL, you can use the Linux-style path: `-v "$(pwd)/uploads:/app/uploads"`.

Testing locally without Docker

1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create `.env` as above and run:

```powershell
python app.py
```

The app will be available at `http://localhost:8000`.

Next steps I can help with:
- Run the Docker build and test it locally from here (I can run the commands if you want).
- Add a small health-check endpoint and a basic `docker-compose.yml` for local dev.
- Add a `Makefile` or PowerShell script to simplify build/run.
