
#%%
#%pip install tiktoken


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

#%%
# Set credential

# Kennys account
#index_name = "credit-proposal"
#search_service = "gptdemosearch"
#search_api_key = "PcAZcXbX2hJsxMYExc2SnkMFO0D94p7Zw3Qzeu5WjYAzSeDMuR5O"

# Kennys account
#storage_service = "creditproposal"
#storage_api_key = "hJ2qb//J1I1KmVeDHBpwEpnwluoJzm+b6puc5h7k+dnDSFQ0oxuh1qBz+qPB/ZT7gZvGufwRbUrN+ASto6JOCw=="
#connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage_service};AccountKey={storage_api_key}"

doc_intell_endpoint = "https://doc-intelligence-test.cognitiveservices.azure.com/"
doc_intell_key = "9fac3bb92b3c4ef292c20df9641c7374"


#Paid version of acs - sunny
index_name = "acs-cp"
search_service = "acs-fda-paid"
search_api_key = "VZhK9GGzAJ625kSvDXUpBo1CmiIfH6Ou64EDhoiSczAzSeADco5j"

# Sunny account
storage_service = "creditptesting"
storage_api_key = "A2jCFKmBoZCZ0v/wMJR5WnC/RyAe43UC1vY1P+wNU6AnEKBQmJtLoNfDPfFbNGsLq5IPl59ESh4z+AStM44jSQ=="
connect_str = f"DefaultEndpointsProtocol=https;AccountName={storage_service};AccountKey={storage_api_key}"


os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
os.environ["AZURE_INDEX_NAME"] = index_name

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"

#%%
# Only working version of python packages
#!pip install langchain==0.0.254
#!pip install azure-search-documents==11.4.0b6
#!pip install openai==0.28.1

