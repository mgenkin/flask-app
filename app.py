from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas

app = Flask(__name__)
try:
    posts = pandas.read_csv("static/posts.csv")
except ValueError:
    posts = pandas.DataFrame()
current_post = pandas.DataFrame(index=[datetime.now()])


@app.route('/')
def home():
    return redirect('/welcome')


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
            global current_post
            current_post['Post'] = request.form['datapt']
            return redirect('/exit')
        else:
            error = 'Bad request: '+repr(request.form)
            return render_template('secondpage.html',
                                   error=error)


@app.route('/showdata')
def showdata():
    return render_template('showdata.html', data=posts.values[:, 0])


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


@app.route('/exit')
def exit():
    global posts
    global current_post
    posts = pandas.concat([posts, current_post])
    posts.to_csv("static/posts.csv")
    return redirect('/showdata')


if __name__ == '__main__':
    app.run(debug=True)
