import os, sqlite3, secrets
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
ROOT=Path(__file__).resolve().parent
(ROOT/"instance").mkdir(exist_ok=True)
(ROOT/"uploads/memories").mkdir(parents=True,exist_ok=True)
app=Flask(__name__)
app.config.update(SECRET_KEY=os.getenv("FLASK_SECRET_KEY",secrets.token_hex(32)),
 MAX_CONTENT_LENGTH=8*1024*1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
 SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE","false").lower()=="true")
DB=ROOT/"instance/birthday.db"
ALLOWED={"jpg","jpeg","png","webp"}

def connect():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
 with connect() as c:
  c.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL)")
  if c.execute("SELECT COUNT(*) FROM messages").fetchone()[0]==0:
   c.execute("INSERT INTO messages(title,body) VALUES(?,?)",("A little note for Kituuu","You make ordinary days feel special. Happy Birthday! ❤️"))

def admin_only(fn):
 @wraps(fn)
 def wrapped(*a,**k):
  if not session.get("admin"): return redirect(url_for("admin_login"))
  return fn(*a,**k)
 return wrapped

@app.after_request
def headers(r):
 r.headers["X-Content-Type-Options"]="nosniff"; r.headers["X-Frame-Options"]="SAMEORIGIN"
 r.headers["Referrer-Policy"]="strict-origin-when-cross-origin"; return r

@app.route("/")
def index(): return render_template("index.html")

@app.post("/unlock")
def unlock():
 attempts=session.get("attempts",0)
 if attempts>=8: return jsonify(ok=False,message="Too many attempts. Refresh and try later."),429
 expected=os.getenv("BIRTHDAY_PASSWORD","")
 supplied=request.form.get("password","")
 if expected and secrets.compare_digest(expected,supplied):
  session["unlocked"]=True; session["attempts"]=0; return jsonify(ok=True)
 session["attempts"]=attempts+1
 return jsonify(ok=False,message="Not quite, my love. Try again ❤️"),401

@app.route("/admin/login",methods=["GET","POST"])
def admin_login():
 if request.method=="POST":
  u=os.getenv("ADMIN_USERNAME","admin"); p=os.getenv("ADMIN_PASSWORD","")
  if p and secrets.compare_digest(request.form.get("username",""),u) and secrets.compare_digest(request.form.get("password",""),p):
   session["admin"]=True; return redirect(url_for("admin"))
  flash("Login details did not match.")
 return render_template("admin_login.html")

@app.get("/admin/logout")
def admin_logout(): session.pop("admin",None); return redirect(url_for("admin_login"))

@app.get("/admin")
@admin_only
def admin():
 with connect() as c: messages=c.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
 return render_template("admin.html",messages=messages)

@app.post("/admin/message")
@admin_only
def add_message():
 title=request.form.get("title","").strip()[:100]; body=request.form.get("body","").strip()[:3000]
 if title and body:
  with connect() as c: c.execute("INSERT INTO messages(title,body) VALUES(?,?)",(title,body))
 flash("Message saved."); return redirect(url_for("admin"))

@app.post("/admin/upload")
@admin_only
def upload():
 f=request.files.get("photo")
 if not f or not f.filename: flash("Choose a photo."); return redirect(url_for("admin"))
 name=secure_filename(f.filename); ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
 if ext not in ALLOWED: flash("Use JPG, PNG or WEBP."); return redirect(url_for("admin"))
 f.save(ROOT/"uploads/memories"/name); flash("Photo uploaded."); return redirect(url_for("admin"))

@app.get("/api/messages")
def messages():
 with connect() as c: rows=c.execute("SELECT title,body FROM messages ORDER BY id DESC").fetchall()
 return jsonify([dict(x) for x in rows])

@app.errorhandler(413)
def too_big(e): return "File too large (maximum 8 MB).",413

if __name__=="__main__":
 init_db(); app.run(debug=os.getenv("FLASK_DEBUG","false").lower()=="true")
