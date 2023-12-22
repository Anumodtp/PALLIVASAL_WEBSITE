from flask import Flask, redirect, url_for, render_template, request, send_from_directory, session ,flash , Response
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from datetime import timedelta
from flask_session import Session
from flask_login import current_user ,LoginManager
from db import db_init, db

from models import Details , Places , LocalWorkforce, Spices , WhereToStay,Plantation,Spiceproducts, Transportation

from sqlalchemy.sql.expression import update
# login_manager = LoginManager()
# from sqlalchemy import text


with open('config.json', 'r') as c:
    data = json.load(c)["data"]

local_server=True    

app = Flask(__name__)

app.secret_key = 'dgw^9ej(l4vq_06xig$vw+b(-@#00@8l7jlv77=sq5r_sf3nu'
app.permanent_session_lifetime = timedelta(minutes=2)
app.config['DB_SERVER'] = data['local_uri']


bcrypt=Bcrypt(app)

def truncate_string(input_string, max_length):
    if len(input_string) > max_length:
        return input_string[:max_length]
    else:
        return input_string
    
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DB_SERVER']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)
# db = SQLAlchemy()
# db.init_app(app)

# # Function that initializes the db and creates the tables
# def db_init(app):
#     db.init_app(app)

#     # Creates the logs tables if the db doesnt already exist
#     with app.app_context():
#         db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/view')
def view():
    return render_template('view.html')

def authenticate_user(contact, password):
    list = Details.query.filter_by(contact=contact).first()
    if list.accept == 1 and list.password == password:
        return True, list.sno
    else:
        return False, None


# @app.route('/userdash_submit', methods=['GET', 'POST'])
# def userdash_submit():

@app.route('/userdash/<int:sno>', methods=['GET', 'POST'])
def userdash(sno):
    if(request.method == 'POST'):
        entry1 = LocalWorkforce.query.join(Details).filter(Details.sno == sno).first()
        entry2 = Spices.query.join(Details).filter(Details.sno == sno).first()
        entry3 = WhereToStay.query.join(Details).filter(Details.sno == sno).first()
        entry4 = Plantation.query.join(Details).filter(Details.sno == sno).first()
        entry5 = Transportation.query.join(Details).filter(Details.sno == sno).first()
        # entry4 = Spiceproducts.query.join(Spices).filter().first()
 
        if entry1:
            entry1.whatsapp_number = request.form.get('whatsapp')
            entry1.remuneration_details = request.form.get('remuneration')
            entry1.technical_qualifications = request.form.get('technical')
            entry1.years_of_exp = request.form.get('exp')
            pic = request.files['img']
            
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry1.img=filename   

            db.session.commit()

        elif entry2:
            entry2.name=request.form.get('shop')
            entry2.location=request.form.get('loc')
            entry2.contact2=request.form.get('contact2')
            pic = request.files['img']
            
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry2.img=filename   
            db.session.commit()

        elif entry3:
                entry3.name = request.form.get('name')
                entry3.location = request.form.get('location')
                entry3.description = request.form.get('description')
                entry3.facilities = request.form.get('facilities')
                entry3.no_of_rooms = request.form.get('rooms')
                entry3.services = request.form.get('services')
                img1 = request.files['img1']

                if img1:
                    filename = secure_filename(img1.filename)
                    if (request.method == 'POST'):    
                        img1.save(os.path.join('static', 'uploads', filename))
                        # mimetype = pic.mimetype
                else:
                    filename = None
                entry3.img1 = filename
                db.session.commit()

        elif entry4:
            entry4.name=request.form.get('name')
            entry4.address=request.form.get('address')
            entry4.location=request.form.get('location')
            entry4.contact=request.form.get('contact')
            entry4.Crops=request.form.get('Crops')
            pic = request.files['img']
            if pic:
                filename = secure_filename(pic.filename)
                pic.save(os.path.join('static', 'uploads', filename))
            else:
                filename = None
            entry4.img=filename   
            db.session.commit()

        elif entry5:
            entry5.cost=request.form.get('cost')
            entry5.Trip_available=request.form.get('Trip_available')
            entry5.Pick_up_and_Drop=request.form.get('Pick_up_and_Drop')
            entry5.Duration=request.form.get('Duration')
            entry5.vehicle=request.form.get('vehicle')
            entry5.no_of_persons=request.form.get('no_of_persons')
            entry5.Things_to_carry=request.form.get('Things_to_carry')
            pic = request.files['img']
            
            # if not pic:
            #     return 'No image uploaded!', 400
            filename = secure_filename(pic.filename)
            entry5.img=filename   
            pic.save(os.path.join('static', 'uploads', filename))
            db.session.commit()

    list = Details.query.filter_by(sno=sno , accept = 1).all()
    localworkforce = LocalWorkforce.query.filter_by(details_id = sno).all()
    wheretostay = WhereToStay.query.filter_by(details_id = sno).all()
    spices = Spices.query.filter_by(details_id = sno).all()
    spiceproducts = Spiceproducts.query.filter_by().all()
    plantation = Plantation.query.filter_by(details_id = sno).all()
    return render_template('userdash.html', list = list , local = localworkforce , stay = wheretostay , spices = spices , prod = spiceproducts , plant = plantation)

