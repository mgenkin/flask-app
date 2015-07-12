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
        if(os.path.isfile("static/breaks_in_story.txt")):
            self.breaks_in_story = [line.strip("\n").split(",") for line in open("static/breaks_in_story.txt","rb").readlines()]
        else:
            raise Exception("Fatal Error: breaks_in_story.txt is missing")
        self.test_num = 0
        self.current_score = 0
        self.task_path = -1
        self.anger = None
        self.question_num = 0
        self.last_score = -1
        self.story_num = 1
    def __repr__(self):
        return (str(self.data)+" data\n"+
                str(self.current_subject)+" current subject\n"+
                str(self.test_num)+" test\n"+
                str(self.current_score)+" score\n"+
                str(self.task_path)+" path\n"+
                str(self.anger)+" anger\n"+
                str(self.question_num)+" question"+
                str(self.breaks_in_story)+" breaks")

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
    return (True, True) #(passed, finished)


def make_sameroom_test(part):
    #todo get the choices and correct answer
    
    return redirect('/sameroom')


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

def make_story(part):
    if (os.path.isfile('static/path'+str(info.task_path)+'/story'+str(part)+'.txt')):
        story_text = open('static/path'+str(info.task_path)+'/story'+str(part)+'.txt').read()
        return render_template('story.html', story_text=story_text)
    else:
        exit()
        return redirect('/')

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
            return render_template('tryagain.html', score=str(info.last_score), passed="true", part="1")
        if finished:
            return render_template('tryagain.html', score=str(info.last_score), passed=None)
    return make_memory_test()



@app.route('/story<int:part>')
def story(part):
    global info
    print info
    if str(part) in info.breaks_in_story[info.task_path]:
        print "making sameroom test"
        return make_sameroom_test(part)
    else:
        print "making story"
        return make_story(part)

@app.route('/sameroom', methods=['GET', 'POST'])
def sameroom():
    if request.method == 'POST':
        use_sameroom_info(request.form)
        info.breaks_in_story[info.task_path].remove(request.form['part'])
        return redirect('/story'+request.form['part'])
    return render_template('sameroom.html', choices=["onion", "pizza"], correct_ans="yes", part=1)






if __name__ == '__main__':
    app.run(debug=True)