from flask import render_template
from flask import Blueprint

FabricoPrefix = Blueprint('Fabrico', __name__, url_prefix='/Fabrico',template_folder="templates")

@FabricoPrefix.route('/')
def login():
    return render_template('login.html')
@FabricoPrefix.route('/registerUser')
def register():
    return render_template('register.html')

@FabricoPrefix.route('/fabrics')
def index():
    return render_template('fabricData.html')