@app.route('/register', methods = ['GET','POST'])
def register():
    if(request.method == 'POST'):
        name = request.form.get('name')
        address = request.form.get('address')
        contact = request.form.get('contact')
        if len(contact)!=10:
            flash('Invalid Mobile number. Please try with a different one.')
            return redirect(url_for('register'))
        x=Details.query.filter_by(contact=contact).first()
        if x is not None:
            flash('Account exists with this number. Please try with a different one.')
            return redirect(url_for('register'))
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password==confirm:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        else:
            flash('Password combination does not match. Please try again.')
            return redirect(url_for('register'))
        
        email = request.form.get('email')
        if '@' not in email and '.' not in email:
            flash('Invalid email format. Please try again.')
            return redirect(url_for('register'))
        services = request.form.get('services')
    
    # @app.route('/upload', methods=['POST'])
    # def upload():
    #     pic = request.files['pic']
    #     if not pic:
    #         return 'No pic uploaded!', 400

    #     filename = secure_filename(pic.filename)
    #     mimetype = pic.mimetype
    #     if not filename or not mimetype:
    #         return 'Bad upload!', 400

    #     img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    #     db.session.add(img)
    #     db.session.commit()

    #     return 'Img Uploaded!', 200
        pic = request.files['file1']
        if not pic:
            flash('No Image uploaded. Please try again.')
            return redirect(url_for('register'))
        filename = secure_filename(pic.filename)
        entry = Details(name=name, address=address, contact=contact , password=hashed_password, email=email, services=services ,date=datetime.now().date() , file=filename)
        if (request.method == 'POST'):    
            pic.save(os.path.join('static', 'uploads', filename))
        db.session.add(entry)
        db.session.commit()
        
        return render_template('confirm.html')
    return render_template('register.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user_contact = request.form.get('contact')
        user_password = request.form.get('password')
        details=Details.query.filter_by(contact=user_contact).first()
        if details and bcrypt.check_password_hash(details.password, user_password):
            return redirect(url_for('userdash', sno=details.sno)) 
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('signin'))  
            
        # try:
        #     result, sno = authenticate_user(user_contact, user_password)
        # except:
        #     flash('Invalid credentials. Please try again.')
        #     return redirect(url_for('signin')) 
        
        # if result:
        #     return redirect(url_for('userdash', sno=sno))  
        # else:

    list = Details.query.filter_by(accept = 1)
    return render_template('signin.html', list=list)

@app.route("/admin",  methods = ['GET', 'POST'])
def admin():
    error = None

    if request.method == "POST":
        session.permanent = True
        username = request.form.get("username", "")
        userpass = request.form.get("password", "")
        if username == data.get('admin_username') and userpass == data.get('admin_password'):
            session['user'] = username
            return render_template('admin_dash.html', data=data)

        error = data.get('error')

    if session.get('user') == data.get('admin_username'):
        return render_template('admin_dash.html', data=data)

    return render_template('admin.html', data=data, error=error)
# @app.route("/")
# def index():
#     if not session.get("user_name"):
#         return redirect("/login")
#     return render_template('welcome.html')

# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         session["user_name"] = request.form.get("name")
#         return redirect("/")
#     return render_template("login.html")

# @app.route("/logout")
# def logout():
#     session["user_name"] = None
#     return redirect("/")
# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)


@app.route('/logout')
def logout():
    if session.get('user') == data.get('admin_username'):
        session.pop('user')
    return redirect('/admin')


@app.route('/admin_view/<int:sno>/<string:slug>' , methods = ["GET" , "POST"])
def admin_view(sno ,slug):
    list = Details.query.filter_by(sno = sno ,slug=slug ,accept = None).first()                
    return render_template('admin_view.html' , list=list )

@app.route('/admin_dash')
def admin_dash():
    return render_template('admin_dash.html')

