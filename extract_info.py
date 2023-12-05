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
from langchain.chains import SimpleSequentialChain
from langchain.chains import SequentialChain

# Setting credit
index_name = "credit-proposal"
search_service = "gptdemosearch"
search_api_key = "PcAZcXbX2hJsxMYExc2SnkMFO0D94p7Zw3Qzeu5WjYAzSeDMuR5O"
storage_service = "creditproposal"
storage_api_key = "hJ2qb//J1I1KmVeDHBpwEpnwluoJzm+b6puc5h7k+dnDSFQ0oxuh1qBz+qPB/ZT7gZvGufwRbUrN+ASto6JOCw=="
connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage_service};AccountKey={storage_api_key}"

doc_intell_endpoint = "https://doc-intelligence-test.cognitiveservices.azure.com/"
doc_intell_key = "9fac3bb92b3c4ef292c20df9641c7374"


# set up openai environment - Jay
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"


# set up openai environment - Ethan
#os.environ["OPENAI_API_TYPE"] = "azure"
#os.environ["OPENAI_API_BASE"] = "https://lwyethan-azure-openai-test-01.openai.azure.com/"
#os.environ["OPENAI_API_VERSION"] = "2023-05-15"
#os.environ["OPENAI_API_KEY"] = "ff96d48045584cb9844fc70e5b802918"


# Setting up ACS -Jay
#os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
#os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
#os.environ["AZURE_INDEX_NAME"] = index_name


# Core LLM call funcition

def cap(match):
    return(match.group().capitalize())

# load json data function
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
def web_extract_RM(section, rm_note_txt, client):
    hierarchy_file_name = "config/hierarchy_v2.json"

    hierarchy_dict_list = load_json(hierarchy_file_name)

    hierarchy_dict_list = hierarchy_dict_list["content"]

    prompt_template_for_extracting_rm_note = """
        For this task, you'll be generating a response based on given information. Please read the client name and the RM's notes, then answer the question provided.

        **Client Name**
        {client_name}

        **RM Notes**
        {rm_note}

        **Question**
        {question}

        While crafting your response, please observe these guidelines:

        1. Provide your answer in English.
        2. Expand on the information provided by the RM where possible.
        3. Do not invent or exaggerate information. Stick to what's provided.
        4. If no relevant information is available, respond with "[N/A]".
        5. Do not include notes about the source of your information in your answer.

        Remember, approach this task calmly and methodically.
        """
    
    rm_prompt_template = PromptTemplate(template=prompt_template_for_extracting_rm_note, input_variables=["rm_note", "question", "client_name"])# "example",])

    
    # set up openai environment - Jay
    llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")


    # set up openai environment - Ethan
    """llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    #"example": dictionary["Example"],

    output_dict_list = []
    for dictionary in hierarchy_dict_list:
        if dictionary["Section"] == section:
            chain = LLMChain(llm=llm_rm_note, prompt=rm_prompt_template)
            dictionary["Value"] = chain({"rm_note":rm_note_txt, "question": dictionary["Question"], "client_name": client })['text']
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
        Carefully consider the following guidelines while working on this task:

        **Note: Write as comprehensively as necessary to fully address the task. There is no maximum length.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".

        **Client Name**
        {client_name}
    
        **Example for Reference**
        {example}
    
        **Input Information**
        {input_info}


        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Executive Summary
def section_1_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Executive Summary**
        Please provide a concise, pointed summary of the recommendation based on the above information. 
        Conclude the recommendation with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Client Request
def section_2_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Client Request**
        Please provide a concise summary of the Client Request based on the above information. 
        Conclude the Client Request with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Shareholders and Group Structure
def section_3_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Project Details**
        Please provide a concise summary of the Project Details based on the above information. 
        Conclude the Project Details with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

# Project Details
def section_4_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Project Details**
        Please provide a concise summary of the Project Details based on the above information. 
        Conclude the Project Details with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])

    return prompt_template_proposal

#  Industry / Section Analysis
def section_5_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Industry / Section Analysis**
        Please provide a concise summary of the Industry / Section Analysis based on the above information. 
        Conclude the Industry / Section Analysis with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Management
def section_6_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Management**
        Please provide a concise summary of the Management based on the above information. 
        Conclude the Management with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Financial Information of the Borrower
def section_7_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        
        **Reminder:** Your response must include information about the equity to debt ratio, Net income, and Return on Equity (ROE) of the borrower. If this information is not provided, make sure to ask the RM for it using the format: "[RM Please help provide further information on Keyword ]". 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Financial Information of the Borrower**
        Please provide a concise summary of the Financial Information of the Borrower based on the above information. 
        Conclude the Financial Information of the Borrower with a statement about the proposed loan facility.
        
        If specific information is missing, use this format: "[RM Please help provide further information on Keyword]". Do not invent information or state that something is unclear. 
        Avoid mentioning any lack of specific information in the output.
        Remember to approach this task one step at a time and to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Other Banking Facilities
def section_8_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        **Reminder:** Your response must include Other Banking Facilities of the borrower. If this information is not provided, make sure to ask the RM for it using the format: "[RM Please help provide further information on Keyword ]". 

        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Other Banking Facilities**
        Please provide a concise summary of the Other Banking Facilities based on the above information. 
        Conclude the Other Banking Facilities with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Opinion of the Relationship Manager
def section_9_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 


        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Opinion of the Relationship Manager**
        Please provide a concise summary of the Opinion of the Relationship Manager based on the above information. 
        Conclude the Opinion of the Relationship Manager with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# Summary of Recommendation
def section_10_template():
    proposal_proposal_template_text = """
        Read this task step by step at a time and take a long breathe.
        Carefully consider the following guidelines while working on this task, Stick strictly to factual and verifiable information.:

        **Note: Write concise in bullet point form, no more than two rows in each bullet points.**

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 


        **Client Name**
        {client_name}

        **Example for Reference**
        {example}

        **Input Information**
        {input_info}

        **Summary of Recommendation**
        Start your recommendation with this line: 'In the view of the above, we recommend the proposed loan facility for management approval.' 
        Please provide a concise, pointed summary of the recommendation based on the above information. 
        This should be a brief, 200-word summary in point form. Skip any initial discussions, and start with the final recommendations immediately.         
        Conclude the recommendation with a statement about the proposed loan facility.
        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["input_info", "client_name", "example"])


    return prompt_template_proposal

