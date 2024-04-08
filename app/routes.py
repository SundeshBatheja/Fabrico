from flask import render_template
from flask import Blueprint
from flask import request

FabricoPrefix = Blueprint('Fabrico', __name__, url_prefix='/Fabrico',template_folder="templates")

@FabricoPrefix.route('/')
def login():
    title = "sign In"
    return render_template('login.html',title=title)

@FabricoPrefix.route('/registerUser')
def register():
    title = "Sign Up"
    return render_template('register.html',title=title)

@FabricoPrefix.route('/fabrics')
def index():
    title = "Records"
    return render_template('fabricData.html',title=title)

@FabricoPrefix.route('/supervision')
def supervision():
    title = "Supervision"
    return render_template('supervision.html',title=title)

@FabricoPrefix.route('/dashboard')
def dashboard():
    title = "Dashboard"
    return render_template('dashboard.html',title=title)

@FabricoPrefix.route('/form',methods=['POST'])
def form():
    Email = request.form.get('username')
    Password = request.form.get('password')
    if not Email or not Password:
        error_statement = 'All fields are required...'
        print('All fields are required...')
        return render_template('login.html',error_statement=error_statement,
                               username=Email,password=Password)
    return render_template('fabricData.html')