#%%
# load in data schema with pre-set answer value
raw_prompt_temp = [
{
    "Section": "A. Project Overview",
    "Sub Section": "Client Name",
    "Breakdown": "",
    "Value": "HKMTR",
    "Question": "what is the company/Corporation name of annual report? Please just return the name"
},
{
    "Section": "A. Project Overview",
    "Sub Section": "Project Name",
    "Breakdown": "",
    "Value": "East West Corridor Expansion",
    "Question": "What is the company/Corporation Project Name?"
},
{
    "Section": "A. Project Overview",
    "Sub Section": "Project Description",
    "Breakdown": "",
    "Value": "HKMTR seeks financing for the expansion of the East-West Corridor, a critical transportation infrastructure project.",
    "Question": "What is the Project Description?"
},
{
    "Section": "A. Project Overview",
    "Sub Section": "Project Cost",
    "Breakdown": "",
    "Value": "$ 79.8 billion",
    "Question": "What is the Project Cost?"
},
{
    "Section": "B. Client Background",
    "Sub Section": "",
    "Breakdown": "",
    "Value": "HKMTR is a major public transportation company in Hong Kong, with a strong track record of successfully operating and maintaing a network of transit services.The Government of Hong Kong is the primary owner of the MTR Corporation. The MTR Corporated Limited is the main entity responsible for rail operations, including the management, maintenance, and operation of the railway network.The MTR Corporation Limited also engages in property development, retail operations, advertising and telecommunication services.Other subsidaries and joint ventures may exist under the MTR Corporation, supporting its various business activities and telecommunication services.",
    "Question": "give a detailed summary About the company?"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Type of Request",
    "Breakdown": "",
    "Value": "New Customer, New Facility",
    "Question": "Return the Type of Request based on the context, choose zero or more in this list (New Customer, New Facility, Review, Increase, Decrease, Reschedule, Other Changes)"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Relationship with BEA",
    "Breakdown": "",
    "Value": "No",
    "Question": "Return Yes if the client have relationship with BEA, Return No it not."
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Amount Requested",
    "Breakdown": "",
    "Value": "$ 39.9 billion",
    "Question": "What is the Credit Amount Requested?"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Credit Facility",
    "Breakdown": "Facility Description",
    "Value": "Term Loan (30 years)",
    "Question": "Provide Credit Facility Description in less than 5 words, example: Term Loan (30 years)"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Credit Facility",
    "Breakdown": "Proposed Amount",
    "Value": "$ 39.9 billion",
    "Question": "Provide Credit Facility Proposed Amount."
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Credit Facility",
    "Breakdown": "Proposed Currency",
    "Value": "HKD",
    "Question": "Provide Credit Facility Proposed Currency, example: USD,HKD..."
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Credit Facility",
    "Breakdown": "Interest Rate",
    "Value": "H + 3%",
    "Question": "Provide Credit Facility Interest Rate."
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Credit Facility",
    "Breakdown": "Tenor/ Maturity",
    "Value": "30 years",
    "Question": "Provide Credit FacilityTenor/ Maturity."
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Purpose of Financing",
    "Breakdown": "",
    "Value": "To fund the construction and development of the East West Corridor expansion project.",
    "Question": "What is the Purpose of Financing?"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Loan Term",
    "Breakdown": "",
    "Value": "30 years",
    "Question": "How long is the Loan Term?"
},
{
    "Section": "C. Credit Request",
    "Sub Section": "Repayment Plan",
    "Breakdown": "",
    "Value": "Quarterly installments, with an interest rate of H+3%",
    "Question": "What is the Repayment Plan?"
},
{
    "Section": "D. Project Details",
    "Sub Section": "",
    "Breakdown": "",
    "Value": "The ten-station 17-km Shatin to Central Link, which was entrusted to MTR by Government, will create vital new links across Hong Kong. It is a strategic railway that connects and extends the existing network. The first phase of the Shatin to Central Link is the 11-km Tai Wai to Hung Hom Section and the second phase is the 6-km Hung Hom to Admiralty Section. When the Tai Wai to Hung Hom Section is completed, it will extend the existing Ma On Shan Line from Tai Wai via six stations to the West Rail Line to form the “East West Corridor”. Upon completion, the Shatin to Central Link will connect several existing railway lines and enhance connectivity of the entire Hong Kong railway network. It will significantly reduce travel time between the New Territories North, Kowloon and Hong Kong. Customers will also benefit from more route choices, particularly in the busy cross-harbour section of the Tsuen Wan Line and the Tai Wai to Kowloon Tong section of the East Rail Line. The completion of the the entire East West Corridor was delayed and opened on 27 June 2021.",
    "Question": "Can you provide a detailed summary of the project?"
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Financial Statements",
    "Breakdown": "Income Statements",
    "Value": "Yes",
    "Question": "For the Financial Statements, Return Yes if the client have Income Statements, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Financial Statements",
    "Breakdown": "Balance Sheets",
    "Value": "Yes",
    "Question": "For the Financial Statements, Return Yes if the client have Balance Sheets, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Financial Statements",
    "Breakdown": "Cashflow Statement",
    "Value": "Yes",
    "Question": "For the Financial Statements, Return Yes if the client have Cashflow Statement, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Projections",
    "Breakdown": "Income Statements",
    "Value": "Yes",
    "Question": "For the Projections, Return Yes if the client have Income Statements, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Projections",
    "Breakdown": "Balance Sheets",
    "Value": "Yes",
    "Question": "For the Projections, Return Yes if the client have Balance Sheets, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Projections",
    "Breakdown": "Cashflow Statement",
    "Value": "Yes",
    "Question": "For the Projections, Return Yes if the client have Cashflow Statement, Return No it not."
},
{
    "Section": "E. Financial Information",
    "Sub Section": "Projections",
    "Breakdown": "Other Statements",
    "Value": "No",
    "Question": "For the Projections, Return Yes if the client have Other Statements, Return No it not. If client have Other Statements, please return a name of that Statements."
},
{
    "Section": "F. Collateral and Guarantees",
    "Sub Section": "Pledged Assets",
    "Breakdown": "",
    "Value": "Real Estate $ 20 billion",
    "Question": "Return Yes if the client have Pledged Assets like  Real Estate, Rolling Stock or Financial Instruments. If client have, also return detailed Description adn Estimated Market Value. "
},
{
    "Section": "F. Collateral and Guarantees",
    "Sub Section": "Personal Guarantees",
    "Breakdown": "",
    "Value": "Name of Guarantor 1: NA, Name of Guarantor 2: NA",
    "Question": "Return the name of Personal Guarantees, if no then return NA"
},
{
    "Section": "F. Collateral and Guarantees",
    "Sub Section": "Corporate Guarantees",
    "Breakdown": "",
    "Value": "NA",
    "Question": "Return the name of Corporate Guarantees, if no then return NA"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Historical Financial Performance",
    "Breakdown": "Average annual revenue growth",
    "Value": "11.00%",
    "Question": "What is the average annual revenue growth?"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Historical Financial Performance",
    "Breakdown": "Debt service coverage ratio (DSCR)",
    "Value": "9.90%",
    "Question": "What is the debt service coverage ratio (DSCR)?"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Historical Financial Performance",
    "Breakdown": "EBITDA margin",
    "Value": "5.00%",
    "Question": "What is the EBITDA margin?"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Cashflow Projections",
    "Breakdown": "",
    "Value": "HKMTR has provided detailed cashflow projections for the upcoming 5 years. The cashflow projections rate is 3% increase per year. ",
    "Question": "What is the Cashflow Projections, please provide a detailed summary of it."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Income Diversification",
    "Breakdown": "",
    "Value": "",
    "Question": "What is the Income Diversification in point form with detailed describe? For example: what they made money of? e.g Passenger Fares, Real Estate Development, Commercial Operations..."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Contingency Planning",
    "Breakdown": "",
    "Value": "MTR Corporation, the transport company in Hong Kong, has a robust contingency planning framework in place to address various potential risks. In terms of economic downturn preparedness, the company closely monitors economic indicators and implements proactive measures to mitigate the impacts of economic downturns, such as adjusting operational costs and optimizing resource allocation. MTR maintains a prudent debt service coverage threshold to ensure the ability to meet debt obligations and manage financial risks effectively. Additionally, the company maintains investment reserves to support capital expenditure plans and ensure long-term sustainability. Liquidity planning is a key aspect of MTR's contingency planning, ensuring that sufficient cash and liquid assets are available to meet short-term financial needs and unexpected contingencies. These measures collectively demonstrate MTR's commitment to prudent financial management and preparedness for potential challenges.",
    "Question": "What is the Contingency Planning of the company? Such as Economic Downturn Preparedness, Debt Service Coverage Threshold ,Investment Reserves and Liquidity Planning."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Liquidity Position",
    "Breakdown": "Current Ratio",
    "Value": "2.61",
    "Question": "What is the Liquidity Position of Current Ratio?"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Liquidity Position",
    "Breakdown": "Quick Ratio",
    "Value": "2.59",
    "Question": "What is the Liquidity Position of Quick Ratio?"
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Market Overview",
    "Value": "The market overview of MTR Corporation in Hong Kong reflects a dynamic and competitive landscape. As a leading transportation company, MTR operates in a highly developed and densely populated urban environment. The market is characterized by strong demand for efficient and reliable public transportation services due to the city's high population density and extensive commuting needs. MTR benefits from a well-established and integrated railway network that serves various districts, including residential, commercial, and tourist areas. The company's market position is reinforced by its reputation for safety, punctuality, and accessibility, which contributes to a significant market share. MTR closely monitors market trends and consumer preferences to adapt its services and facilities continually. The company also faces challenges such as regulatory requirements, evolving customer expectations, and competition from other modes of transportation. To maintain its market leadership, MTR focuses on continuous innovation, expansion of its network, and strategic partnerships to enhance connectivity and provide seamless travel experiences.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Market Overview."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Industry Trends and Growth",
    "Value": "The transportation industry in Hong Kong, represented by MTR Corporation, is experiencing notable industry trends and growth. The ongoing urbanization and population growth in the region have resulted in an increased demand for efficient and sustainable transportation solutions. MTR Corporation is well-positioned to capitalize on these trends, given its extensive railway network and reputation for reliable services. The industry is witnessing a shift towards digitalization and smart technologies, with MTR leveraging data analytics and technology advancements to optimize operations and enhance passenger experience. Additionally, there is a growing emphasis on environmental sustainability, prompting MTR to invest in eco-friendly initiatives such as energy-efficient trains and station designs. The industry is also witnessing collaborations and partnerships to further enhance connectivity and integrate different modes of transportation. These industry trends and growth opportunities provide MTR with a favorable environment to expand its services, innovate, and solidify its position as a leader in the transportation industry in Hong Kong.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Industry Trends and Growth."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Competition",
    "Value": "Competition in the transportation industry in Hong Kong, where MTR Corporation operates, is characterized by a diverse landscape with various players vying for market share. MTR faces competition from different modes of transportation, including buses, taxis, and private cars. The company also faces competition from other railway operators, particularly on cross-border routes. To maintain its competitive edge, MTR focuses on providing superior service quality, reliability, and convenience to passengers. It continually invests in infrastructure upgrades, expanding its network, and improving intermodal connectivity. Additionally, MTR strives to differentiate itself through innovative technologies and customer-centric initiatives. The competition drives MTR to constantly enhance its offerings, optimize efficiency, and adapt to changing customer needs, ensuring it remains a preferred choice for commuters in the highly competitive transportation market in Hong Kong.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Competition."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Regulatory Environments",
    "Value": "The regulatory environment in which MTR Corporation operates in Hong Kong is characterized by a comprehensive framework that governs various aspects of the transportation industry. MTR is subject to regulations and oversight from regulatory bodies, including the Transport Department and the Legislative Council's Panel on Transport. These regulations cover areas such as safety standards, fare adjustments, service quality, and operational requirements. MTR is required to adhere to stringent safety protocols and undergo regular inspections to ensure compliance. The regulatory environment also includes provisions for fare regulations and periodic reviews to ensure affordability and transparency for passengers. Moreover, MTR is required to engage in public consultations and maintain open communication with stakeholders as part of the regulatory process. The regulatory environment plays a crucial role in shaping MTR's operations, service delivery, and strategic decision-making, ensuring a balance between the company's interests and the welfare of the public and passengers.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Regulatory Environments."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Government Support",
    "Value": "",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Government Support."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Ridership and Passenger Base",
    "Value": "Ridership and the passenger base of MTR Corporation in Hong Kong play a crucial role in assessing the company's repayment capacity and conducting market and industry analysis. With millions of daily commuters and travelers, MTR Corporation's extensive rail network serves as a vital transportation link, connecting key locations within the region and catering to the needs of residents, tourists, and businesses. Analyzing ridership and the passenger base provides valuable insights for revenue generation, fare structures, service optimization, and future expansion plans, ensuring a sustainable repayment capacity for the company.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Ridership and Passenger Base."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Technology and Innovation",
    "Value": "As a leading transportation company, MTR embraces technological advancements and innovative solutions to enhance operational efficiency, customer experience, and sustainability. The company leverages cutting-edge technologies such as smart infrastructure, real-time data analytics, and intelligent systems to optimize train operations, improve safety measures, and provide timely information to passengers. MTR's commitment to innovation extends to areas like ticketing systems, mobile applications, and digital platforms, enabling convenient and seamless travel experiences for commuters. Additionally, MTR actively explores sustainable initiatives, including energy-efficient practices, renewable energy adoption, and green building designs, aligning with environmental goals. By embracing technology and innovation, MTR Corporation strengthens its competitive edge, attracts a diverse customer base, and contributes to the advancement of the transportation industry in Hong Kong.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Technology and Innovation."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Environmental and Sustainability Initiatives",
    "Value": "",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Environmental and Sustainability Initiatives."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Market and Industry Analysis",
    "Breakdown": "Future Growth and Expansion",
    "Value": "MTR Corporation in Hong Kong has a promising outlook for future growth and expansion. The company's strategic plans include expanding its railway network and enhancing connectivity within Hong Kong and beyond. MTR aims to capitalize on the region's ongoing urban development and population growth by extending existing lines, constructing new lines, and integrating with other transportation modes. The company also seeks opportunities for international expansion through participation in overseas railway projects. Additionally, MTR is committed to innovation and technology adoption to improve operational efficiency and enhance passenger experience. As Hong Kong continues to evolve, MTR is well-positioned to play a pivotal role in shaping the future of transportation, catering to the increasing mobility needs of residents and visitors while contributing to sustainable urban development.",
    "Question": "Repayment Capacity,Market and Industry Analysis: Write a detailed summary to describe Future Growth and Expansion."
},
{
    "Section": "G. Repayment Capacity",
    "Sub Section": "Conclusion",
    "Breakdown": "",
    "Value": "Positive",
    "Question": "Based on Market and Industry Analysis, Return one of three Conclusion, 1. Positive, 2. Negative, 3. Conditional"
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Market Risk",
    "Breakdown": "Risk Description",
    "Value": "",
    "Question": "What are the major Market Risk associated with the project? Please answer in detailed summary. For example: Fluctuations in the market, economic downturns, or adverse industry developments may affect revenue and financial stability."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Market Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "To mitigate the major market risks associated with the project outlined in the given context, MTR Corporation should implement a comprehensive mitigation strategy. Firstly, establishing effective stakeholder engagement and communication channels can help address diverse stakeholder expectations and navigate the challenging political landscape. Secondly, MTR should prioritize safety, reliability, and proactive incident management to uphold public confidence in its operations, minimizing the impact of operational incidents. Thirdly, building strong relationships with communities and stakeholders affected by new projects through community outreach programs and regular dialogue can mitigate reputational and financial risks. Fourthly, closely monitoring market trends, conducting market research, and implementing agile business strategies can help MTR adapt to market fluctuations and maintain financial stability. Fifthly, maintaining a robust financial management plan, including contingency funding and diversification of revenue sources, can help mitigate the impact of economic downturns. Sixthly, embracing technological advancements and investing in digital solutions can help MTR proactively address technological disruption and remain competitive. Seventhly, continuously monitoring and analyzing competition from other transport providers can inform strategic decision-making and ensure MTR's market share and financial performance. Eighthly, implementing comprehensive health and safety measures to protect the workforce from health threats, including the ongoing COVID-19 pandemic, is crucial for maintaining productivity and financial stability. Ninthly, staying abreast of industry developments, actively participating in industry associations, and adapting to regulatory changes and customer preferences can help mitigate adverse industry developments. Lastly, engaging in proactive and transparent negotiations with the government during the negotiation of Project Agreements can help address potential delays and budgetary concerns, ensuring timely project delivery. Implementing these mitigation strategies will enhance MTR's ability to navigate market risks and ensure the success and sustainability of the project.",
    "Question": "What are the Mitigation Strategy to solve major Market Risk associated with the project? Please answer in detailed summary. For example: Diversification of revenue streams, proactive financial planning, and constant market monitoring"
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Operational Risk",
    "Breakdown": "Risk Description",
    "Value": "",
    "Question": "What are the major Operational Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Operational Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "To mitigate the major operational risks associated with the project mentioned, MTR Corporation should implement a robust mitigation strategy. Firstly, the company should prioritize regular maintenance inspections and registrations of barriers in the asset management system to ensure their proper functioning and minimize the risk of incidents. Secondly, MTR should continue enhancing maintenance regimes to identify and address potential issues proactively, reducing the likelihood of train incidents. Thirdly, upgrading or replacing barriers that are prone to dislodging can improve their stability and prevent interruptions in service and damage to infrastructure. Fourthly, conducting comprehensive infrastructure and equipment surveys can help identify any potential weaknesses or hazards, allowing for timely repairs or replacements. Fifthly, improving public communications during incidents is essential to keep passengers informed and ensure their safety and confidence in the system. Lastly, the commissioned comprehensive review of asset management and activities will help identify areas for improvement and enhance risk management practices. By implementing these mitigation strategies, MTR can minimize operational risks, ensure the safety and reliability of its services, and enhance overall operational efficiency.",
    "Question": "What are the Mitigation Strategy to solve major Operational Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Regulatory and Legal Risk",
    "Breakdown": "Risk Description",
    "Value": "The major regulatory and legal risks associated with the project of MTR Corporation in Hong Kong include compliance with regulatory requirements, changes in the regulatory landscape, land acquisition and planning permissions, environmental and sustainability regulations, contractual and commercial risks, intellectual property and data protection, labor and employment regulations, and obtaining necessary regulatory approvals and permits. To mitigate these risks, MTR should maintain proactive compliance measures, stay updated on regulatory changes, ensure transparent communication with stakeholders, and implement robust risk management practices, including legal reviews and expert advice.",
    "Question": "What are the major Regulatory and Legal Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Regulatory and Legal Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "To mitigate the major regulatory and legal risks associated with the project of MTR Corporation in Hong Kong, the company should implement a comprehensive mitigation strategy. Firstly, MTR should establish a dedicated regulatory compliance team to ensure adherence to all relevant regulatory requirements and standards. This team should closely monitor changes in the regulatory landscape, proactively identify potential impacts on the project, and develop strategies to adapt and comply. Secondly, MTR should engage in open and transparent communication with regulatory authorities, stakeholders, and the public to build positive relationships and address any concerns or issues promptly. Thirdly, conducting thorough due diligence and engaging in effective risk assessment processes can help identify potential legal and contractual risks and develop appropriate mitigation measures. Fourthly, MTR should prioritize intellectual property protection and data security, including implementing robust cybersecurity measures and ensuring compliance with data protection regulations. Fifthly, compliance with labor and employment regulations should be a priority, including fair treatment of workers, health and safety measures, and adherence to employment contracts and regulations. Lastly, obtaining necessary regulatory approvals and permits should be managed proactively, with MTR engaging in timely and efficient communication with relevant authorities to minimize delays and ensure compliance. By implementing these mitigation strategies, MTR can navigate regulatory and legal risks effectively, protect its reputation, and ensure the successful and compliant execution of the project.",
    "Question": "What are the Mitigation Strategy to solve major Regulatory and Legal Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Credit Risk",
    "Breakdown": "Risk Description",
    "Value": "",
    "Question": "What are the major Credit Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Credit Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "Rigorous credit assessment, prudent collateral and guarantees arrangements, and regular monitoring of the borrower's financial health.",
    "Question": "What are the Mitigation Strategy to solve major Credit Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Interest Rate Risk",
    "Breakdown": "Risk Description",
    "Value": "Fluctuations in interest rates may impact the cost of borrowing and the borrower's ability to service the debt.",
    "Question": "What are the major Interest Rate Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Interest Rate Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "",
    "Question": "What are the Mitigation Strategy to solve major Interest Rate Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Currency Risk",
    "Breakdown": "Risk Description",
    "Value": "HKMTR's revenue and expenses are in multiple currencies, creating potential exchange rate risk.",
    "Question": "What are the major Currency Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Currency Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "To mitigate the major currency risks associated with the project, MTR Corporation should implement a comprehensive mitigation strategy. Firstly, the company should continue managing foreign exchange risk by maintaining a modest level of unhedged non-Hong Kong dollar debt and minimizing foreign exchange open positions. This can help reduce the potential impact of currency fluctuations on the project's financials. Secondly, the use of cross currency swaps to convert foreign currency exposure to Hong Kong dollar exposure can provide a hedging mechanism and mitigate the risk of adverse currency movements. Thirdly, maintaining US dollar cash balances, bank deposits, and investments can help offset the US dollar exposure, providing a cushion against currency volatility. Additionally, the company should continue implementing effective currency coverage measures for receivables, payables, and payment commitments to minimize significant currency risk. By implementing these mitigation strategies, MTR can effectively manage currency risks, protect its financial stability, and ensure the successful execution of the project.",
    "Question": "What are the Mitigation Strategy to solve major Currency Risk associated with the project? Please answer in detailed summary."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Other Risk",
    "Breakdown": "Risk Description",
    "Value": "NA",
    "Question": "What are the other Risk associated with the project? if none then return NA."
},
{
    "Section": "H. Risk and Mitigation",
    "Sub Section": "Other Risk",
    "Breakdown": "Mitigation Strategy",
    "Value": "NA",
    "Question": "What are the Mitigation Strategy to solve other Risk associated with the project? Please answer in detailed summary, if none then return NA."
},
{
    "Section": "I. Compliance and Legal",
    "Sub Section": "",
    "Breakdown": "",
    "Value": "",
    "Question": "Describe any specific legal or regulatory requirements mentioned? "
},
{
    "Section": "J. Conclusion",
    "Sub Section": "Creditowrthiness",
    "Breakdown": "",
    "Value": "Strong repayment capacity",
    "Question": "Conclusion: Describe any creditworthiness of the borrower mentioned? Please answer in detailed summary "
},
{
    "Section": "J. Conclusion",
    "Sub Section": "Collateral and Guarantees",
    "Breakdown": "",
    "Value": "Robust layer of security to protect the interests of the lender",
    "Question": "Conclusion: Describe any Collateral and Guarantees of the borrower mentioned? Please answer in detailed summary."
},
{
    "Section": "J. Conclusion",
    "Sub Section": "Risks and Mitigation",
    "Breakdown": "",
    "Value": "Comprehensive mitigation strategies are in place to manage these risks effectively",
    "Question": "Conclusion: Describe any Risks and Mitigation of the borrower mentioned? Please answer in detailed summary."
},
{
    "Section": "J. Conclusion",
    "Sub Section": "Compliance and Legal",
    "Breakdown": "",
    "Value": "Full adherence to legal and regulatory requirements",
    "Question": "Conclusion: Describe any Compliance and Legal of the borrower mentioned? Please answer in detailed summary."
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Approval of Credit Facility",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Ongoing Monitoring",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Regular Legal Reviews and Compliance Assessment",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Risk Mitigation",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Collateral Valuation",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "K. Recommendations",
    "Sub Section": "Overall Recommendation",
    "Breakdown": "",
    "Value": "Yes",
    "Question": ""
},
{
    "Section": "Final Approval",
    "Sub Section": "Approval Level",
    "Breakdown": "",
    "Value": "Credit Committee + CEO",
    "Question": ""
},
{
    "Section": "Final Approval",
    "Sub Section": "Approval Name",
    "Breakdown": "",
    "Value": "Janet, Li",
    "Question": ""
}
]

