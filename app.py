from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import csv
import pickle
import random
import os


class SubjectDataLine():
    # the data of the next CSV line to be added to the CSV document.

    def __init__(self):
        self.date = str(datetime.now().date())
        if(os.path.isfile("static/prog/count.p")):
            count = pickle.load(open("static/prog/count.p", 'rb'))
            self.id = count+1
        else:
            self.id = 0
        self.anger = None
        self.task = ""
        self.block = 1
        self.stimulus = ""
        self.response = ""
        self.RT = None
        self.correct_response = ""
        self.accuracy = None

    def __repr__(self):
        out_str = "SubjectDataLine Object.  Attributes: \n"
        attr_dict = self.get_attribute_dictionary()
        for key in attr_dict:
            out_str += str(key) + ": " + str(attr_dict[key]) + "\n"
        return out_str

    def get_attribute_dictionary(self):
        attr_dict = {
            "date": self.date,
            "id": self.id,
            "anger": self.anger,
            "task": self.task,
            "block": self.block,
            "stimulus": self.stimulus,
            "response": self.response,
            "RT": self.RT,
            "correct_response": self.correct_response,
            "accuracy": self.accuracy
        }
        return attr_dict

    def write_line(self):
        # add this line to the big CSV file
        attr_dict = self.get_attribute_dictionary()
        if os.path.isfile("static/data.csv"):
            with open("static/data.csv", "a") as csvfile:
                dw = csv.DictWriter(csvfile, fieldnames=attr_dict.keys())
                dw.writerow(attr_dict)
        else:
            with open("static/data.csv", 'w') as csvfile:
                dw = csv.DictWriter(csvfile, fieldnames=attr_dict.keys())
                dw.writeheader()
                dw.writerow(attr_dict)
        # re-initialize the object, keeping the attributes that represent the
        # subject
        id_num, date, anger = self.id, self.date, self.anger
        self.__init__()
        self.id, self.date, self.anger = id_num, date, anger
        #pickle id so we can increment it next time
        pickle.dump(self.id, open("static/prog/count.p", 'wb'))


def make_learn_question(current_task):
    global next_line
    assert next_line.task == "Learning Phase"
    letters = [u"A", u"B", u"C", u"D"]
    # we are making the question from the images stored in the images directory
    file_list = os.listdir("static/path"+str(current_task)+"/images")
    random.shuffle(file_list)
    choices = [img[:-4] for img in file_list[:4]]  # choose 4, cut the ".jpg"
    correct = random.randint(0, 3)
    img_src = "static/path" + \
        str(current_task) + "/images/" + choices[correct] + ".jpg"
    next_line.stimulus = choices[correct]
    next_line.correct_response = letters[correct]
    return choices, letters[correct], img_src

def process_line(story_line):
    is_question = (story_line.split("|")[0] == "Q")
    if is_question:
        line = story_line.split("|")[1:]
    else:
        line = story_line
    return is_question, line

# main application object
app = Flask(__name__)
# the next_line object collects the data that needs to be written to the
# next line
next_line = SubjectDataLine()
# randomly determine which task this subject will do first
current_task = int(random.random() > 0.5)
second_time_around = False

# display the intro page, which asks if the subject is angry
@app.route('/')
def home():
    return render_template('intro.html')


# terms and conditions page
@app.route('/terms', methods=['GET', 'POST'])
def terms():
    global next_line
    if request.method == 'POST':
        # if it's a post request, you must have come here from the intro page
        # so we need to save your anger state
        next_line.anger = (request.form['anger'] == u'1')  # boolean value
    return render_template('terms.html')


# memorize the map
@app.route('/map', methods=['GET', 'POST'])
def map():
    global current_task, next_line
    img_path = "static/path" + str(current_task) + "/map.jpg"
    return render_template('map.html', img_src=img_path)


# variables to keep track of for the learning phase
block, correct_ans = 0, ""
question_count, num_correct, just_got_ten = 0, 0, False
story = None


# learning phase, questions
@app.route('/learn', methods=['GET', 'POST'])
def learn():
    global current_task, next_line, block, question_count, num_correct, just_got_ten, correct_ans
    # if it's a post request, the subject just answered a question
    # so we need to check his/her answer and proceed accordingly
    if request.method == 'POST':
        next_line.response = request.form['answer']
        next_line.RT = request.form['RT']
        next_line.accuracy = int(next_line.response == unicode(correct_ans))
        num_correct += next_line.accuracy
        next_line.write_line()
        question_count += 1
        print question_count, num_correct
        if question_count == 10:
            return redirect('/tryagain')
    next_line.task = "Learning Phase"
    next_line.block = block
    choices, correct_ans, img_src = make_learn_question(current_task)
    return render_template('learn.html', img_src=img_src, choices=choices)


@app.route('/tryagain')
def tryagain():
    global num_correct, just_got_ten, question_count, block
    block += 1
    passed = (just_got_ten and (num_correct == 10))
    score = num_correct
    just_got_ten = (num_correct == 10)
    question_count, num_correct = 0, 0
    return render_template("tryagain.html", score=score, passed=passed)


story_f = open("static/path"+str(current_task)+"/story.txt", 'rt')
story_line = ""
is_question = False
@app.route('/story', methods=['GET', 'POST'])
def story():
    global current_task, next_line, story_f, story_line, is_question
    next_line.block = 0
    next_line.task = "TASK"+str(current_task)
    if request.method == 'POST':
        # a post request must contain the answer to a question
        next_line.response = request.form['answer']
        next_line.RT = request.form['RT']
        next_line.accuracy = int(next_line.response == next_line.correct_response)
        next_line.write_line()
    if int(story_f.name[11]) != current_task:
        story_f = open("static/path"+str(current_task)+"/story.txt", 'rt')
    story_line = story_f.readline().rstrip('\n')
    if story_line == "":
        return  redirect('/finish')
    is_question = (story_line.split("|")[0] == "Q")
    if is_question:
        q_info = story_line.split("|")[1:]
        next_line.stimulus = q_info[1]+"-"+q_info[2]
        next_line.correct_response = q_info[0]
        return render_template("story.html", probes=q_info[1:], is_question=is_question) 
    return render_template("story.html", story_text=story_line, is_question=is_question)


@app.route('/finish')
def finish():
    global current_task, second_time_around, block
    block = 1
    if second_time_around:
        return render_template("finish.html", second_time_around=True)
    second_time_around=True
    current_task = (1-current_task)
    return render_template("finish.html", second_time_around=False)

# run the app
if __name__ == '__main__':
    app.run(debug=True)