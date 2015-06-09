from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pandas
import pickle
import random
import os


class SessionInfo():
    def __init__(self):
        if(os.path.isfile("static/data.p")):
            self.data = pandas.read_pickle("static/data.p")
        else:
            self.data = pandas.DataFrame()
        self.current_subject = pandas.DataFrame(index=[datetime.now()])
        if(os.path.isfile("static/room_lists.p")):
            self.room_lists = pickle.load("static/room_lists.p")
        else:
            self.room_lists = [["cheddar", "swiss", "provolone", "havarti", "brie"], ["iris", "tulip", "rose", "dandelion", "daffodil"]]
            #raise Exception("Fatal Error: room dictionaries are missing")
        self.test_num = 0
        self.current_score = 0
        self.task_path = -1
        self.anger = None
        self.question_num = 0
    def __repr__(self):
        return (str(self.data)+" data\n"+
                str(self.current_subject)+" current subject\n"+
                str(self.test_num)+" test\n"+
                str(self.current_score)+" score\n"+
                str(self.task_path)+" path\n"+
                str(self.anger)+" anger\n"+
                str(self.question_num)+" question")

app = Flask(__name__)
info = SessionInfo()

def exit():
    global info
    info.data = pandas.concat([info.data, info.current_subject])
    info.data.to_pickle("static/data.p")
    info.data.to_csv("static/data.csv")
    info = SessionInfo()


def use_sameroom_info(form):
    global info
    if form['correctness'] == u'correct':
        info.current_subject['sameroom'] = 1
    else:
        info.current_subject['sameroom'] = 0


def use_memory_test_info(form):
    global info
    print info
    passed, finished = False, False
    info.question_num += 1
    if form['correctness'] == u'correct':
        info.current_score += 1
    if  info.question_num >= 10:
        finished = True
        testlabel = 'test'+str(info.test_num)
        info.current_subject[testlabel] = info.current_score
        info.test_num += 1
        info.question_num = 0
        if info.current_score == 10 and info.last_score == 10:
            passed = True
        info.last_score = info.current_score
        info.current_score = 0 
    return (passed, finished)


def make_memory_test():
    global info
    things = info.room_lists[info.task_path]
    random.shuffle(things)
    img_name = things[0]
    correct_ans = random.randint(0,3)
    choices = ["","","",""]
    for i in range(1,5):
        choices[i-1] = things[i]
    choices[correct_ans] = img_name
    return render_template('memorytest.html',
                               image_source='static/path'+str(info.task_path)+'/images/'+img_name+'.jpg', choices=choices, correct_ans=correct_ans)

@app.route('/')
def home():
    return redirect('/welcome')


#the first page seen by the subject.  asks the experimenter to enter whether or not the subject is angry.
@app.route('/welcome', methods = ['GET', 'POST'])
def welcome():
    global info
    if request.method == 'GET':
        return render_template('welcome.html')
    if request.method == 'POST':
        info.anger = request.form['anger']
        info.current_subject['anger'] = request.form['anger']
        info.task_path = random.randint(0,1)
        return redirect('/viewmap')


@app.route('/viewmap',  methods=['GET', 'POST'])
def viewmap():
    global info
    if request.method == 'GET':
        return render_template('viewmap.html',
                               image_source='static/path'+str(info.task_path)+'/images/map.jpg')
    if request.method == 'POST':
        if request.form['continue'] == u'true':
            return redirect('/memorytest')


@app.route('/memorytest', methods=['GET', 'POST'])
def memorytest():
    if request.method == 'POST':
        passed, finished = use_memory_test_info(request.form)
        if passed and finished:
            return render_template('tryagain.html', score=str(info.last_score), passed="true")
        if finished:
            return render_template('tryagain.html', score=str(info.last_score), passed=None)
    return make_memory_test()



@app.route('/congrats')
def congrats():
    return render_template('congrats.html')


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

@app.route('/story')
def story():
    global info
    story_text = open('static/path'+str(info.task_path)+'/story.txt').read()
    return render_template('story.html', story_text=story_text)

@app.route('/sameroom', methods=['GET', 'POST'])
def sameroom():
    if request.method == 'POST':
        use_sameroom_info(request.form)
        exit()
        return redirect('/')
    return render_template('sameroom.html', )






if __name__ == '__main__':
    app.run(debug=True)
