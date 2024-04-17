from datetime import date, timedelta
from flask import jsonify, render_template
from flask import Blueprint
from flask import request
from app.models import Defect,Fabric, FabricDefects
from app import db

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
     # Get all fabrics
    fabrics = Fabric.query.all()

    # Count defected and non-defected fabrics for all fabrics
    defected_count = sum(1 for fabric in fabrics if fabric.total_defects)
    non_defected_count = len(fabrics) - defected_count
    
    # Get today's date
    today_date = date.today()
    # Get yesterday's date
    yesterday_date = today_date - timedelta(days=1)

    # Query fabrics added yesterday
    fabrics_yesterday = Fabric.query.filter(db.func.date(Fabric.date_added) == yesterday_date).all()
    # Query fabrics added today
    fabrics_today = Fabric.query.filter(db.func.date(Fabric.date_added) == today_date).all()

    # Calculate defected and non-defected counts for today
    defected_count_today = sum(1 for fabric in fabrics_today if fabric.total_defects)
    non_defected_count_today = len(fabrics_today) - defected_count_today
    defected_count_yesterday = sum(1 for fabric in fabrics_yesterday if fabric.total_defects)
    defect_counts = {}
    for defect_type in ['Hole', 'Stain', 'Line', 'Knot']:
        count = db.session.query(db.func.count(FabricDefects.id)).filter(FabricDefects.defect == defect_type).scalar()
        defect_counts[defect_type] = count

    # Get the count of "hole" defect, default to 0 if not found
    hole_count = defect_counts.get("Hole", 0)
    stain_count = defect_counts.get("Stain", 0)
    line_count = defect_counts.get("Line", 0)
    knot_count = defect_counts.get("Knot", 0)

    return render_template('dashboard.html', title=title, defected_count=defected_count, non_defected_count=non_defected_count, 
                           defected_count_today=defected_count_today, non_defected_count_today=non_defected_count_today,
                           hole_count=hole_count, stain_count=stain_count, line_count=line_count, knot_count=knot_count,defected_count_yesterday=defected_count_yesterday)
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
