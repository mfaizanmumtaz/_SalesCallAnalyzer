from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()
openai_gpt3 = ChatOpenAI(model="gpt-3.5-turbo-1106").with_fallbacks([ChatOpenAI(model="gpt-4-1106-preview")])

openai = ChatOpenAI(model="gpt-4-1106-preview")
openai = ChatGoogleGenerativeAI(model='gemini-pro')
# Getting data from utils.py
from utils import get_data
GetData = get_data()
Quality_Assurance_Scorecard_Questions = GetData.get_questions
transcript = GetData.get_transcription
VULNERABILITY_EXAMPLES = GetData.get_vulnerability_examples

prompt = ChatPromptTemplate.from_messages([

("user","""Your task involves analyzing a phone call transcription between Money Advisor  advisor and a customer, within the context of the UK financial system. The transcription is delimited with XML tags. Follow these steps:

Carefully review the advisor's phone call transcription with the customer. Ensure you fully grasp the content, especially considering the UK financial regulations and practices, before proceeding to conclusions or decisions.

Address the question which is delimited with ``` based on your analysis of the transcription.Format your responses in this manner:
Questions : [Question Goes Here]
Response: [Either Complete or Partial or Unsatisfied (a one word answer that describes the answers response based on the question.]
Answer: [followed by an answer (answer should be short and brief, the max word count should be 200 words, but ideally less words, that offer a clear understanding and analysis.]
 
Remember to use Python '\n' line breaks for separating your answers, making them suitable for parsing in a Streamlit app.Please do your best it is very important to my career.

-------------

> <advisor phone call transcription with customer>: {transcription} <advisor phone call transcription with customer>""")])
chain = prompt | openai | StrOutputParser()

Money_Advisor_Scorecard = RunnablePassthrough() | (lambda x: [{"question":question["question"],"transcription":x["transcription"] } for question in Quality_Assurance_Scorecard_Questions]) | chain.map() | (lambda x: "\n\n".join(x).replace("\n", "<br>"))

vulnerability_prompt = ChatPromptTemplate.from_messages([

("user","""You are tasked with detecting vulnerabilities in customer support calls in customer speech. Follow these steps to complete the task:

Vulnerability Examples: Provided in CSV format, delimited with triple backticks (```).
Customer Support Call: Transcribed and delimited with XML tags.
Task Objective: Identify vulnerabilities in customer speech. Vulnerabilities refer to situations where a customer's statements or behavior indicate a need for special attention or care. For example, in the UK, if a customer mentions being seriously ill, the advisor should express concern, inquire about the illness, and use this information to decide whether to continue or halt the call. This is an example of customer vulnerability.
 
Reporting: Create a concise report highlighting instances where customers exhibit unexpected behavior, indicating vulnerability.
 
> Please do your best it is very important to my career.\

---------------

> ```{vulnerability_examples}```
    
---------------
    
> <Employee phone call transcription with customer>: {transcription} </Employee phone call transcription with customer>
    """)
])

vulnerability_prompt_chain = RunnablePassthrough.assign(
    vulnerability_examples= lambda x: VULNERABILITY_EXAMPLES
) | vulnerability_prompt | openai | StrOutputParser()

sales_techniques = ChatPromptTemplate.from_messages(
    [
("user", """You are assigned the role of an Analyzer for Customer Support Call advisor Techniques. The phone call transcription is delimited with XML tags. Please follow these instructions to successfully complete your analysis:

> Analysis Objective: Evaluate the effectiveness of the Customer Support Call advisor techniques during the provided phone call.
> Reporting: Deliver a concise report assessing the advisor performance and technique proficiency.
 
Importance: This task is crucial for my professional development, so please conduct a thorough and accurate analysis.
 
----------------

> <Employee phone call transcription with customer>: {transcription} </Employee phone call transcription with customer>
 
Your insightful and detailed evaluation of the customer support call advisor techniques is essential.""")
    ]
) | openai | StrOutputParser()

summarizer_prompt = ChatPromptTemplate.from_messages(
    [
("user","""Summarize the following customer support call.\
which is delimited with XML tag in a single paragraph. Then write a markdown list of the speakers and each of their key points. Finally, list the next steps or action items suggested by the speakers, if any.
    
-------------
    
> <Employee phone call transcription with customer>: {transcription} <Employee phone call transcription with customer>""")

]) | openai | StrOutputParser()
