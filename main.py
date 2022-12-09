from flask import Flask, request, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy import Column, Integer, String
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)

app.secret_key = 'some-secret_key'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'data.db')
app.config["JWT_SECRET_KEY"] = 'secret-key'
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']

db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database created!")


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("Database dropped!")


@app.cli.command('db_seed')
def db_seed():

    test_user = User(first_name='Apurva',
                     last_name='Yadav',
                     email='something@gmail.com',
                     password='1234567890')

    db.session.add(test_user)
    db.session.commit()
    print('database_seeded')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        test = User.query.filter_by(email=email).first()
        if test:
            flash("Email already exists", category='error')
        else:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            password = request.form['password']
            user = User(first_name=first_name, last_name=last_name, password=password, email=email)
            db.session.add(user)
            db.session.commit()
            flash("profile created successfully", category='success')
            return render_template('login.html')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        test = User.query.filter_by(email=email, password=password).first()
        if test:
            access_token = create_access_token(identity=email)
            tabl = pd.DataFrame()
            return render_template('upload.html', access_token=access_token, tabl=tabl )
        else:
            flash("Bad email or password. Please try again", category='error')

    return render_template('login.html')


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["input_file"]
        if file:
            filename = secure_filename(file.filename)
            df = pd.read_csv(file, index_col=False, sep=';|,|/t')
            return render_template('upload.html', tabl=df, filename=filename)
    return render_template('upload.html')


@app.route('/', methods=['GET', 'POST'])
def home_page():
    return render_template('base.html')


# database models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


if __name__ == '__main__':
    app.run(debug=True)



