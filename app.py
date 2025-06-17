import os 
from flask import Flask, flash, send_from_directory, request, jsonify, abort, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from obs_client_comm import OBSclient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from forms import SignupForm, LoginForm, is_safe_url, createInstance
from connection_manager import connection_manager
import flask
import base64
import obsws_python as obs
import logging

load_dotenv()
print("DATABASE_URL:", os.environ.get('DATABASE_URL'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, 
           static_folder = FRONTEND_DIST_DIR , 
           static_url_path = '/static',
           template_folder = TEMPLATES_DIR)

CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_PUBLIC_URL')
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("No ENCRYPTION_KEY set for encryption operations")
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    connections = db.relationship('OBSConnection', backref='user', lazy=True, cascade ="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.id

class OBSConnection(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(200), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=4455)
    encrypted_password = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def set_obs_password(self, password):
        self.encrypted_password = cipher_suite.encrypt(password.encode()).decode()

    def get_obs_password(self):
        return cipher_suite.decrypt(self.encrypted_password.encode()).decode()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def serve_svelte_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/goodstyles.css')
def serve_css():
    return send_from_directory(TEMPLATES_DIR, 'goodstyles.css', mimetype='text/css')

@app.route('/signup', methods = ["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            form.username.errors.append('Username already exists')
        else:
            try:
                newUser = User()
                newUser.username = form.username.data
                newUser.set_password(form.password.data)
                db.session.add(newUser)
                db.session.commit()
                login_user(newUser)
                return redirect('/')
            except Exception as e:
                db.session.rollback()
                print('Error creating user: {e}')
                return render_template('signupSheet.html', form=form)
            
    return render_template('signupSheet.html', form = form)

@app.route('/api/instances')
@login_required
def instances():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/renderInstances')
@login_required
def render():
    connectionList = []
    for connection in current_user.connections:
        connectionList.append({
            'id':connection.id,
            'name':connection.name,
            'host':connection.host
        })
    return jsonify({
        'user_id':current_user.id,
        'username': current_user.username,
        'connections':connectionList
    })

@app.route('/api/quickConnect', methods=["GET", "POST"])
def quickConnect():
    form = createInstance()
    if form.validate_on_submit():
        host = form.host.data
        if ':' in host:
            hostUrl, port = host.rsplit(':', 1)
        else:
            hostUrl = host
            port = 4455
        try:
            obs_instance = OBSclient(hostUrl, form.password.data, port)
            obs_instance.connect()
            scenes = obs_instance.get_scenes()
            token = connection_manager.add_connection(obs_instance)
            print(scenes)
            return redirect(f'/quickScenes?token={token}')
        except Exception as e:
            print('Error:', e)
    return render_template('quickInstance.html', form=form)

@app.route('/quickScenes')
def quickScenes():
    return render_template('sceneDashboard.html')

@app.route('/api/quickSession')
def fetchQuickScenes():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    obs_client = connection_manager.get_connection(token)
    if not obs_client:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    scenes_result = obs_client.get_scenes()
    if not scenes_result['success']:
        return jsonify({'error': 'Failed to get scenes'}), 500
    
    return jsonify({
        'connected':True,
        'scenes': [scene['sceneName'] for scene in scenes_result['data']],
        'token': token
    })
@app.route('/api/server_instances',methods = ["GET", "POST"])
@login_required
def server_instances():
    form = createInstance()
    if form.validate_on_submit():
        print('Form validated')
        newConnection = OBSConnection(name=form.name.data, host=form.host.data)
        newConnection.set_obs_password(form.password.data)
        print('connections appended')
        print(current_user.connections)
        try:
            db.session.commit()
            print('Weallgood')
        except Exception as e:
            db.session.rollback()
            print(e)

    return render_template('instanceForm.html', form=form)

@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!')
            next = flask.request.args.get('next')
            if not is_safe_url(next):
                return flask.abort(400)
            return redirect(next or '/api/quickConnect')

    return render_template('login.html', form = form)


@app.route('/<path:path>')
def serve_static_files(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return redirect('/')
    
@app.route('/api/obs/scenes')
@login_required
def get_scene_list():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    obs_client = connection_manager.get_connection(token)
    if not obs_client:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    try:
        scenes = obs_client.get_scenes()
        if not scenes['success']:
            return jsonify({
                "error": scenes.get('error', 'Unknown error'),
                "scenes": []
            }), 400
        
        return jsonify({
            "scenes": scenes['data'],
            "success": True
        })
    
    except Exception as e:
        return jsonify({
            "error": f'Server error: {str(e)}',
            "scenes": []
        }), 500

@app.route('/api/obs/scenes/<scene_name>', methods=["POST", "GET"])
def scene_switch(scene_name):
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    obs_client = connection_manager.get_connection(token)
    if not obs_client:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    try:
        success = obs_client.switch_scene(scene_name)
        if success:
            return jsonify({'scene_name': scene_name, 'success':True})
        else:
            return jsonify({'scene_name': scene_name, 'success': False, 'error': 'Switch failed'})
    except Exception as e:
        return jsonify({'scene_name': scene_name, 'success': False, 'error':f'Unable to switch scene:{e}'})

@app.route('/api/current_scene')
def current_scene():
    token  = request.args.get('token')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    obs_client = connection_manager.get_connection(token)
    if not obs_client:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    try:
        program_scene = obs_client.get_program_scene().scene_name
        return jsonify({'current_scene': program_scene, 'success': True})
    except Exception as e:
        return jsonify(f'Error finding current scene: {e}')
    

with app.app_context():
    db.create_all()

def test_database_setup():
    with app.app_context():
        print('Testing')
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_name = "user"
        columns = inspector.get_columns(table_name)
        print(f"Columns in {table_name}")
        table_names = inspector.get_table_names()
        print(f'Tables found: {table_names}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)