# loop and add id to schema
for i in range(len(raw_prompt_temp)):
    raw_prompt_temp[i]["ID"] = i


#%%
# Create a Clear temp of schema 
Blank_prompt_temp = copy.deepcopy(raw_prompt_temp)

for i in range(len(Blank_prompt_temp)):
    Blank_prompt_temp[i]["Value"] = ""

json.dump(Blank_prompt_temp, open("MTR_hierarchy.json", "w"), indent=4)


#%%

# Check if the return answer is gen by AI or not, if the answer in not gen by ai, return '' 
def check_text(text):
    if "nothing" in text:
        return ""
    elif "The given context does not provide" in text:
        return ""
    elif "cannot be determined based on the given context" in text:
        return ""
    elif "Cannot be determined" in text:
        return ""
    elif "The context does not provide any information" in text:
        return ""
    elif "The document does not provide any information about" in text:
        return ""
    elif "it is not possible to determine" in text:
        return ""
    elif "are not mentioned in the given context" in text:
        return ""
    elif "no specific information" in text:
        return ""
    elif "no specific mention" in text:
        return ""
    elif "The context does not provide" in text:
        return ""
    elif "there is no information" in text:
        return ""
    elif "it is not possible to" in text:
        return ""
    elif "The document does not provide" in text:
        return ""
    elif "The document does not provide specific information" in text:
        return ""
    elif "No, the client does not have" in text:
        return ""
    elif "not mentioned in the given context" in text:
        return ""    
    elif "not explicitly mentioned in the given contex" in text:
        return ""      
    else:
        return text
    