# template for regeneration
def regen_template():
    proposal_proposal_template_text = """
        To complete this task, carefully consider the previous paragraph and the RM's instructions. Your task is to edit and summarize the previous paragraph according to the instructions provided.

        **Note: Write as comprehensively as necessary to fully address the task. There is no maximum length.**

        **Previous Paragraph**
        {previous_paragraph}

        **RM Instructions**
        {rm_instruction}

        When crafting your response, adhere to the following guidelines:

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.

        If specific information is missing, use the following format: "[RM Please provide further information on Keyword ]". Do not invent information or state that something is unclear. 
        Do not mention any lack of specific information in the output.

        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["previous_paragraph", "rm_instruction"])


    return prompt_template_proposal

def review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.

        **Input Paragraph**
        {first_gen_paragraph}

        Double check the Input Paragraph does not contains any content from 'example'.

        **Example**
        {example}

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["first_gen_paragraph", "example"])

    return prompt_template_proposal

def regenerate_review_prompt_template():
    proposal_proposal_template_text = """
        To complete this task. Your task is to review and edit the Input paragraph according to the instructions provided.

        **Input Paragraph**
        {re_gen_paragraph}

        1. Base your content on the client name and the input_info provided. Do not include content from 'example' in your output - it's for reference only.
        2. Avoid mentioning "RM Note", "Component", or any meetings with the client. Instead, phrase your information as "It is mentioned that".
        3. Do not mention the source of your input, justify your answers, or provide your own suggestions or recommendations.
        4. Your response should be in English and divided into paragraphs. If a paragraph exceeds 100 words, break it down into smaller sections.
        5. Don't include line breaks within sentences in the same paragraph.
        6. Start your paragraph directly without a heading.
        7. You can use point form or tables to present your answer, but do not introduce what the section includes.
        8. Avoid phrases like "Based on the input json" or "it is mentioned".
        9. Please generate responses without using any subjective language or phrases that might express sentiments or personal judgments such as 'unfortunately'.
        10. Please generate responses that do not invent any numbers or statistics. You may only use figures if they are explicitly mentioned in the provided content.
        11. Do not add disclaimers or state the source of your information in your response.
        12. If specific information is missing or not provided in the input information, return text at the end by follow this format: "[RM Please help provide further information on Keyword ]". Do not invent information or state that something is unclear. 

        
        If specific information is missing, follow this format: "[RM Please help provide further information on Keyword]". Do not invent information or state that something is unclear. 
        Make assumptions where necessary, but do not mention any lack of specific information in the output.
        Take this task one step at a time and remember to breathe.
        """
    prompt_template_proposal = PromptTemplate(template=proposal_proposal_template_text, input_variables=["re_gen_paragraph"])

    return prompt_template_proposal


# function to perform first generation of the paragraph
def first_generate(section_name, input_json, client):


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
    # For each section, gen content based on its prompt.
    if section_name == "Executive Summary":
        prompt_template_proposal = section_1_template()
    elif section_name == "Client Request":
        prompt_template_proposal = section_2_template()
    elif section_name == "Shareholders and Group Structure":
        prompt_template_proposal = section_3_template()
    elif section_name == "Project Details":
        prompt_template_proposal = section_4_template()    
    elif section_name == "Industry / Section Analysis":
        prompt_template_proposal = section_5_template()
    elif section_name == "Management":
        prompt_template_proposal = section_6_template()
    elif section_name == "Financial Information of the Borrower":
        prompt_template_proposal = section_7_template()
    elif section_name == "Other Banking Facilities":
        prompt_template_proposal = section_8_template()
    elif section_name == "Opinion of the Relationship Manager":
        prompt_template_proposal = section_9_template()
    elif section_name == "Summary of Recommendation":
        prompt_template_proposal = section_10_template()
    else:
        prompt_template_proposal = first_gen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")

    # set up openai environment - Ethan
    """llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal,
        output_key="first_gen_paragraph"
    )

    review_chain = LLMChain(llm=llm_proposal, prompt=review_prompt_template(), output_key="reviewed")

    overall_chain = SequentialChain(chains=[chain, review_chain], 
                                    input_variables=["input_info", "client_name", "example"],
                                    # Here we return multiple variables
                                    output_variables=["reviewed"],
                                    verbose=True)

    # Break the input_json by parts
    input_info_str = []
    example_str = []

    for item in input_json:
        sub_section = item['Sub-section']
        value = item['Value']
        example = item['Example']
        input_info_str.append(f"{sub_section} : {value}")
        example_str.append(f"{sub_section} : {example}")

    final_dict = {"input_info": ", ".join(input_info_str), "Example": ", ".join(example_str)}

    drafted_text = overall_chain({"input_info": final_dict["input_info"], "client_name": client, "example": final_dict["Example"]})
    drafted_text = drafted_text["reviewed"]
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    # All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    lines = drafted_text2.split("\n")

    for i, line in enumerate(lines):
        matches = re.findall(r"\[RM (.+?)\]\.?", line)  # Find all [RM ...] followed by optional dot
        for match in matches:
            rm_fill = match + "\n"
            rm_fill_values.append(rm_fill)
        
        # remove all the RM requests and the optional following dots from the line
        line = re.sub(r"\[RM .+?\]\.?", "", line)
        lines[i] = line

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : rm_fill_text,
    }

    #output the result
    return output_json

