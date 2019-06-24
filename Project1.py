import os
from flask import Flask, render_template, request, flash, redirect, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug import SharedDataMiddleware
import statistics
from werkzeug.utils import secure_filename
import re

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})



db = SQLAlchemy(app)

class Formdata(db.Model):
    __tablename__ = 'ekgdata'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    filename = db.Column(db.String)
    data = db.Column(db.Integer)

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data

db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('dataFiles.html')
            #redirect(url_for('uploaded_file',
                    #                filename=filename))
    return render_template('home.html')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/uploadData')
def uploadData():
    return render_template('uploadData.html')


@app.route('/dataFiles')
def dataFiles():
    list = os.listdir("uploads")
    if(len(list) != db.session.query(Formdata).count()):
        for i in list:
            if(db.session.query(Formdata).filter_by(filename = i).count() == 0):
                name = i
                path = "uploads/" + name
                data = open(path).read()
                fd=Formdata(name, data)
                db.session.add(fd)
                db.session.commit()
    fd=db.session.query(Formdata).all()

    return render_template('dataFiles.html', formdata=fd)

@app.route('/processed', methods = ["GET", "POST"] )
def processed():
    if request.method == 'POST':

        path = "uploads/" + request.form['selectFile']
        data = open(path).read()
        #split data

        data = re.findall(r'[0-9]+', data)
        data_list = []

        
        for i in range(int(len(data)/2)):

            data_list.append([int(data[2*i]), int(data[(2*i)+1])])




    return render_template('processed.html', data_list = data_list)


if __name__ == "__main__":
    app.debug = True
    app.run()