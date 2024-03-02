import os
import secrets
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from flask_cors import CORS
from dotenv import load_dotenv
from python_code.models import db, init_db, Project, UserSession, User
from python_code.creator import (
    training_data, update_data, insert_data,
)
from python_code.destroyer import (
    delete_conversation, delete_data
)
from python_code.preserver import (
    query, get_conversation, get_knowledge_bases,
    load_kb_conversation
)
from realtime import realtime_query


# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)
app.secret_key =  os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
init_db(app)
# print('db = ',os.environ.get('SQLALCHEMY_DATABASE_URI'))

CORS(app, origins=['http://localhost:5173', 'http://localhost:5173/signin', 'http://localhost:5173/signup', 'http://127.0.0.1:5173/signup', 'http://127.0.0.1:5173/signin', 'http://127.0.0.1:5173/signup'])

@app.route('/')
def status():
    if 'session_token' in session:
        return 'OK!'
    return redirect('http://localhost:5173/signin')

@app.route('/check_session', methods=['POST'])
def check_session():
    user_id = request.json['user_id']
    session_token = request.json['session_token']
    print(user_id, session_token)
    user_session = UserSession.query.filter_by(user_id=user_id, session_token=session_token).first()
    if user_session:
        return {'status': 'valid'}
    else:
        return {'status': 'invalid'}

# @app.route('/get_data', methods=['POST'])
# def get_data_type():
#     data_type = request.form.get('data_type') or request.args.get('data_type')
#     if data_type == 'url':
#         url = request.form.get('url') or request.args.get('url')
#         result = get_data( data_type = data_type, url = url, )
#     if data_type == 'file':
#         file = request.form.get('file') or request.args.get('file')
#         file.save('file/' + file.filename)
#         result = get_data(data_type = data_type,file = file.filename,)
#     return jsonify(result)

@app.route('/knowledge_bases', methods=['POST'])
def knowledge_bases():
    user_id = request.form.get('user_id')
    return get_knowledge_bases(user_id=user_id)

@app.route('/train_knowledge_base', methods=['POST'])
def train():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    data_type = request.form.get('data_type') or request.args.get('data_type')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    file = request.form.get('file') or request.args.get('file')
    url = request.form.get('url') or request.args.get('url')
    text = request.form.get('text') or request.args.get('text')
    result = training_data(data_type=data_type, kb_name=kb_name, user_id=user_id, file=file, url=url, text=text)
    return jsonify(result)

@app.route('/delete_knowledge_base', methods=['POST'])
def delete():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    result = delete_data(user_id=user_id, kb_name=kb_name)
    return jsonify(result)

@app.route('/update_knowledge_base', methods=['POST'])
def update():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    data_type = request.form.get('data_type') or request.args.get('data_type')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    file = request.form.get('file') or request.args.get('file')
    url = request.form.get('url') or request.args.get('url')
    text = request.form.get('text') or request.args.get('text')
    result = update_data(data_type=data_type, kb_name=kb_name, user_id=user_id, file=file, url=url, text=text)
    return jsonify(result)

@app.route('/insert_knowledge_base', methods=['POST'])
def insert():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    data_type = request.form.get('data_type') or request.args.get('data_type')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    file = request.form.get('file') or request.args.get('file')
    url = request.form.get('url') or request.args.get('url')
    text = request.form.get('text') or request.args.get('text')
    result = insert_data(data_type=data_type, kb_name=kb_name, user_id=user_id, file=file, url=url, text=text)
    return jsonify(result)

@app.route('/query_knowledge_base', methods=['POST'])
def get_response():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    user_query = request.form.get('user_query') or request.args.get('user_query')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    conversation_id = request.form.get('conversation_id') or request.args.get('conversation_id')
    message_id = request.form.get('message_id') or request.args.get('message_id')
    result = query(user_id=user_id, user_query=user_query, kb_name=kb_name, conversation_id=conversation_id, message_id=message_id)
    return jsonify(result)

@app.route('/delete_conversation', methods=['POST'])
def del_conversation():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    conversation_id = request.form.get('conversation_id') or request.args.get('conversation_id')
    result = delete_conversation(user_id=user_id, kb_name=kb_name, conversation_id=conversation_id)
    return jsonify(result)

@app.route('/get_conversation', methods=['POST'])
def get_previous_conversation():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    conversation_id = request.form.get('conversation_id') or request.args.get('conversation_id')
    result = get_conversation(user_id=user_id, conversation_id=conversation_id)
    return jsonify(result)

@app.route('/load_knowledge_base_conversations', methods=['POST'])
def load_knowledge_base_conversation():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    kb_name = request.form.get('kb_name') or request.args.get('kb_name')
    result = load_kb_conversation(user_id=user_id, kb_name=kb_name)
    return jsonify(result)

@app.route('/create_project')
def create_project():
    user_id = request.form.get('user_id') or request.args.get('user_id')
    project_name = request.form.get('project_name') or request.args.get('project_name')
    if not project_name:
        return 'Project name required.'
    project_exists = db.session.query(db.exists().where(Project.name == project_name)).scalar()
    print('project_exists = ',project_exists)
    if project_exists:
        return f'Project exists with the name {project_name}'
    else:
        project = Project(name=project_name)
        db.session.add(project)
        db.session.commit()
        return 'project_created'
    
@app.route('/realtime_query', methods=['POST'])
def realtime_response():
    query = request.form.get('query') or request.args.get('query')
    result = realtime_query(query)
    return jsonify(result)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.json['username']
    password = request.json['password']
    print(username, password)
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return {'error': 'User already exist'}
    else:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return {'status':'ok'}

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'error': 'Username doesn\'t exist'}
    if user and user.check_password(password):
        # Generate a session token and store it in the database
        session_token = secrets.token_hex(16)
        new_session = UserSession(user_id=user.id, session_token=session_token)
        db.session.add(new_session)
        db.session.commit()
        # Set the session token in the user's browser
        session['session_token'] = session_token
        print(session_token)
        flash('Logged in successfully.', 'success')
        return {'user_id':user.id, 'session_token': session_token}
    else:
        return {'error': 'invalid'}

# @app.route('/dashboard')
# def dashboard():
#     session_token = session['session_token']
#     user_session = UserSession.query.filter_by(session_token=session_token).first()
#     if user_session:
#         # User is authenticated, display the dashboard
#         return render_template('dashboard.html')
#     flash('Please log in to access the dashboard.', 'danger')
#     return redirect(url_for('login'))

@app.route('/logout')
def logout():
    user_id = request.json['user_id']
    session_token = request.json['session_token']
    user_session = UserSession.query.filter_by(user_id=user_id, session_token=session_token).first()
    if user_session:
        # Remove the session from the database
        db.session.delete(user_session)
        db.session.commit()
        session.pop('session_token', None)
    else:
        return {'status': 'Logged out'}

if __name__ == '__main__':
    app.run(port=5000, debug=False)