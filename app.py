from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/data.db'
db = SQLAlchemy(app)


class DataPt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datapt = db.Column(db.String(80), unique=True)

    def __init__(self, datapt):
        self.datapt = datapt

    def __repr__(self):
        return 'DataPt %r' % self.datapt

db.create_all()


@app.route('/')
def home():
    return "Hello, Worffghld!"  # return a string


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


@app.route('/firstpage',  methods=['GET', 'POST'])
def firstpage():
    if request.method == 'GET':
        return render_template('firstpage.html',
                               image_source='static/eximg.jpg', error=None)
    elif request.method == 'POST':
        if request.form['continue'] == u'true':
            return redirect('/secondpage')
        else:
            error = 'Bad request: '+repr(request.form)
            return render_template('firstpage.html',
                                   image_source='static/eximg.jpg',
                                   error=error)


@app.route('/secondpage', methods=['GET', 'POST'])
def secondpage():
    if request.method == 'GET':
        return render_template('secondpage.html')  # render a template
    elif request.method == 'POST':
        if request.form['datapt'] is not None:
            db.session.add(DataPt(request.form['datapt']))
            db.session.commit()
            print DataPt
            print DataPt.query.all()
            return render_template('secondpage.html',
                                   data=DataPt.query.all())
        else:
            error = 'Bad request: '+repr(request.form)
            return render_template('secondpage.html',
                                   error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != 'admin' or
                request.form['password'] != 'admin'):
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/')
    return render_template('login.html', error=error)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
