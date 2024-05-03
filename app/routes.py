from datetime import date, timedelta
from flask import render_template, Response,jsonify,request,session, redirect, url_for, current_app
from flask import Blueprint
import flask
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

flag_check = False

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

@FabricoPrefix.route('/account')
def MyAccount():
    title = "My Account"
    return render_template('userAccount.html',title=title)

@FabricoPrefix.route('/fabrics')
def index():
    title = "Records"
    fabrics = Fabric.query.all()
    fabric_defects = {}
    
    fabric_defects = {}
    for fabric in fabrics:
        defect_counts = {}
        fabric_defect_entries = FabricDefects.query.filter_by(fabric_id=fabric.fabric_id).all()
        for defect_entry in fabric_defect_entries:
            defect_counts[defect_entry.defect] = defect_counts.get(defect_entry.defect, 0) + 1
        fabric_defects[fabric.fabric_id] = defect_counts

    return render_template('fabricData.html', title=title, fabrics=fabrics, fabric_defects=fabric_defects)

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
    global flag_check
    video_path = session.get('video_path', None)
    if video_path:
        defectDir = 'app/static/defects'
        if os.listdir(defectDir):
            for filename in os.listdir(defectDir):
                file_path = os.path.join(defectDir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error while deleting file: {e}")
        session.pop('video_path')  # Remove video_path from session after processing once
        flag_check = True
        return Response(generate_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "No video uploaded"
    
@FabricoPrefix.route('/addFabric', methods=['GET', 'POST'])
def addFabric():
    title = "Fabric Report"
    global flag_check
    if request.method == 'POST' and flag_check==True:
        defectDir = 'app/static/defects'  # Use forward slashes instead of backslashes
        total_defects = len(os.listdir(defectDir)) // 3
        fabrics = Fabric.query.all()
        fabricNum = len(fabrics)
        fabric_id = f"FAB{fabricNum + 1}"
        today_date = date.today()
        new_fabric = Fabric(
            fabric_id=fabric_id,
            total_defects=total_defects,
            date_added=today_date
        )
        db.session.add(new_fabric)
        db.session.commit()
        defect_types = {}
        defect_images = {}
        for defect_type in ['Hole', 'Stain', 'Line', 'Knot']:
            count = len([f for f in os.listdir(defectDir) if f.startswith(defect_type)]) // 3
            if count > 0:
                defect_types[defect_type] = int(count)
                defect_images[defect_type] = []

                # Get the images for the defect type
                for i in range(1, count + 1):
                    original_image_name = f"{defect_type}_{i}.jpg"
                    gray_image_name = f"{defect_type}_{i}_Mask.jpg"
                    boundary_image_name = f"{defect_type}_{i}_boundary.jpg"
                     # Read images as binary data
                    with open(os.path.join(defectDir, original_image_name), 'rb') as f:
                        original_image_data = f.read()

                    with open(os.path.join(defectDir, gray_image_name), 'rb') as f:
                        gray_image_data = f.read()

                    with open(os.path.join(defectDir, boundary_image_name), 'rb') as f:
                        boundary_image_data = f.read()
                    fabric_defect = FabricDefects(
                        defect=defect_type,
                        fabric_id=fabric_id,
                        defectimage=original_image_data,
                        defectGray=gray_image_data,
                        defectBoundary=boundary_image_data
                    )
                    db.session.add(fabric_defect)
                    db.session.commit()
                    original_image = f"{defect_type}_{i}.jpg"
                    mask_image = f"{defect_type}_{i}_Mask.jpg"
                    boundary_image = f"{defect_type}_{i}_boundary.jpg"
                    defect_images[defect_type].append((original_image, mask_image, boundary_image))
    
        flag_check = False
        return render_template('report.html', fabric_id=fabric_id, total_defects=total_defects,
                               date_added=today_date, defect_types=defect_types, defect_images=defect_images,title=title)
    else:
        title = "Supervision"
        form = UploadFileForm()
        if form.validate_on_submit():
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            session['video_path'] = file_path
        return render_template('supervision.html',title=title,form = form)

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
