import os
import pathlib
from turtle import color
from flask import Flask, redirect, session, abort, request, render_template, flash,  url_for, send_file
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
from flask import flash
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from datetime import date
from werkzeug.utils import secure_filename
import psycopg2 
import psycopg2.extras
import re 

from tensorflow.keras.utils import load_img
from tensorflow.keras.utils import img_to_array
import tensorflow as tf
import numpy as np
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg 


app = Flask(__name__)

model = tf.keras.models.load_model('model.h5')
perdict_list = []

app.secret_key = "CodeSpecialist.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "366834887588-nr8s3qb0phf47d57hf7apl7v80juca3c.apps.googleusercontent.com"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes= ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback")
conn = psycopg2.connect(host='localhost', database='DB', user='postgres', password='1212', port='5432')

UPLOAD_FOLDER = 'static/images/'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS =set(['png','jpg','jpeg','gif'])

class DataStore():
    mail = None
    img = None
    name = None
    acc_type =None
data = DataStore()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route('/',methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('Email', None)
   # Redirect to login page
   return redirect('/')

@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template("Home.html")


@app.route('/signin') 
def signin():  
    return render_template("sign in.html")


@app.route('/signin_btn', methods=['GET', 'POST'])
def signin_btn ():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'Email' in request.form and 'Password' in request.form:
        Email = request.form['Email']
        data.mail=Email
        Password = request.form['Password']

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (Email,))
       
        # Fetch one record and return result and split img path
        account = cursor.fetchone()
        m = str(account['image_path']).split("/")
        imag = "/".join(m[1:])
        data.img=imag
        user_name = account['full_name']
        data.name = user_name
        user_acc = int(account['role_id'])

        if user_acc == 1:
            user_acc ='Patient'

        elif user_acc == 2:
            user_acc = 'Doctor'

        elif user_acc == 3:
            user_acc = 'Hospital'

        data.acc_type = user_acc

        if account:
            if Email == account['email']:
                if Password == account['pass']:
                    return render_template("Home.html", image=imag, name= user_name, role = user_acc)
                else:
                # Account doesnt exist or username/password incorrect
                    flash('Incorrect email/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect email/password')
 
        return render_template('sign in.html')


@app.route('/rhome',methods=['GET', 'POST']) 
def rhome():  
    return render_template("Home.html",image=data.img, name= data.name, role= data.acc_type)

@app.route('/payment',methods=['GET', 'POST']) 
def payment():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
       
            Mail=request.form['mail']
            cursor.execute('SELECT * FROM users WHERE email = %s', (Mail,))
            account = cursor.fetchone()
            today = date.today()
            cursor.execute("INSERT INTO  transactions (tran_date, u_id) VALUES (%s, %s)", (today, account['u_id']))
            conn.commit()
            return render_template("Home.html", image=data.img, name= data.name, role= data.acc_type)
    else:      
        return render_template("Payment.html") 
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('sign up.html')

