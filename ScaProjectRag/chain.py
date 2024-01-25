from langchain_community.vectorstores import Pinecone
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from operator import itemgetter
from typing import List, Tuple
from langchain.schema import AIMessage, HumanMessage, format_document
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)

PINECONE_INDEX_NAME = "sca-project-rag"
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# from langchain_community.document_loaders import PyPDFDirectoryLoader
# loader = PyPDFDirectoryLoader("ScaProjectRag/pdfs")
# data = loader.load()

# print("data has been loaded.")
# # Split
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=150)
# all_splits = text_splitter.split_documents(data)

# vectorstore = Pinecone.from_documents(
#     documents=all_splits, embedding=OpenAIEmbeddings(), index_name=PINECONE_INDEX_NAME
# )
# retriever = vectorstore.as_retriever()

vectorstore = Pinecone.from_existing_index(PINECONE_INDEX_NAME, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

openai = ChatOpenAI(model="gpt-3.5-turbo-1106")
# Condense a chat history and follow-up question into a standalone question
_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""  # noqa: E501
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# RAG answer synthesis prompt
template = """Answer the question based on the following context. If you cannot find a satisfactory answer within this context, then provide an answer based on your own knowledge:
<context>
{context}
</context>"""
ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ]
)

# Conversational Retrieval Chain
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:
    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))
    return buffer


# User input
class ChatHistory(BaseModel):
    chat_history: List[Tuple[str, str]] = Field(..., extra={"widget": {"type": "chat"}})
    question: str


_search_query = RunnableBranch(
    # If input includes chat_history, we condense it with the follow-up question
    (
        RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
            run_name="HasChatHistoryCheck"
        ),  # Condense follow-up question and chat into a standalone_question
        RunnablePassthrough.assign(
            chat_history=lambda x: _format_chat_history(x["chat_history"])
        )
        | CONDENSE_QUESTION_PROMPT
        | openai
        | StrOutputParser(),
    ),
    # Else, we have no chat history, so just pass through the question
    RunnableLambda(itemgetter("question")),
)

_inputs = RunnableParallel(
    {
        "question": lambda x: x["question"],
        "chat_history": lambda x: _format_chat_history(x["chat_history"]),
        "context": _search_query | retriever | _combine_documents,
    }
).with_types(input_type=ChatHistory)

chain = _inputs | ANSWER_PROMPT | openai | StrOutputParser()