@app.route('/admin_accept', methods=['GET' , 'POST'])
def admin_accept():
    # Get the row id from the request
    # Query the row to be moved from Table1
    # row = Details.query.get(row_id)
    # stmt = update(Details).where(Details.accept == None).values(accept = 1)
    row_id = request.form.get('row_id')
    details_instance = Details.query.filter_by(sno=row_id).first()
    details_instance.accept = 1
    service=details_instance.services
    db.session.commit()
    if service in ["Carpentary works" , 'Plumbing services' , 'Electrical works']:
        new_local_workforce = LocalWorkforce(details_id=details_instance.sno)
        db.session.add(new_local_workforce)
        db.session.commit()
    elif service=='Spices outlet':
        spiceobj = Spices(details_id=details_instance.sno)
        db.session.add(spiceobj)
        db.session.commit()
    elif service in ["Home stay" , "Resorts" , "Tent Camping" , "Dormitories"]:
        new_wheretostay = WhereToStay(details_id=details_instance.sno)
        db.session.add(new_wheretostay)
        db.session.commit()
    elif service=='plantation':
        plantation = Plantation(details_id=details_instance.sno)
        db.session.add(plantation)
        db.session.commit()

    elif service in ["Jeep safari" , 'Taxi service' , 'Bike Rental' , "Auto Rickshaw" , 'Car Rental']:
        transport = Transportation(details_id=details_instance.sno)
        db.session.add(transport)
        db.session.commit()

    # session.query(Details).filter(Details.accept == None , sno = row_id).update({Details.accept: 1})
    # stmt = Details.update().where(Details.accept == None).values(accept = 1)
    # if row:
    #     Details(acce)

    # if row:
    #     # Create a new row in Table2 with the same data
    #     new_row = Accept(name=row.name, address=row.address, contact=row.contact , password=row.password, confirm=row.confirm, email=row.email, services=row.services ,date=datetime.now(), slug=row.slug , file = row.file )  # Modify this based on your table columns
    #     # Add the new row to Table2
    #     db.session.add(new_row)
    #     # Delete the row from Table1
    #     db.session.delete(row)
    #     # Commit the changes to the database
    # db.session.commit(stmt)
    return render_template('admin_accept.html')
    # else:
    #     return 'Row not found'

@app.route('/admin_reject', methods=['POST'])    
def admin_reject():
    row_id2 = request.form.get('row_id2')
    row = Details.query.filter_by(sno = row_id2).first()
    filename = row.file
    if row:
        try:
            os.remove(os.path.join('static', 'uploads', filename))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return render_template('admin_reject.html')


@app.route('/approved_remove', methods=['POST'])    
def approved_remove():
    row_id2 = request.form.get('row_id2')
    row = Details.query.filter_by(sno = row_id2).first()
    filename = row.file
    if row:
        try:
            os.remove(os.path.join('static', 'uploads', filename))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return render_template('admin_reject.html')

@app.route('/requests', methods=["GET" ,"POST"])
def requests():
    if "user" in session:
        list = Details.query.filter_by(accept = None).all()
        return render_template('requests.html', list=list)
    else:
        return render_template('admin.html')

@app.route('/approved_app', methods=["GET" ,"POST"])
def approved_app():
    list = Details.query.filter_by(accept = 1).all()
    return render_template('approved_app.html', list=list)

@app.route('/approved_view/<int:sno>/<string:slug>' , methods = ["GET" , "POST"])
def approved_view(sno ,slug ):
    list = Details.query.filter_by(sno = sno ,slug=slug ,accept = 1).first()                
    return render_template('approved_view.html' , list=list )

@app.route('/edit_pages' , methods=["GET" ,"POST"])
def edit_pages():
    if(request.method == 'POST'):
        name = request.form.get('name')
        description = request.form.get('desc')
        map = request.form.get('map')

        if 'files[]' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        num = len(files)
        file_names = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_names.append(filename)
                file.save(os.path.join('static', 'uploads', filename))

        if(num == 1):
            entry = Places(name=name, description = description ,  map = map , img1 = file_names[0] )
        elif(num == 2):
            entry = Places(name=name, description = description ,  map = map , img1 = file_names[0] ,img2 = file_names[1] )
        elif(num == 3):
            entry = Places(name=name, description = description ,  map = map ,img1 = file_names[0] ,img2 = file_names[1], img3 = file_names[2] )
        elif(num == 4):
            entry = Places(name=name, description = description ,  map = map ,img1 = file_names[0] ,img2 = file_names[1], img3 = file_names[2], img4 = file_names[3] )
        elif(num == 5):
            entry = Places(name=name, description = description ,  map = map ,img1 = file_names[0] ,img2 = file_names[1], img3 = file_names[2], img4 = file_names[3] ,img5 = file_names[4])
        # elif(num > 5):
       

        if(num<=5):
            db.session.add(entry)
        else:
            flash('only a maximum of 5 should be uploaded!')
        db.session.commit()
            
    return render_template('edit_pages.html' )

