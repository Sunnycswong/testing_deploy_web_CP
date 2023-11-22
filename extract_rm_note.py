
#%%
## Import Library
import os
import json
import copy
import re
import string
import openai

# from azure.core.credentials import AzureKeyCredential
# from azure.identity import AzureDeveloperCliCredential
# from azure.search.documents import SearchClient
# from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     HnswParameters,
#     PrioritizedFields,
#     SearchableField,
#     SearchField,
#     SearchFieldDataType,
#     SearchIndex,
#     SemanticConfiguration,
#     SemanticField,
#     SemanticSettings,
#     SimpleField,
#     VectorSearch,
#     VectorSearchAlgorithmConfiguration,
# )
# from azure.storage.blob import BlobServiceClient
# from azure.storage.blob import BlobServiceClient
# from azure.core.exceptions import ResourceExistsError

# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores.azuresearch import AzureSearch
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores.azuresearch import AzureSearch
# from langchain.chains import RetrievalQA
# from langchain.chains.question_answering import load_qa_chain
# #from langchain.retrievers import AzureCognitiveSearchRetriever
# from langdetect import detect
# from langchain.prompts import PromptTemplate

# # Create chain to answer questions
# from langchain.chains import RetrievalQA
# from langchain.chains.question_answering import load_qa_chain
# from langchain.memory import ConversationBufferMemory
# from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# # Import Azure OpenAI
# from langchain.llms import AzureOpenAI 
from langchain.chat_models import AzureChatOpenAI
# from langchain.schema import HumanMessage

# from langchain.chains import LLMChain
# from langchain.llms import AzureOpenAI 
# from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
# from langchain.chat_models import AzureChatOpenAI
# from langchain.memory import CosmosDBChatMessageHistory

# from langchain.chains import create_extraction_chain
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate

#import textwrap
#import logging

#%%
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

#%%
def load_json(json_path):
    with open(json_path, "r" ,encoding="utf-8") as f:
        data = json.load(f)
    return data


#%%
#one off exercise 
##This cell is to generate the schema of displaying in the frondend
default_text = 'Write the client background section by the given information'
section_prompt_dict = {'A. Project Overview': "Write me an overview on the project based on the provided component",
 'B. Client Background': default_text,
 'C. Credit Request': default_text,
 'D. Project Details': default_text,
 'E. Financial Information': default_text,
 'F. Collateral and Guarantees': default_text,
 'G. Repayment Capacity': default_text,
 'H. Risk and Mitigation': default_text,
 'I. Compliance and Legal': default_text,
 'J. Conclusion': default_text,
 'K. Recommendations': default_text,
 'Final Approval': default_text}

