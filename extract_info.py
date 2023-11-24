#%%
## Import Library
import copy
import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswParameters,
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
)
from azure.storage.blob import BlobServiceClient
from langchain.chains import LLMChain
from langchain.llms import AzureOpenAI 
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import CosmosDBChatMessageHistory
import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import json

from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
#from langchain.retrievers import AzureCognitiveSearchRetriever
from langdetect import detect
from langchain.prompts import PromptTemplate
import re
# Create chain to answer questions
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import ConversationalRetrievalChain

# Import Azure OpenAI
from langchain.llms import AzureOpenAI 
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage

import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswParameters,
    PrioritizedFields,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticSettings,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
)

from azure.storage.blob import BlobServiceClient
from pypdf import PdfReader
from langchain.schema import Document
import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
#import textwrap
import logging
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import json
from docx import Document as DocxDocument
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re


index_name = "credit-proposal"
search_service = "gptdemosearch"
search_api_key = "PcAZcXbX2hJsxMYExc2SnkMFO0D94p7Zw3Qzeu5WjYAzSeDMuR5O"
storage_service = "creditproposal"
storage_api_key = "hJ2qb//J1I1KmVeDHBpwEpnwluoJzm+b6puc5h7k+dnDSFQ0oxuh1qBz+qPB/ZT7gZvGufwRbUrN+ASto6JOCw=="
connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage_service};AccountKey={storage_api_key}"

doc_intell_endpoint = "https://doc-intelligence-test.cognitiveservices.azure.com/"
doc_intell_key = "9fac3bb92b3c4ef292c20df9641c7374"

# set up openai environment
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"

os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
os.environ["AZURE_INDEX_NAME"] = index_name

# Core LLM call funcition

def cap(match):
    return(match.group().capitalize())


def load_json(json_path):
    with open(json_path, "r" ,encoding="utf-8") as f:
        data = json.load(f)
    return data

'''
    You could follow the below extraction example format to output the answer.
    example (Keyword: example):
    {example}

    3. The example (Keyword: proposal_example) above is just for your reference only to improve your theme, you must not directly copy the content in the examples

'''

#This funcition is to prepare the rm note in desired format for web, call by app.py
def web_extract_RM(section, rm_note_txt):
    hierarchy_file_name = "config/hierarchy_v2.json"

    hierarchy_dict_list = load_json(hierarchy_file_name)

    hierarchy_dict_list = hierarchy_dict_list["content"]

    prompt_template_for_extracting_rm_note = """
    Read the following context, aggregate the context and answer the input question based on the aggregate context (Keyword: Question):
    
    Please Just based on the 
    context: {rm_note}

    ======
    Question: {question}
    ======

    Follow the instruction below:
    1. Please provide your answer in English
    2. Do not start your answer with "Based on the given information"
    3. If possible, try to expand the information provided from the RM
    4. Do not create any figures by make-up 
    5. Please provide [N/A] as answer if you cannot find any relevant information from the given context. Example Format: [N/A]
    
    Take a deep breath and work on this step by step
    """
    rm_prompt_template = PromptTemplate(template=prompt_template_for_extracting_rm_note, input_variables=["rm_note", "question",])# "example",])

    llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0.1,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")

    #"example": dictionary["Example"],

    output_dict_list = []
    for dictionary in hierarchy_dict_list:
        if dictionary["Section"] == section:
            chain = LLMChain(llm=llm_rm_note, prompt=rm_prompt_template)
            dictionary["Value"] = chain({"rm_note":rm_note_txt, "question": dictionary["Question"]})['text']
            dictionary["Value"] = dictionary["Value"].replace("Based on the given information, ", "")
            if "[N/A]" in dictionary["Value"]:
                dictionary["Value"] = ""
            output_dict_list.append(dictionary)

    # Create Json file 
    # output_json_name = "GOGOVAN_hierarchy_rm_note.json"
    # json.dump(output_dict_list, open(output_json_name, "w"), indent=4)

    return output_dict_list

'''
        ======
        Example: (Keyword: proposal_example)
        {example}
        ======

'''


