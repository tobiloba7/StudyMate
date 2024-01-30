from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routines.db'  # SQLite database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Routine model
class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    tasks = db.relationship('Task', backref='routine', lazy=True)

    def __repr__(self):
        return f"Routine('{self.name}', '{self.created_at}')"

# Define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    routine_id = db.Column(db.Integer, db.ForeignKey('routine.id'), nullable=False)


# Mock data for demonstration purposes
mock_completed_routines = ["Routine 1", "Routine 2", "Routine 3"]

# Explicitly create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/create_routine', methods=['GET', 'POST'])
def create_routine():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'routine':
            routine_name = request.form.get('name')
            if not routine_name:
                return redirect(url_for('create_routine'))

            routine = Routine.query.filter_by(name=routine_name).first()
            if not routine:
                routine = Routine(name=routine_name)
                db.session.add(routine)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Error occurred while creating routine:", str(e))
                # Handle the error as needed

        elif form_type == 'task':
            routine_name = request.form.get('name')
            task_content = request.form.get('content')
            task_category = request.form.get('category')

            routine = Routine.query.filter_by(name=routine_name).first()
            if not routine:
                # Handle case where routine does not exist
                pass

            task = Task(content=task_content, category=task_category, routine=routine)
            db.session.add(task)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Error occurred while adding task:", str(e))
                # Handle the error as needed

        return redirect(url_for('create_routine'))

    return render_template('create_routine.html')







@app.route('/completed_routines')
def completed_routines():
    return render_template('completed_routines.html', routines=mock_completed_routines)

@app.route('/logout')
def logout():
    # Add logic for logging out
    return "Logout functionality"

if __name__ == '__main__':
    app.run(debug=True)
