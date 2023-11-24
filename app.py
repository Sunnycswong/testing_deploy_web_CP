import os
import json
import flask

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_cors import CORS
import logging

import export_doc
import extract_info


app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


# route for healthcheck
@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    # Returning an api for showing in reactjs
    return {"status": "OK"}


# route for extracting information from RM notes
@app.route('/generate', methods=['POST'])
def extract_rm_notes():

    data = request.get_json()
    logging.info("API request param:", data)
    #client_name = data["client_name"]
    section_name = data["section_name"]
    # Client_name = Client_name + "_rm_note.json"
    rm_note_txt = data["rm_note_txt"]
    output_json = extract_info.run_first_gen(section_name, rm_note_txt) 

    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)


@app.route('/regen', methods=['POST'])
def regen():
    data = request.get_json()
    logging.info("API request param:", data)
    section_name = data["section_name"]
    previous_paragraph = data["previous_paragraph"]
    rm_instruction = data["rm_instruction"]
    output_json = extract_info.regen(section_name, previous_paragraph, rm_instruction)
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(output_json)

# return the docx document 

@app.route('/export', methods=['POST'])
def export_doc():
    data = request.get_json()
    logging.info("API request param:", data)
    client_name = data["client_name"]
    consolidated_text = data["consolidated_text"]
    export_doc.create_docx(client_name, consolidated_text)

    return 


if __name__ == '__main__':
   app.run()