@app.route('/signup_process',methods=['GET', 'POST']) 
def home(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'FullName' in request.form and 'Password' in request.form and 'Email' in request.form:
        # Create variables for easy access
        FullName = request.form['FullName']
        Email = request.form['Email']
        Password = request.form['Password']
        NickName=request.form['NickName']
        user_acc=request.form['job']
        phone= request.form['phone']
        Age=request.form['Age']
        Gender=request.form['Gender']

        if user_acc=='Patient':
            user_acc = 1

        elif user_acc=='Doctor':
            user_acc = 2

        elif user_acc=='Hospital':
            user_acc = 3

        if Gender=='Female':
            Gender='f'
        
        else:
            Gender='m'
            
        cursor.execute('SELECT * FROM users WHERE full_name = %s', (FullName,))
        account = cursor.fetchone()
       
        if account:
            flash('Account already exists!')
            
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', Email):
                flash('Invalid email address!')

        elif not re.match(r'[A-Za-z0-9]+', FullName):
                flash('Username must contain only characters and numbers!')
        
        elif not FullName or not Password or not Email:
                flash('Please fill out the form!')
        
        else:
                # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (role_id,full_name, email, pass,age,phone,gender,nick_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (user_acc,FullName, Email,Password,Age,phone,Gender,NickName))
                
            conn.commit()
                
    return render_template("sign in.html")


@app.route('/improve_ux', methods=['GET', 'POST']) 
def improve_ux():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST' :
        Q1=request.form['q1']
        Q2=request.form['q2']
        Q3=request.form['q3']
        Q4=request.form['q4']
        Q5=request.form['q5']
        
        cursor.execute("INSERT INTO improve_ux(q1,q2,q3,q4,q5) VALUES (%s,%s,%s,%s,%s)", (Q1,Q2,Q3,Q4,Q5))
       
        conn.commit()
        return render_template("Home.html", image=data.img, name=data.name, role= data.acc_type)   
    else:
        
        
        return render_template("improve ux.html")

@app.route('/profile') 
def profile():
    return render_template('profile.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    profileImage = request.files['profileImage']
    image_path = 'static/Profiles/' + profileImage.filename
    profileImage.save(image_path)
    return image_path
  
@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/edit',methods=['GET', 'POST'])  
def edit():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
    Email = request.form['email']
    cursor.execute('SELECT * FROM users WHERE email = %s', (Email,))
    account = cursor.fetchone()
    full_name = request.form['full_name']
    nick_name = request.form['nick_name']
    password= request.form['password']
    phone= request.form['phone']
    user_photo = upload_image()
    user_acc = request.form['job']
    
    data.acc_type = user_acc
    user_name = account['full_name']
    data.name = user_name
    
    if user_acc=='Patient':
        user_acc = 1

    elif user_acc=='Doctor':
        user_acc = 2

    elif user_acc=='Hospital':
        user_acc = 3

    if account:
        cursor.execute( " UPDATE users SET role_id = %s,full_name = %s,nick_name = %s,pass = %s,image_path = %s,phone = %s WHERE email= %s",
        (user_acc,full_name, nick_name, password, user_photo, phone,account["email"],))
        conn.commit()
        cursor.close()

    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (Email,))
    account = cursor.fetchone()
    m = str(account['image_path']).split("/")
    cursor.close()
    imag = "/".join(m[1:])
    data.img=imag  
    return render_template('Home.html', image=data.img, name=data.name, role= data.acc_type)    


@app.route('/contact',methods=['GET', 'POST'])
def contacts():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST' :
        name=request.form['name']
        email=request.form['email']
        message=request.form['message']
        
        cursor.execute("INSERT INTO support_tickets (names,email,mssg) VALUES (%s,%s,%s)", (name,email,message))
       
        conn.commit()
        return render_template("Home.html", image=data.img, name= data.name, role= data.acc_type)   
    else:
        return render_template("contact us.html")
 

@app.route('/contact_guest',methods=['GET', 'POST'])
def contact():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if request.method == 'POST' :
        name=request.form['name']
        email=request.form['email']
        message=request.form['message']
        cursor.execute("INSERT INTO support_tickets (names,email,mssg) VALUES (%s,%s,%s)", (name,email,message))
       
        conn.commit()
        return render_template("index.html")   
    else:
        return render_template("contact_guest.html")


@app.route('/pricing_guest',methods=['GET', 'POST'])
def pricing_guest():
    return render_template("Pricing Guest.html")


@app.route('/q_test/')
def q_test():
   return render_template('q_test_guest.html') 

@app.route('/q_test_user')
def q_test_user():
   return render_template('q_test.html') 

@app.route('/q_result/')
def q_result():
   return render_template('Q-result.html') 


@app.route('/pricing',methods=['GET', 'POST'])
def pricing():
    return render_template('pricing.html', image=data.img, name= data.name, role= data.acc_type)


@app.route('/tools',methods=['GET'])
def tools():
    return render_template("Tools.html", image=data.img, name= data.name, role= data.acc_type)


@app.route('/tools',methods=['GET', 'POST'])
def prdeict():
    if request.method == 'POST':
        imageFile = request.files['imagefile']
        image_path = './images/' + imageFile.filename
        imageFile.save(image_path)


        image = load_img(image_path, target_size=(456, 456))
        image = img_to_array(image)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        pred = model.predict(image)
        res = pred[0].tolist()

        if len(perdict_list) > 0:
            perdict_list.clear()

        for i in range(len(res)):
            perdict_list.append(float("{0:.2f}".format(res[i])))

    return render_template("Tools.html", prediction = plotting(), image=data.img, name= data.name, role= data.acc_type)

@app.route('/plotting')
def plotting():
    classes  = ['Actinic Keratosis','Basel Carcinoma', 'Benign Keratosis', 
                'Dermatofibroma', 'Melanoma', 'Melanocytic Nevi', 
                'Squamous Carcinoma', 'Unknown Lesion', 'Vascular Lesions']
    fig = plt.figure(figsize = (8, 6))
    orange = '#D94B2E'
    aqua   = '#32CCFF'
    xx= plt.xticks(rotation=25, horizontalalignment="center" , color="white")
    xx= plt.yticks(color="white")
    xx= plt.bar(classes, perdict_list, color = aqua, width = 0.5)
    xx[4].set_color(orange)
    plt.legend(xx[4:6], ['Melanoma', 'Others'])
    plt.rc('font', size = 8)
    


    canvas = FigureCanvasAgg(fig)
    img = io.BytesIO()
    fig.savefig(img, transparent = True)
    img.seek(0)

    return send_file(img, mimetype='img/png')

@app.route('/gallery')
def gallery():
    return render_template("gallery.html", image=data.img, name= data.name, role= data.acc_type)


if __name__ =='__main__':  
    app.run(debug = True)  