def first_gen_template():
    proposal_proposal_template_text = """
        Read the input json for this section carefully and aggregate the content of "Value" key:

        Please follow the format in content of "example" key to output the answer
        But please do not include any content in "example" key to output the answer, as it just use as reference


        Read the input json for this section carefully and aggregate the content of "Value" key
        please based on the content in "Value" key to output the answer
        Input JSON:
        {input_json}
        
        Then write paragraph(s) based on the above aggregrated context 

        Rules you need to follow:
        1. Don't mention the word "RM Note" and "Component", and don't mention you held a meeting with the client! Instead, you shall say "It is mentioned that"
        2. Don't mention the source of your input (i.e. RM Note (Keyword: rm_note), example, document)
        3. Don't justify your answers
        4. Don't provide suggestion or recommendation by yourself
        5. Provide your answer in English
        6. Breake it to multi-paragraphs if one single paragraph consists of more than 100 words
        7. In the same paragraph, don't input line breaks among the sentences
        8. Don't start with your answer by a title. You must start your paragraph immediately
        9. The example (Keyword: proposal_example) above is just for your reference only to improve your theme, you must not directly copy the content in the examples
        10. If possible, you can use point-form, tables to provide your answer
        11. Don't introduce what this section includes

        Guidance when you do not have the information:
        1. When you don't have the specific information or you need further information (Keyword: further_info), you have to write it in the following format: [RM please helps provide the further information of (Keyword: further_info)], where please supplement the information you need here.
        2. You must not create the information by yourself if you don't have relevant information
        3. You cannot say "It's unclear that", please refer to point 1 for the formatting for requesting further information

        Take a deep breath and work on this step by step
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_json"])


    return prompt_template_proposal


def regen_template():
    proposal_proposal_template_text = """
        Read the previous_paragraph, RM instruction for this section carefully:
        
        Please follow the previous paragraph and RM instruction and return a summarize paragraph in human readable form:
        {previous_paragraph}

        ======================================

        Please follow the RM instruction to edit the previous_paragraph and return a summarize paragraph in human readable form:
        You could treat the RM instruction as prompt.
        RM instruction:
        {rm_instruction}
        ======================================

        Then write paragraph(s) based on the above aggregrated context

        Rules you need to follow:
        1. Don't mention the word "RM Note" and "Component", and don't mention you held a meeting with the client! Instead, you shall say "It is mentioned that"
        2. Don't mention the source of your input (i.e. RM Note (Keyword: rm_note), example, document)
        3. Don't justify your answers
        4. Don't provide suggestion or recommendation by yourself
        5. Provide your answer in English
        6. Breake it to multi-paragraphs if one single paragraph consists of more than 100 words
        7. In the same paragraph, don't input line breaks among the sentences
        8. Don't start with your answer by a title. You must start your paragraph immediately
        9. The example (Keyword: proposal_example) above is just for your reference only to improve your theme, you must not directly copy the content in the examples
        10. If possible, you can use point-form, tables to provide your answer
        11. Don't introduce what this section includes

        Guidance when you do not have the information:
        1. When you don't have the specific information or you need further information (Keyword: further_info), you have to write it in the following format: [RM please helps provide the further information of (Keyword: further_info)], where please supplement the information you need here.
        2. You must not create the information by yourself if you don't have relevant information
        3. You cannot say "It's unclear that", please refer to point 1 for the formatting for requesting further information

        Take a deep breath and work on this step by step
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["previous_paragraph", "rm_instruction"])


    return prompt_template_proposal


# to first generate 
def first_generate(section_name, input_json):


    """
    A core function to generate the proposal per section

    Parameters:
    -----------
    prompt: str
    Prompt text for instructing the output based on RM prompt

    rm_note: str
    It contains the information from the RM

    example: str
    Input example for GPt to take it as an example

    """
    #.format(content=content, section=section, context=context)
    
    prompt_template_proposal = first_gen_template()

    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal
    )

    drafted_text = chain({"input_json": input_json
                    ,})['text']
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")
    
    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(cap, drafted_text2)

    
    rm_fill_values = []
    additional_info_values = []
    lines = drafted_text2.split("\n")
    for line in lines:
        match = re.search(r"\[RM .+?\]", line)
        if match:
            rm_fill = match.group(0)
            # Remove the '[RM ' at the start and ']' at the end, then append
            rm_fill = rm_fill.replace('[RM ', '', 1)
            rm_fill = rm_fill[:-1] # remove the closing bracket
            rm_fill_values.append(rm_fill)
            line = line.replace(rm_fill, "")
                
        # Check for "Please provide further information" in the line
        if "Please provide further information" in line:
            # Append the whole line
            additional_info_values.append(line)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)
    additional_info_text = ' '.join(additional_info_values)

    # Combine rm_fill_text and additional_info_text into one string
    combined_text = rm_fill_text + ' ' + additional_info_text

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM fill" : combined_text,
    }
    #output the result
    return output_json

def run_first_gen(section, rm_note_txt):

    extract_json = web_extract_RM(section ,rm_note_txt)
    output_json = first_generate(section, extract_json)

    return output_json

def regen(section_name, previous_paragraph, rm_instruction):
    prompt_template_proposal = regen_template()

    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal
    )

    drafted_text = chain({"previous_paragraph": previous_paragraph
                    ,"rm_instruction":rm_instruction})['text']
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")
    
    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(cap, drafted_text2)

    rm_fill_values = []
    additional_info_values = []
    lines = drafted_text2.split("\n")
    for line in lines:
        match = re.search(r"\[RM .+?\]", line)
        if match:
            rm_fill = match.group(0)
            # Remove the '[RM ' at the start and ']' at the end, then append
            rm_fill = rm_fill.replace('[RM ', '', 1)
            rm_fill = rm_fill[:-1] # remove the closing bracket
            rm_fill_values.append(rm_fill)
            line = line.replace(rm_fill, "")
                
        # Check for "Please provide further information" in the line
        if "Please provide further information" in line:
            # Append the whole line
            additional_info_values.append(line)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)
    additional_info_text = ' '.join(additional_info_values)

    # Combine rm_fill_text and additional_info_text into one string
    combined_text = rm_fill_text + ' ' + additional_info_text

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM fill" : combined_text,
    }
    #output the result
    return output_json
