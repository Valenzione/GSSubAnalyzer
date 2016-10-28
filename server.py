#!flask/bin/python
import os
import time

from flask import url_for
from werkzeug.utils import secure_filename

from flask import redirect

from flask import flash

from flask import request

import main
import json
from word_extractor import extract_words, jsonify
from flask import Flask

app = Flask(__name__)
MAX_FILE_SIZE = 16 * 1024 * 1024
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['srt'])
app.config['UPLOAD_FOLDER'] = "uploads/"


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            words_list = extract_words(filename,5)
            return jsonify(words_list)
    return "Hey!"



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(debug=True)
