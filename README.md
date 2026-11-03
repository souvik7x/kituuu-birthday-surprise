# Kituuu's Little Universe ❤️

A personal Flask birthday website using your 7 supplied photos and the M4A song recording.

## Windows setup
1. Install Python 3.10+.
2. Open this folder in VS Code and open Terminal.
3. Run:

```powershell
py -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
```

4. Edit `.env`. Set a private `BIRTHDAY_PASSWORD`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and a long random `FLASK_SECRET_KEY`. Never share `.env` or commit it to GitHub.
5. Run `python app.py`.
6. Open http://127.0.0.1:5000

SQLite initializes automatically. The birthday password is checked only on the server and is never sent to JavaScript.

## Assets
Your photos are in `static/images/`. Your supplied audio is in `static/audio/main-phir-bhi-tumko-chahunga.m4a`. The player starts after the password interaction; if autoplay is blocked, press Play. M4A playback depends on browser support.

## Admin
Open `/admin/login`. Credentials are the values you set in `.env`. The dashboard provides basic photo upload and message storage.

## Before public deployment
This is a personal starter project, not a fully hardened public service. Add CSRF protection (e.g. Flask-WTF), production rate limiting (e.g. Flask-Limiter), hashed admin credentials, robust admin session controls, and validate upload content rather than relying only on extensions. Use HTTPS, set `COOKIE_SECURE=true`, use a production WSGI server, and configure persistent storage for SQLite/uploads. Netlify static hosting alone cannot run Flask.