# Re-generate function
def regen(section_name, previous_paragraph, rm_instruction):
    prompt_template_proposal = regen_template()

    # set up openai environment - Jay
    llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")


    # set up openai environment - Ethan
    """llm_proposal = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                            openai_api_version="2023-05-15", openai_api_base="https://lwyethan-azure-openai-test-01.openai.azure.com/")"""
    
    chain = LLMChain(
        llm=llm_proposal,
        prompt=prompt_template_proposal,
        output_key="re_gen_paragraph"
    )

    review_chain = LLMChain(llm=llm_proposal, prompt=regenerate_review_prompt_template(), output_key="reviewed")

    overall_chain = SequentialChain(chains=[chain, review_chain], 
                                    input_variables=["previous_paragraph", "rm_instruction"],
                                    # Here we return multiple variables
                                    output_variables=["reviewed"],
                                    verbose=True)


    drafted_text = overall_chain({"previous_paragraph": previous_paragraph, "rm_instruction":rm_instruction})
    drafted_text = drafted_text["reviewed"]
    drafted_text2 = drafted_text.replace("Based on the given information, ", "").replace("It is mentioned that ", "")

    #All capital letters for first letter in sentences
    formatter = re.compile(r'(?<=[\.\?!]\s)(\w+)')
    drafted_text2 = formatter.sub(lambda m: m.group().capitalize(), drafted_text2)

    # Capitalize the first character of the text
    drafted_text2 = drafted_text2[0].capitalize() + drafted_text2[1:]

    rm_fill_values = []
    lines = drafted_text2.split("\n")

    for i, line in enumerate(lines):
        matches = re.findall(r"\[RM (.+?)\]\.?", line)  # Find all [RM ...] followed by optional dot
        for match in matches:
            rm_fill = match + "\n"
            rm_fill_values.append(rm_fill)
        
        # remove all the RM requests and the optional following dots from the line
        line = re.sub(r"\[RM .+?\]\.?", "", line)
        lines[i] = line

    # Rejoin the lines into a single string without RM requests
    drafted_text2 = "\n".join(lines)

    # Join all the strings in the list with a space in between each string
    rm_fill_text = ' '.join(rm_fill_values)

    output_json = {
        "section": section_name,
        "output": drafted_text2,
        "RM_fill" : rm_fill_text,
    }

    #output the result
    return output_json


# Wrapper function
def run_first_gen(section, rm_note_txt, client):

    extract_json = web_extract_RM(section ,rm_note_txt, client)
    output_json = first_generate(section, extract_json, client)

    return output_json
