from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError 
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from math import ceil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study_items.db'
app.config['SECRET_KEY'] = 'code_cave'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # Foreign key to Tag table

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='tag', lazy=True)  # Relationship to Task table

with app.app_context():
    db.create_all()
    predefined_tags = ["DSA", "TSP", "EYC", "All"]
    for tag_name in predefined_tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:

            new_tag = Tag(name=tag_name)
            db.session.add(new_tag)
    db.session.commit()
   

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('layout'))
        else:
            flash('Incorrect username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('register'))

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already taken. Please choose another one.', 'error')

    return render_template('register.html')


@app.route('/layout')
@login_required
def layout():
    predefined_tags = [tag.name for tag in Tag.query.all()]
    return render_template('layout.html', predefined_tags=predefined_tags)

@app.route('/')
@app.route('/<tag>')
@login_required
def index():
    tag = request.args.get('tag')
    page = request.args.get('page', 1, type=int)  # Get the page number from the URL query parameters

    # Adjust the query to fetch tasks based on the current page number
    tasks_query = Task.query.filter_by(user_id=current_user.id, done=False)
    if tag == 'All':
        tasks_query = tasks_query.filter_by(user_id=current_user.id)
    elif tag:
        tasks_query = tasks_query.filter_by(user_id=current_user.id, tag_id=tag)

    tasks = tasks_query.paginate(page=page, per_page=5)  # Paginate the tasks

    predefined_tags = [tag.name for tag in Tag.query.all()]

    return render_template('index.html', predefined_tags=predefined_tags, tasks=tasks, username=current_user.username)

    # try:
    #     response = requests.get('http://worldtimeapi.org/api/timezone/Africa/Lagos')
    #     response.raise_for_status()
    #     data = response.json()
    #     api_datetime = data['datetime']
    #     formatted_datetime = datetime.strptime(api_datetime, '%Y-%m-%dT%H:%M:%S.%f%z')
    #     formatted_datetime_str = formatted_datetime.strftime('%A %B %d %Y %H:%M')
    #     datetime_info = formatted_datetime_str
    # except Exception:
    #     datetime_info = "N/A"

    # return render_template('index.html', predefined_tags=predefined_tags, tasks=tasks, remaining_tasks=remaining_tasks, username=username, datetime_info=datetime_info)


    
@app.route('/add', methods=['POST'])
@login_required
def add():
    task_text = request.form['study_items'].strip()
    selected_tag_id = request.form['tag']

    if not task_text:
        flash('Cannot add an empty study item. Please enter a task.', 'error')
        return redirect(url_for('index'))
    
    new_task = Task(task=task_text, user_id=current_user.id, tag_id=selected_tag_id) 

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/completed')
@login_required
def completed():
    completed_tasks = Task.query.filter_by(user_id=current_user.id, done=True).all()
    return render_template('completed_routines.html', completed_tasks=completed_tasks)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    task = Task.query.get(id)
    if request.method == 'POST':
        task.task = request.form['study_items']
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', task=task)

@app.route('/check/<int:id>')
@login_required
def check(id):
    task = Task.query.get(id)
    task.done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        if request.form.get('confirm') == 'yes':
            db.session.delete(task)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    return render_template('confirm_delete.html', task=task)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
 
