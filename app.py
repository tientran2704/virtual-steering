from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import math
import keyinput
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Configure MySQL connection
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# MySQL configurations
try:
    # Kết nối với tài khoản root và mật khẩu 27042004
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:27042004@localhost/virtual_steering'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Test database connection
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    engine.connect()
    print("Database connection successful!")
except SQLAlchemyError as e:
    print(f"Error connecting to database: {str(e)}")
    raise

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variables for camera and hand tracking
camera = None
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
font = cv2.FONT_HERSHEY_SIMPLEX

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # Increased length for MySQL
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def process_hand_gestures(image, results):
    imageHeight, imageWidth, _ = image.shape
    co = []
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            for point in mp_hands.HandLandmark:
                if str(point) == "HandLandmark.WRIST":
                    normalizedLandmark = hand_landmarks.landmark[point]
                    pixelCoordinatesLandmark = mp_draw._normalized_to_pixel_coordinates(
                        normalizedLandmark.x,
                        normalizedLandmark.y,
                        imageWidth, 
                        imageHeight
                    )
                    try:
                        co.append(list(pixelCoordinatesLandmark))
                    except:
                        continue

    if len(co) == 2:
        xm, ym = (co[0][0] + co[1][0]) / 2, (co[0][1] + co[1][1]) / 2
        radius = 150
        try:
            m = (co[1][1]-co[0][1])/(co[1][0]-co[0][0])
        except:
            return image

        a = 1 + m ** 2
        b = -2 * xm - 2 * co[0][0] * (m ** 2) + 2 * m * co[0][1] - 2 * m * ym
        c = xm ** 2 + (m ** 2) * (co[0][0] ** 2) + co[0][1] ** 2 + ym ** 2 - 2 * co[0][1] * ym - 2 * co[0][1] * co[0][0] * m + 2 * m * ym * co[0][0] - 22500
        xa = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        xb = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        ya = m * (xa - co[0][0]) + co[0][1]
        yb = m * (xb - co[0][0]) + co[0][1]

        if m != 0:
            ap = 1 + ((-1/m) ** 2)
            bp = -2 * xm - 2 * xm * ((-1/m) ** 2) + 2 * (-1/m) * ym - 2 * (-1/m) * ym
            cp = xm ** 2 + ((-1/m) ** 2) * (xm ** 2) + ym ** 2 + ym ** 2 - 2 * ym * ym - 2 * ym * xm * (-1/m) + 2 * (-1/m) * ym * xm - 22500
            try:
                xap = (-bp + (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                xbp = (-bp - (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                yap = (-1 / m) * (xap - xm) + ym
                ybp = (-1 / m) * (xbp - xm) + ym
            except:
                return image

        cv2.circle(img=image, center=(int(xm), int(ym)), radius=radius, color=(195, 255, 62), thickness=15)
        cv2.line(image, (int(xa), int(ya)), (int(xb), int(yb)), (195, 255, 62), 20)

        if co[0][0] > co[1][0] and co[0][1] > co[1][1] and co[0][1] - co[1][1] > 65:
            keyinput.release_key('s')
            keyinput.release_key('d')
            keyinput.press_key('a')
            cv2.putText(image, "Turn left", (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.line(image, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif co[1][0] > co[0][0] and co[1][1] > co[0][1] and co[1][1] - co[0][1] > 65:
            keyinput.release_key('s')
            keyinput.release_key('d')
            keyinput.press_key('a')
            cv2.putText(image, "Turn left", (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.line(image, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif co[0][0] > co[1][0] and co[1][1] > co[0][1] and co[1][1] - co[0][1] > 65:
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.press_key('d')
            cv2.putText(image, "Turn right", (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.line(image, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif co[1][0] > co[0][0] and co[0][1] > co[1][1] and co[0][1] - co[1][1] > 65:
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.press_key('d')
            cv2.putText(image, "Turn right", (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.line(image, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)
        else:
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.release_key('d')
            keyinput.press_key('w')
            cv2.putText(image, "keep straight", (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            if ybp > yap:
                cv2.line(image, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
            else:
                cv2.line(image, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)

    elif len(co) == 1:
        keyinput.release_key('a')
        keyinput.release_key('d')
        keyinput.release_key('w')
        keyinput.press_key('s')
        cv2.putText(image, "keeping back", (50, 50), font, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

    return image

def generate_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            # Process hand gestures and update frame
            frame = process_hand_gestures(frame, results)
            
            # Flip the image horizontally for a selfie-view display
            frame = cv2.flip(frame, 1)
            
            # Convert back to BGR for OpenCV
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    logout_user()
    return redirect(url_for('index'))

@app.route('/start_steering')
@login_required
def start_steering():
    return render_template('steering.html')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
@login_required
def stop_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 