@app.route('/confirm')
def confirm():
    return render_template('confirm.html')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def upload_image():
# 	if 'files[]' not in request.files:
# 		flash('No file part')
# 		return redirect(request.url)
# 	files = request.files.getlist('files[]')
# 	file_names = []
# 	for file in files:
# 		if file and allowed_file(file.filename):
# 			filename = secure_filename(file.filename)
# 			file_names.append(filename)
# 			file.save(os.path.join('static', 'uploads', filename))

# 	return render_template('upload.html', filenames=file_names)


@app.route('/tour')
def tour():
    list = Places.query.filter_by().all()
    return render_template('tour.html' , list = list)

@app.route('/place/<int:id>', methods = ["GET" , "POST"])
def place(id):
    list = Places.query.filter_by(id = id ).first()                
    return render_template('place.html' , list = list)

@app.route('/added_places', methods=["GET" ,"POST"])
def added_places():
    list = Places.query.filter_by().all()
    return render_template('addedplaces.html', list=list)

@app.route('/addedplace_detail/<int:id>' , methods = ["GET" , "POST"])
def addedplace_detail(id):
    list = Places.query.filter_by(id = id ).first()                
    return render_template('addedplace_detail.html' , list=list )

@app.route('/place_remove', methods=['POST'])    
def place_remove():
    row_id2 = request.form.get('row_id2')
    row = Places.query.filter_by(id = row_id2).first()
    img1 = row.img1
    img2 = row.img2
    img3 = row.img3
    img4 = row.img4
    img5 = row.img5
    if row:
        try:
            os.remove(os.path.join('static', 'uploads', img1))
            os.remove(os.path.join('static', 'uploads', img2))
            os.remove(os.path.join('static', 'uploads', img3))
            os.remove(os.path.join('static', 'uploads', img4))
            os.remove(os.path.join('static', 'uploads', img5))
        except:
            pass
        db.session.delete(row)
        db.session.commit()     
    return redirect(url_for('added_places'))


@app.route('/where_to_stay')
def where_to_stay():
    list = Details.query.filter_by(accept = 1).all()
    return render_template('where_to_stay.html', list = list)


@app.route('/dormitories')
def dormitories():
    list = Details.query.filter_by( accept = 1).all()
    info = WhereToStay.query.filter_by().all()
    return render_template('dormitories.html', info = info , list = list )