credit_proposal_example_dict = {'A. Project Overview': """The deal is referred by Pamfleet Group (“Pamfleet”) and our relationship with it can be traced back to early 2006 when the OIC was with Hang Seng Bank.  After joining ICBC (Asia), OIC’d tried a couple of time to cooperate with Pamfleet, but was in vain owing to the more aggressive offer given by Pamfleet’s partner banks, like CITIC Ka Wah Bank.  However, due to ICBCA business scale, network plus OIC’s marketing effort and cordial relationship, Pamfleet agreed to provide an industry / office acquisition project for our consideration.

In this project, Pamfleet is to cooperate with Angelo Gordon Group (“Angelo Gordon”), a US investment company dedicated to alternative investment to form a fund, which will be used to acquire Ever Gain Plaza located in Kwai Chung (the “Property”) or the companies holding the Property.""",
 'B. Client Background': """""",
 'C. Credit Request': """To facilitate the acquisition of the majority of Ever Gain Plaza, Pamfleet and Angelo Gordon would like our Bank to consider granting:
c)	Term Loan Facility of HKD757.5M (“Facility”) for its acquisition against the First Legal Charge on the Property plus other terms customary to this type of financing as stipulated in the Annex.
d)	IRS Facility of HKD757.5M (notional) for hedging the interest rate risk of the Facility

(For terms and conditions of the Facility, please refer to Front Page Application)

Please note that mezzanine loans may be provided by other financial institutions or investors for the Borrower, so that the latter and its related sponsors can enhance the yield and return of this property investment.  

Concerning the risk to ICBCA, we consider that it is acceptable given we require that the Facility A + those mezzanine loans should NOT exceed 70% of the prevailing Market Value of the Property, based on the valuation provided by an independent professional valuer acceptable to the Lender.  Should it be exceeded, the Borrower is required to provide additional securities acceptable to the Lender or reduce the aggregate outstanding so that the Facility A to valuation ratio (“LTV”) returns to 60% or below within 45 days after the Lender’s giving of notification.  Please note that All Monies First Legal Mortgage on the Property is ONLY for our Bank.  The other lenders can only get Second Legal Mortgage, which is behind our First Legal Mortgage..
""",
 'D. Project Details': """The summary of the Property are as follows:
Ever Gain Plaza Details
Location:	88 Container Port Road, Kwai Chung
Type:	Industrial Office
Gross Floor Area of the Property:	582,335 sq ft, representing 53% undivided shares ownership of the whole property (60% of the GFA) plus 187 car parking spaces
Occupancy:	Over 90%
Management:	Pamfleet since 2007
Total Rental:	Around HKD6.8M (about HKD12-13 per sq ft) per month
Age:	Since 1998
Users:	Industrial, trading, logistic, shipping and transportation companies etc.
Updated valuation:	CMV: HKD1,981M (Knight Frank)
Estimated Acquisition Cost:	HKD1,515M (cost per sq ft at HKD2,500- based on GFA), HKD340K per car parking space
Estimated Renovation Cost:	HKD5M 
Target Market:	End users, existing tenants, investors
Details:	The Property/site is easily accessible and located just 3 minutes to Kwai Fong MTR station, 8 minutes to container terminals and 20 minutes to Hong Kong International Airport.  Free shuttle bus services are provided to Kwai Fong and Mei Foo MTR Stations.

Property Summary
The Property comprises the majority portion of Ever Gain Plaza. This portion is approximately 582,335 square feet, or 60% of the industrial office floor area (7/F–28/F). The Property also includes 187 car parking bays on the Lower Ground Floor, Ground Floor, 1st Floor and 2nd Floor.

With its distinctive architectural design and energy-efficient curtain wall system, Ever Gain Plaza is a landmark industrial office building in the Kwai Chung area. Completed in 1998, Ever Gain Plaza offers easy access to Hong Kong’s major container terminals, as well as to rail and major road networks. The building comprises two towers atop a 7-storey podium and a lower ground floor. Each tower consists of 22 floors, affording a total gross floor area of over 900,000 square feet of industrial office space. Ever Gain Plaza was built to provide its users with convenient facilities including a food court and ample parking spaces. There are a total of 30 lifts, 8 for cargo and 22 for passengers, providing efficient vertical transportation in the building.

Strengths of the Property
	A landmark industrial office building in Kwai Chung strategically positioned within 8 minutes by car to Hong Kong’s major container terminals and 15 minutes to the Hong Kong International Airport, the Central business district, and the border with mainland China.  Ever Gain Plaza is within 5 minutes walking distance to the Kwai Fong MTR (subway) station.
	High quality building specifications and facilities - considered to be a benchmark property in the area. Key tenants in the building are predominantly major corporate industrial office occupiers such as NTT Asia, Arrow Asia, Jardine Shipping and NEC Technologies.
	High occupancy rate of approximately 90% is supported by strong tenant covenants.
""",
 'E. Financial Information': """""",
 'F. Collateral and Guarantees': """""",
 'G. Repayment Capacity': """""",
 'H. Risk and Mitigation': """""",
 'I. Compliance and Legal': """""",
 'J. Conclusion': """""",
 'K. Recommendations': """""",
 'Final Approval': """In view of the above, we recommend the proposed loan facility for management approval."""}

hierarchy_file_name = "hierarchy.json"

hierarchy_dict_list = load_json(hierarchy_file_name)

