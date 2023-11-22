import os
import json
import flask

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from flask_cors import CORS
import logging

import extract_document
import extract_rm_note
import proposal_gpt


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


# route for RM_NOTES
@app.route('/RM_note', methods=['POST'])
def extract_RM():

    hierarchy_file_name = "hierarchy.json"
    schema_file_name = "schema.json"
    hierarchy_dict_list = extract_rm_note.load_json(hierarchy_file_name)
    schema_dict_list = extract_rm_note.load_json(schema_file_name)

    data = request.get_json()
    logging.info("API request param:", data)
    Client_name = data["Client_name"]
    Client_name = Client_name + "_rm_note.json"
    rm_note_txt = data["rm_note_txt"]
    hierarchy_dict_list, rm_prompt_template, llm_rm_note, rm_note_txt = extract_rm_note.web_extract_RM(rm_note_txt)
    hierarchy_rm_note = extract_rm_note.extract_rm_note(hierarchy_dict_list=hierarchy_dict_list
                , rm_note=rm_note_txt 
                , rm_prompt_template=rm_prompt_template
                , llm=llm_rm_note
                , output_json_name=Client_name)
    
    schema_with_rm_note = proposal_gpt.update_schema_json(schema_dict_list, hierarchy_rm_note, update_key='RM Note')
    first_RM_version = proposal_gpt.gen_first_web_and_json(schema_with_rm_note)

    
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(first_RM_version)

@app.route('/regen', methods=['POST'])
def regen():
    data = request.get_json()
    logging.info("API request param:", data)
    question = data["question"]
    sessionId = data["sessionId"]
    
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    #return jsonify(json_response)

if __name__ == '__main__':
   app.run()

#%%

def extract_RM():
    data = [{"Client_name":"gogovan", "rm_note_txt":"123"}]
    Client_name = data[0]["Client_name"]
    rm_note_txt = data[0]["rm_note_txt"]
    rm_notes = json.dump([rm_note_txt], open(Client_name, "w"), indent=4)
    print(rm_notes)
# %%
extract_RM()
# %%
