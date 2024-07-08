from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
from datetime import timedelta
from celery_config import make_celery
from sqlalchemy import func
from api import init_api

app = Flask(__name__)
app.config['SECRET_KEY'] = '9a8e4fd3c3a78bcaa0ee705ab621ae1a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session')

# Celery configuration
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)

db = SQLAlchemy(app)
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Create API blueprint
api = Blueprint('api', __name__)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', todos=todos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)  # Set remember=True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Set remember=True
            return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    new_todo = Todo(title=title, description=description, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
@login_required
def complete_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        todo.completed = not todo.completed
        db.session.commit()
        if todo.completed:
            send_task_completion_notification.delay(todo.id)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
@login_required
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    todo = Todo.query.get_or_404(id)
    if todo.user_id != current_user.id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', todo=todo)
@celery.task
def send_task_completion_notification(task_id):
    # In a real application, you would send an email or push notification here
    todo = Todo.query.get(task_id)
    print(f"Task '{todo.title}' has been completed!")

def init_db():
    db.create_all()
    print("Database initialized.")

@app.route('/stats')
@login_required
def task_stats():
    total_tasks = Todo.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Todo.query.filter_by(user_id=current_user.id, completed=True).count()
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return render_template('stats.html', 
                           total_tasks=total_tasks, 
                           completed_tasks=completed_tasks, 
                           completion_rate=completion_rate)

from api import init_api
init_api(api, app, db, Todo)
app.register_blueprint(api)

if __name__ == '__main__':
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    with app.app_context():
        init_db()
    app.run(debug=True)