@app.route('/view_dormitories/<int:id>')
def view_dormitories(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_dormitories.html' , list = list , info = info)


@app.route('/home_stay')
def home_stay():
    list = Details.query.filter_by( accept = 1).all()
    info = WhereToStay.query.filter_by().all()
    return render_template('home_stay.html', info = info , list = list )

@app.route('/view_homestay/<int:id>')
def view_homestay(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_homestay.html' , list = list , info = info)


@app.route('/resorts')
def resorts():
    list = Details.query.filter_by( accept = 1).all()
    info = WhereToStay.query.filter_by().all()
    return render_template('resorts.html', info = info , list = list )

@app.route('/view_resorts/<int:id>')
def view_resorts(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_resorts.html' , list = list , info = info)

@app.route('/tent_camping')
def tent_camping():
    list = Details.query.filter_by( accept = 1).all()
    info = WhereToStay.query.filter_by().all()
    return render_template('tent_camping.html', info = info , list = list )

@app.route('/view_tent/<int:id>')
def view_tent_camping(id):
    list = Details.query.filter_by(sno = id , accept = 1)
    info = WhereToStay.query.filter_by(details_id = id)
    return render_template('view_tent.html' , list = list , info = info)

@app.route('/local_workforce')
def local_workforce():
    list = Details.query.filter_by(accept = 1).all()
    return render_template('local_workforce.html' , list = list)

@app.route('/view_localworkforce/<int:sno>', methods=['GET', 'POST'])
def view_localworkforce(sno):
    list = Details.query.filter_by(sno = sno , accept = 1)
    info = LocalWorkforce.query.filter_by(details_id = sno)  
    return render_template('view_localworkforce.html' , list = list, info = info )


@app.route('/plantation_crops')
def plantation_crops():
    list1 = Plantation.query.filter_by().all()
    return render_template('plantation_crops.html',list=list1)

@app.route('/spices')
def spices():
    list = Details.query.filter_by().all()
    return render_template('spices.html',list=list)

@app.route('/spices_view')
def spices_view():
    lis1=Details.query.filter_by(services='Spices outlet').all()
    lis2 = Spices.query.filter_by().all()
    lis3=Spiceproducts.query.filter_by().all()
    lis4 = Spiceproducts.query.with_entities(Spiceproducts.product).all()
    product_list = [item.product for item in lis4]
    product_list=list(set(product_list))
    print(product_list)
    return render_template('spices_view.html',lis1=lis1,lis2=lis2,lis3=lis3,product_list=product_list)

@app.route('/view_spices/<int:sno>', methods=['GET', 'POST'])
def view_spices(sno):
    lis1 = Details.query.filter_by(sno = sno , accept = 1)
    lis2 = Spices.query.filter_by(details_id = sno)  
    lis3=Spiceproducts.query.filter_by().all()
    return render_template('view_spices.html' ,lis2=lis2,lis1=lis1,lis3=lis3 )

@app.route('/addspiceproduct/<int:sno>', methods=['GET', 'POST'])
def addspiceproduct(sno):
    if(request.method == 'POST'):
        product=request.form.get('product')
        price=request.form.get('price')
        details_instance = Details.query.filter_by(sno=sno).first()
        details_instance_spices = Spices.query.filter_by(details_id=details_instance.sno).first()
        spiceobj = Spiceproducts(product=product,price=price,details_id=details_instance_spices.local_id)
        db.session.add(spiceobj)
        db.session.commit()
        # entry3=Spiceproducts()
        # db.session.add(entry3)
        # db.session.commit()

    list = Details.query.filter_by(sno=sno , accept = 1).all()
    list1=Spices.query.filter_by().all()
    list2=Spiceproducts.query.filter_by().all()
    return render_template('add_spices.html', list = list ,list1=list1,list2=list2)


# @app.route('/deletespiceproduct/<int:sno>', methods=['GET', 'POST'])
# def deletespiceproduct(sno):
#     if(request.method == 'POST'):
        
    #     details_instance = Details.query.filter_by(sno=sno).first()
    #     details_instance_spices = Spices.query.filter_by(details_id=details_instance.sno).first()
        # spiceobj = Spiceproducts(details_id=sno).all()
        # db.session.delete(spiceobj)
        # db.session.commit()
    
    # list = Details.query.filter_by(sno=sno , accept = 1).all()
    # list1=Spices.query.filter_by().all()
    # list2=Spiceproducts.query.filter_by().all()
    # return render_template('addspices.html')

    

@app.route('/transport')
def transport():
    list = Details.query.filter_by(accept = 1).all()
    return render_template('transport.html', list = list)

@app.route('/transport_view/<string:services>', methods=["GET" ,"POST"])
def transport_view(services):
    list = Details.query.filter_by(services = services , accept = 1)
    return render_template('transport_view.html', list=list)

@app.route('/transport_detail_view/<int:sno>', methods=["GET" ,"POST"])
def transport_detail_view(sno):
    list = Details.query.filter_by(sno = sno , accept = 1)
    list1=Transportation.query.filter_by(details_id = sno).first()
    return render_template('view_transportation.html', list=list,list1=list1)

@app.route('/transport_view/busview')
def busview():
    return render_template('bus.html')
# @app.route('/taxiservices')
# def taxiservices():
#     list = Accept.query.filter_by().all()
#     for item in list:
#         if item.services=='Taxi Services':
#             x=x.append(item)    
#     return render_template('transport_view.html', list = x)


# @app.route('/taxiservices/<string:services>', methods=["GET" ,"POST"])
# def taxiservices(services):
#     list = Accept.query.filter_by(services=services)   
#     return render_template('transport_view.html', list = list)


# @app.route('/CarRental')
# def CarRental():
#     list = Accept.query.filter_by(services='Car Rental')
#     return render_template('transport_view.html', list = list)

@app.route('/image/<string:img>', methods=['GET', 'POST'])
def image(img):
    return render_template('image.html' , img = img )

@app.route('/<text>', methods=['GET', 'POST'])
def all_routes(text):
    return redirect(url_for('index'))


if __name__ == ("__main__"):
    app.run(debug=True)
