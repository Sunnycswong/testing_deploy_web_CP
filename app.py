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


# route for extracting information from RM notes
@app.route('/rm_note', methods=['POST'])
def extract_rm_notes():

    #hierarchy_file_name = "config/hierarchy.json"
    #schema_file_name = "config/schema.json"
    #hierarchy_dict_list = extract_rm_note.load_json(hierarchy_file_name)
    #schema_dict_list = extract_rm_note.load_json(schema_file_name)

    data = request.get_json()
    logging.info("API request param:", data)
    Client_name = data["client_name"]
    # Client_name = Client_name + "_rm_note.json"
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


# return the sector regen
# accept the json like this {"section": 'Client Background',"instruction":"Gogovan is requesting a credit facility of $60 million instead of $10 million"}
@app.route('/regen', methods=['POST'])
def regen():

    data = request.get_json()
    logging.info("API request param:", data)
    section = data["section"]
    prompt = data["instruction"]
    sector = proposal_gpt.edit_web_json(section, prompt)
    # Convert the JSON response to a JSON-serializable format    
    # Return the JSON response
    return jsonify(sector)


# return the docx document 
# accept json like this:
"""[
    {
        "Section": "Project Overview",
        "Component": [
            "Project Name",
            "Project Description",
            "Project Cost"
        ],
        "Prompt": "Write me an overview on the project based on the provided component",
        "Example": "The deal is referred by Pamfleet Group (\u201cPamfleet\u201d) and our relationship with it can be traced back to early 2006 when the OIC was with Hang Seng Bank.  After joining ICBC (Asia), OIC\u2019d tried a couple of time to cooperate with Pamfleet, but was in vain owing to the more aggressive offer given by Pamfleet\u2019s partner banks, like CITIC Ka Wah Bank.  However, due to ICBCA business scale, network plus OIC\u2019s marketing effort and cordial relationship, Pamfleet agreed to provide an industry / office acquisition project for our consideration.\n\nIn this project, Pamfleet is to cooperate with Angelo Gordon Group (\u201cAngelo Gordon\u201d), a US investment company dedicated to alternative investment to form a fund, which will be used to acquire Ever Gain Plaza located in Kwai Chung (the \u201cProperty\u201d) or the companies holding the Property.",
        "RM Note": "- Client Name: Gogovan\n- Project Name: The company/project name mentioned in the RM note is Gogovan.\n- Project Description: The project description for Gogovan is to support its expansion plans, technology investments, and working capital needs. The company aims to enter new markets, both domestically and internationally, to capture additional customer segments and increase market share. Gogovan also plans to invest in technology and infrastructure improvements to streamline operations, optimize delivery routes, and enhance overall efficiency. The proposed credit facility of $10 million will enable Gogovan to execute its growth strategy and maintain its competitive edge in the logistics and delivery industry.\n- Project Cost: The project cost for Gogovan's expansion plans, technology investments, and working capital needs is not mentioned in the RM note.\n",
        "Document": "",
        "GPT Output": "the client for this project is Gogovan, a company in the logistics and delivery industry. The project aims to support Gogovan's expansion plans, technology investments, and working capital needs. Gogovan intends to enter new markets, both domestically and internationally, in order to capture additional customer segments and increase its market share.\n\nTo achieve this, Gogovan plans to invest in technology and infrastructure improvements. These investments will help streamline operations, optimize delivery routes, and enhance overall efficiency. However, the specific project cost for Gogovan's expansion plans, technology investments, and working capital needs is not mentioned in the provided information.\n\nThe proposed credit facility of $10 million will enable Gogovan to execute its growth strategy and maintain its competitive edge in the logistics and delivery industry. This credit facility will provide the necessary financial support for Gogovan's expansion plans and technology investments.\n\nOverall, the project for Gogovan focuses on expanding its market presence, improving operational efficiency through technology investments, and securing the necessary working capital to support its growth strategy.",
        "Component_Text": "Project Name, Project Description, Project Cost"
    },
                     .... ]"""
@app.route('/docx', methods=['POST'])
def docx():

    data = request.get_json()
    logging.info("API request param:", data)
    json_data = data["json_data"]

    proposal_gpt.create_docx(json_data)

    return 



if __name__ == '__main__':
   app.run()

#%%
'''
def extract_RM():
    data = [{"Client_name":"gogovan", "rm_note_txt":"123"}]
    Client_name = data[0]["Client_name"]
    rm_note_txt = data[0]["rm_note_txt"]
    rm_notes = json.dump([rm_note_txt], open(Client_name, "w"), indent=4)
    print(rm_notes)
# %%
extract_RM()
# %%
'''
