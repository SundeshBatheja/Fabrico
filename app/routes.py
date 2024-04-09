from flask import jsonify, render_template
from flask import Blueprint
from flask import request
from app.models import Defect,Fabric

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
    fabrics = Fabric.query.all()
    return render_template('fabricData.html',title=title, fabrics=fabrics)

@FabricoPrefix.route('/supervision')
def supervision():
    title = "Supervision"
    return render_template('supervision.html',title=title)

@FabricoPrefix.route('/dashboard')
def dashboard():
    title = "Dashboard"
    return render_template('dashboard.html',title=title)

@FabricoPrefix.route('/LoginForm',methods=['POST'])
def loginForm():
    Username = request.form.get('username')
    Password = request.form.get('password')
    if not Username or not Password:
        error_statement = 'All fields are required...'
        print('All fields are required.')
        return render_template('login.html',error_statement=error_statement,
                               username=Username,password=Password)
    return render_template('fabricData.html')

@FabricoPrefix.route('/RegisterForm',methods=['POST'])
def registerForm():
    Username = request.form.get('username')
    Password = request.form.get('password')
    systemid = request.form.get('systemid')
    if not Username or not Password or not systemid:
        error_statement = 'All fields are required.'
        print('All fields are required.')
        return render_template('register.html',error_statement=error_statement,
                               username=Username,password=Password,systemid=systemid)
    return render_template('fabricData.html')
