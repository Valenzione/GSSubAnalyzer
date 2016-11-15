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
from word_extractor import extract_words, jsonify
from flask import Flask

app = Flask(__name__)
MAX_FILE_SIZE = 16 * 1024 * 1024
# UPLOAD_FOLDER = '/path/to/the/uploads'
# set as part of the config
SECRET_KEY = 'many random bytes'
ALLOWED_EXTENSIONS = {'vtt'}
app.config['UPLOAD_FOLDER'] = "uploads/"


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
        if words_quantity < 0:
            return "Words must be posiive number"

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            return "Invalid filename"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            words_list = extract_words(filename, words_quantity)
            return jsonify(words_list)

    return "Only POST queries"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug=True)
