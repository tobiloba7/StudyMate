from flask import Flask, render_template

app = Flask(__name__)

# Mock data for demonstration purposes
mock_completed_routines = ["Routine 1", "Routine 2", "Routine 3"]

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/create_routine')
def create_routine():
    #logic for creating a study routine
    return render_template('create_routine.html')

@app.route('/completed_routines')
def completed_routines():
    return render_template('completed_routines.html', routines=mock_completed_routines)

@app.route('/logout')
def logout():
    # logic for logging out
    return "Logout functionality"

if __name__ == '__main__':
    app.run(debug=True)