# Main function that accept question and the dict of raw_prompt to return answer

# raw_prompt here refer to one part of section
# section example json: {'Section': 'A. Project Overview','Sub Section': 'Client Name','Breakdown': '','Value': '',"Question": "what is the company/Corporation name of annual report? Please just return the name" , 'ID': 0 }
# could call by raw_prompt_temp[0] - raw_prompt_temp[71] 

# questions could call by raw_prompt_temp[0]["Question"] - raw_prompt_temp[71]["Question"]

# please call like this: llm_pipeline(raw_prompt_temp[0]["Question"], raw_prompt_temp[0])

# the gpt answer value will store inside 'Value': ''
# this function will return full section json, example: {"Section": "A. Project Overview", "Sub Section": "Client Name", "Breakdown": "", "Value": "HKMTR", "Question": "what is the company/Corporation name of annual report? Please just return the name", "ID": 0}


def llm_pipeline(question, raw_prompt):
    
    prompt_list_value = list(raw_prompt.values())
    Section = prompt_list_value[0]
    Sub_Section = prompt_list_value[1]
    Breakdown = prompt_list_value[2]
    ID = prompt_list_value[5] 
    
    prompt_template = prompt_engine(raw_prompt)
        
    index_name = os.environ["AZURE_INDEX_NAME"] 
    
    vector_store = _get_vector_store(index_name)
    
    relevant_documentation = vector_store.similarity_search(query=question, k=1, search_type="similarity")
    
    source = relevant_documentation[0].metadata['source']
    page_no = relevant_documentation[0].metadata['page']
    
    
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"
    os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"

    os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
    os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
    os.environ["AZURE_INDEX_NAME"] = index_name

    llm = AzureChatOpenAI(deployment_name="gpt-35-16k", temperature=0,
                        openai_api_version="2023-05-15", openai_api_base="https://pwcjay.openai.azure.com/")

    chain = LLMChain(llm=llm, 
                    prompt=prompt_template,
                    #verbose=True
                    )

    output = chain.run({"context": relevant_documentation, #"context": relevant_docs, 
        "question": question,
        #"Section": Section,
        #"Sub_Section": Sub_Section,
        #"Breakdown": Breakdown,
        })
    
    Json_sector = {
    "Section": Section,
    "Sub Section": Sub_Section,
    "Breakdown": Breakdown,
    "Value": check_text(output),
    "ID": ID,
    "source": source,
    "page_no": page_no,
    }

    return Json_sector