instruction_list = []
for section_dict in hierarchy_dict_list:
    create_new_dict = True
    if len(instruction_list) == 0:
        pass
    else:
        instruction_dict = {}
        for dictionary in instruction_list:
            if section_dict["Section"] == dictionary["Section"]: #If true, just modify the existing dict
                if section_dict["Sub Section"] not in dictionary["Component"]:
                    dictionary["Component"].append(section_dict["Sub Section"])
                create_new_dict = False
                pass
    if create_new_dict:
        instruction_dict = {"Section": section_dict["Section"],
                                    "Component": [],
                                    "Prompt": section_prompt_dict[section_dict["Section"]],
                                    "Example": credit_proposal_example_dict[section_dict["Section"]] ,
                                    "RM Note": "",
                                    "Document": "",
                                    "GPT Output": "",
                                    "Others" : ""
                                    }
        instruction_list.append(instruction_dict)

for l in instruction_list:
    l["Component_Text"] = ', '.join(l["Component"])

json.dump(instruction_list, open("MTR_schema.json", "w"), indent=4)

def cap(match):
    return(match.group().capitalize())



#%%
#This funcition is to extract RM notes for web, call by app.py
def web_extract_RM(rm_note_txt):

    # read config files in config directory
    hierarchy_file_name = "config/hierarchy.json"
    schema_file_name = "config/schema.json"

    hierarchy_dict_list = load_json(hierarchy_file_name)
    schema_dict_list = load_json(schema_file_name)

    schema_dict_list_with_GPT = copy.deepcopy(schema_dict_list)
    for l in schema_dict_list_with_GPT:
        section = l["Section"]
        prompt = l['Prompt']
        rm_note = l['RM Note']
        document = l['Document']
        example = l['Example']

    prompt_template_for_extracting_rm_note = """
    Read the RM note (Keyword: rm_note) to answer the input question (Keyword: Question):
    
    rm_note (Keyword: rm_note):
    {rm_note}
    ======
    Question (Keyword: Question):
    {question}
    ======
    
    Then answer the question based on the above aggregrate context

    Guidance when you do not have that information:
    1. When you don't have the specific information based on rm_note (Keyword: rm_note), you have to write it in the following format: [Information not available]
    2. You must not create the information by yourself if you don't have relevant information
    3. You cannot say "It's unclear that", please refer to point 1 for the formatting for requesting further information

    Rules you have to follow:
    1. Please provide your answer in English
    2. do not start your answer with "Based on the given information"
    3. The example (Keyword: proposal_example) above is just for your reference only to improve your theme, you must not directly copy the content in the examples
    4. If possible, try to expand the information provided from the RM
    5. Do not create any figures by make-up 

    Take a deep breath and work on this step by step
    """
    rm_prompt_template = PromptTemplate(template=prompt_template_for_extracting_rm_note, input_variables=["rm_note", "question"])

    llm_rm_note = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0.1,
                            openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")

    return hierarchy_dict_list, rm_prompt_template, llm_rm_note, rm_note_txt


#This cell is to prepare the rm note in desired format
def extract_rm_note(hierarchy_dict_list, rm_note, rm_prompt_template, llm, output_json_name):
    """
    Read the rm_note_txt and extract the information (Key: RM Note)
    """
    output_dict_list = []
    for dictionary in hierarchy_dict_list:
        chain = LLMChain(llm=llm, prompt=rm_prompt_template)
        dictionary["Value"] = chain({"rm_note":rm_note, "question": dictionary["Question"]})['text']
        dictionary["Value"] = dictionary["Value"].replace("Based on the given information, ", "")
        output_dict_list.append(dictionary)
    # json.dump(output_dict_list, open(output_json_name, "w"), indent=4)

    return output_dict_list

'''
extract_rm_note(hierarchy_dict_list=hierarchy_dict_list
                , rm_note=rm_note_txt 
                , rm_prompt_template=rm_prompt_template
                , llm=llm_rm_note
                , output_json_name="GOGOVAN_hierarchy_rm_note.json")
'''

                