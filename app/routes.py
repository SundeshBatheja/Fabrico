from datetime import date, timedelta
from flask import render_template, Response,jsonify,request,session, redirect, url_for
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from wtforms.validators import InputRequired,NumberRange
from flask import request
from werkzeug.utils import secure_filename
from app.models import Defect,Fabric, FabricDefects
from app import db
from app.processing.videoProcess import video_detection
import os
import cv2


def generate_frames(path_x=''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        if detection_ is None:
            break
        ref, buffer = cv2.imencode('.jpg', detection_)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
class UploadFileForm(FlaskForm):
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

FabricoPrefix = Blueprint('Fabrico', __name__, url_prefix='/Fabrico',template_folder="templates")
UPLOAD_FOLDER = os.path.join('uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    


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

@FabricoPrefix.route('/supervision',methods=['GET','POST'])
def supervision():
    title = "Supervision"
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        session['video_path'] = file_path
    return render_template('supervision.html',title=title,form = form)

@FabricoPrefix.route('/video')
def video():
    video_path = session.get('video_path', None)
    if video_path:
        session.pop('video_path')  # Remove video_path from session after processing once
        return Response(generate_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "No video uploaded"

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