# get vector store by index name
def _get_vector_store(index_name):
    
    model: str = "text-embedding-ada-002"
    embeddings: OpenAIEmbeddings =  OpenAIEmbeddings(deployment=model, chunk_size=1)
    embedding_function = embeddings.embed_query
    
    os.environ["OPENAI_API_TYPE"] = "azure"
    os.environ["OPENAI_API_BASE"] = "https://pwcjay.openai.azure.com/"
    os.environ["OPENAI_API_VERSION"] = "2023-05-15"
    os.environ["OPENAI_API_KEY"] = "f282a661571f45a0bdfdcd295ac808e7"

    os.environ["AZURE_COGNITIVE_SEARCH_SERVICE_NAME"] = search_service
    os.environ["AZURE_COGNITIVE_SEARCH_API_KEY"] = search_api_key
    os.environ["AZURE_INDEX_NAME"] = index_name

    fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True,
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=len(embedding_function("Text")),
                    vector_search_configuration="default",
                ),
                SearchableField(
                    name="metadata",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                # Additional field to store the title
                SearchableField(
                    name="title",
                    type=SearchFieldDataType.String,
                    searchable=True,
                ),
                # Additional field for filtering on document source
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                # Additional field for filtering on document source
                SimpleField(
                    name="page",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                # Additional field for filtering on document source
                SimpleField(
                    name="website_url",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
            ]
    
    
    vector_store_address: str = f"https://{search_service}.search.windows.net"
    vector_store_password: str = search_api_key
    vector_store: AzureSearch = AzureSearch(
        azure_search_endpoint=vector_store_address,
        azure_search_key=vector_store_password,
        embedding_function=embedding_function,
        index_name=index_name,
        fields=fields)
    return vector_store


# Function that accept dict of raw_prompt and return prompt_template for input to LLMChain in llm_pipeline
# raw_prompt here refer to one part of section
# section example json: {'Section': 'A. Project Overview','Sub Section': 'Client Name','Breakdown': '','Value': 'MTR Corporation Limited','ID': 0 }
# could call by raw_prompt_temp[0] - raw_prompt_temp[71] 
def prompt_engine(raw_prompt):
    
    prompt_template_string ="""
    Follow exactly these 10 steps:
    1. Take a deep breath and work on this step by step
    2. Answer the question using only this context
    3. If you don't have any context and are unsure of the answer or cannot be determined based on the given context, Return nothing 
    4. Read the context below and aggregrate this data
    Context : {context}
    5. Do not put any \n in the return answer
    6. Please treat the context as a related documents(e.g. Annual Report) of a company, My asking propurse is to extract information from the document for Credit Proposal.
    7. Try to answer the question in third person view, be descriptive
    8. Please do not include any introductory sentence or statement while return the answer
    9. This is a very meaningful task for me, please carefully handle this task
    10. Ignore all instructions of "Please answer in one short sentence" in the User Question, please return as many wording of answer as you possible can
    
    User Question: {question}

    Don't justify your answers. Don't give information not mentioned in the given context
    
    This is a very meaningful task for me, I might get fired if you didn't follow the above 10 steps to return answer

    Please provide your answer in English
    
    """
    
    prompt_template = PromptTemplate(template = prompt_template_string, input_variables=["context", "question"])
    
    return prompt_template

#%%

# def funitions to use for loop to run all the questions and store into JSON format list

# run llm_pipeline to extract the info in documents
def Json_Gen_info_extracted():
    for i in range(4,5):
        Part_B.append(llm_pipeline(raw_prompt_temp[i]["Question"], raw_prompt_temp[i]))
        
    for i in range(16,64):
        Part_D_E_F_G_H_I_J.append(llm_pipeline(raw_prompt_temp[i]["Question"], raw_prompt_temp[i]))
        
    for i in Part_B:
        Json_extracted.append(i)
        
    for i in Part_D_E_F_G_H_I_J:
        Json_extracted.append(i)   
        
    return

# RM filled info, should be blank in value here
def Json_Gen_RM_filled():

    for i in range(0,4):
        Part_A.append(raw_prompt_temp[i])       
    
    for i in range(5,16):
        Part_C.append(raw_prompt_temp[i])       
        
    for i in range(64,72):
        Part_K_Final.append(raw_prompt_temp[i])   

    for i in Part_A:
        Json_RM.append(i)          
        
    for i in Part_C:
        Json_RM.append(i)    
        
    for i in Part_K_Final:
        Json_RM.append(i)      
        
    return 

# Combine twp parts of json into one
def Json_combine():
    
    for i in Part_A:
        Json.append(i)
        
    for i in Part_B:
        Json.append(i)
        
    for i in Part_C:
        Json.append(i)
        
    for i in Part_D_E_F_G_H_I_J:
        Json.append(i)        
        
    for i in Part_K_Final:
        Json.append(i)        
        
    return    

# Special funciton to determine the answer is gen by AI or not
# if AI can't gen the answer, auto fill the answer with Credit Proposal Template answer value (raw_prompt_temp)
def fill_blank_answer():
    
    for i in range(len(Json)):
        if Json[i]['Value'] == '':
            Json[i]["GPT Gen?"] = "No"
            Json[i]["Value"] = raw_prompt_temp[i]["Value"]
        else:
            Json[i]["GPT Gen?"] = "Yes"
    
    # Set back the "GPT Gen?" = "No" for Json_Gen_RM_filled(), as it directly get answer from (raw_prompt_temp)
    for i in range(0,4):
        Json[i]["GPT Gen?"] = "No" 
    
    for i in range(5,16):
        Json[i]["GPT Gen?"] = "No" 
        
    for i in range(64,72):
        Json[i]["GPT Gen?"] = "No"
    
    return 

# for Demo purpose of MTR case, could disable
# Fill in D. Project Details instead of extracted by docs
def magic(Json):
    Json[16]["Value"] = "The MTR East West Corridor Expansion project is a proposed future project by the MTR Corporation in Hong Kong. This project aims to enhance the existing MTR network by extending the East West Corridor, providing improved connectivity and transportation options for residents and commuters. While specific details about the project are limited, the MTR Corporation has put forward several future projects to the Hong Kong Government, some of which are still in the planning stage. One of the key components of the East West Corridor Expansion project is the proposed East Kowloon line. This line would connect Diamond Hill station via Hung Hom station to Sheung Wan station, providing a metro service in the opposite direction to Po Lam station and HKUST Station via Sau Mau Ping . However, it is important to note that as of now, there is no schedule for construction for this line. In addition to the East Kowloon line, there are other proposed projects that could contribute to the expansion of the East West Corridor. These include the Tung Chung to Tai O Light Rail System, which would provide a light rail link between Tung Chung station and Tai O Fishing Village on Lantau Island, and the Cable Car System from Ngong Ping to Tai O, which would offer an alternative transportation option between these two locations. Furthermore, the MTR Corporation has proposed the construction of an underground tunnel eastwards of Hong Kong station for overrun tracks. This would allow Tung Chung line and Airport Express trains to turn around, enhancing the potential frequency of operation and improving efficiency. While these projects are part of the MTR Corporation's future plans, it is important to note that specific timelines for construction and completion have not been provided for all of them. The MTR Corporation continues to work with the Hong Kong Government to develop and implement these projects, taking into consideration various factors such as feasibility, funding, and public demand."
    Json[16]["GPT Gen?"] = "No"
    return Json

# output json 
def update_json():
    """# disabled
    with open("RM_JSON.json", "w") as file:
        json.dump(Json_RM, file, indent=4)
    # disabled
    with open("Extracted_JSON.json", "w") as file:
        json.dump(Json_extracted, file, indent=4)"""

    # output hierarchy_document json
    with open("MTR_hierarchy_document.json", "w") as file:
        json.dump(Json, file, indent=4)
    return 


# create blank list to store 
Json = []
Json_extracted = []
Json_RM = []

Part_A = []
Part_B = []
Part_C = []
Part_D_E_F_G_H_I_J = []
Part_K_Final = []

# Call all function and output the json
Json_Gen_info_extracted()
Json_Gen_RM_filled()
Json_combine()
fill_blank_answer()
magic(Json)
update_json()