#!flask/bin/python
import os
import time

from flask import url_for
from werkzeug.utils import secure_filename

from flask import redirect

from flask import flash

from flask import request

from flask import abort

import main
import json

import word_info
from db_helper import learn_word, get_quiz_words
from word_extractor import extract_words
from flask import Flask

app = Flask(__name__)
MAX_FILE_SIZE = 16 * 1024 * 1024
# UPLOAD_FOLDER = '/path/to/the/uploads'
# set as part of the config
SECRET_KEY = 'many random bytes'
ALLOWED_EXTENSIONS = {'vtt'}
app.config['UPLOAD_FOLDER'] = "uploads/"


def quizify(words_list):
    quiz_candidates = get_quiz_words()

    for x in words_list:
        if x['lemma'] in quiz_candidates:
            x['quiz'] = 'true'
        else:
            x['quiz'] = 'false'
    return words_list


def get_words_info(final_words):
    result_list = list()
    for x in final_words:
        dict_record = dict()
        dict_record['word'] = x[0]
        dict_record['lemma'] = x[1]
        dict_record['pos'] = x[2]
        dict_record['start_time'] = str(x[3].total_seconds() * 1000)
        dict_record['end_time'] = str(x[4].total_seconds() * 1000)
        dict_record['translation'] = word_info.get_translation(x[1])
        dict_record['definition'] = word_info.get_defenition(x[1], x[2])
        dict_record['example'] = word_info.get_example(x[1])
        result_list.append(dict_record)
    return result_list


@app.route('/check_later', methods=['GET'])
def check_word_later():
    if 'word' not in request.args:
        return "Submit word"
    learn_word(request.args['word'])
    return "Succes!"


@app.route('/subdata', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            "No file send"

        if 'difficulty' not in request.args:
            return "No difficulty parameter"

        diffculty = int(request.args['difficulty'])
        if diffculty > 5 or diffculty < 1:
            return "Improper difficulty: must be [1;5]"

        if 'words' not in request.args:
            return "No words parameter"

        words_quantity = int(request.args["words"])
        if words_quantity < -1:
            return "Invalid words quantity"

        # check if the post request has the file part
        if 'file' not in request.files:
            "No file send"
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            return "Invalid filename"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            words_list = extract_words(filename, words_quantity, diffculty)
            advices = get_words_info(words_list)
            quiz_words = quizify(advices)
            return json.dumps(quiz_words)

    return "Only POST queries"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', debug=True)
