import json
import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, send_file
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy
import openai
import redis
import rq
from rq.job import Job

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'welcome'

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
r = redis.Redis(host='localhost', port=6379, db=0)

q = rq.Queue(connection=r)

openai.api_key = os.getenv("OPENAI_API_KEY")

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    prof = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    language_id = db.Column(db.String(2), nullable=False)

    def __repr__(self):
        return f"User({self.first_name} {self.last_name})"


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('welcome'))

def session_set(r, key: str, value): r.set(key, value)
def session_get(r, key: str): return r.get(key)
def session_has(r, key: str): return r.exists(key)
def session_del(r, key: str): return r.delete(key)


@app.route('/', methods=['GET', 'POST'])
@login_required
def query():
    if request.method == 'POST':
        query_text = request.form['query']
        qid = str(uuid.uuid4())
        job = q.enqueue_call(func=generate_presentation, args=(qid, query_text, current_user.prof, app.instance_path, current_user.language_id)) # TODO: add current user context
        presentation = {
            "status": "pending",
            "query_text": query_text,
            "job_id": job.get_id()
        }
        session_set(r, qid2qck(qid), json.dumps(presentation))
        return redirect(url_for('slides', qid=qid))

    return render_template('query.html')


@app.route('/slides/<string:qid>')
@login_required
def slides(qid):
    return render_template('slides.html', qid=qid)

@app.route('/query/<string:qid>/<int:i>/audio')
def get_audio(qid, i):
    fn = get_audio_clip_path(app.instance_path, qid, i)
    if not os.path.isfile(fn):
        return jsonify(error="Not found"), 404
    return send_file(fn, mimetype='audio/mpeg')

def is_presentation_ready(slides):
    for slide in slides:
        if slide["image_status"] == "pending" or slide["audio_status"] == "pending":
            return False
    return True

@app.route('/debug/<string:qid
