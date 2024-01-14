from langserve.client import RemoteRunnable
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
import PyPDF2,os
import pinecone
import streamlit as st

st.set_page_config(page_title="Chat On Data", page_icon="🤖")
st.title("Chat On Data 💬")

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
    environment=os.getenv("PINECONE_ENVIRONMENT"),  # next to api key in console
)

embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
PINECONE_INDEX_NAME = "sca-project-rag"

def read_pdf_content(pdf_path):

        pdf_reader = PyPDF2.PdfReader(pdf_path)

        full_text = ""

        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=150)
        texts = text_splitter.split_text(full_text)

        index = pinecone.Index(PINECONE_INDEX_NAME)

        vectorstore = Pinecone(index,embeddings,text_key="text")

        vectorstore.add_texts(texts)

upload_pdf = st.file_uploader(
    "Upload a PDF file", type=["pdf"], accept_multiple_files=False
)

if upload_pdf is not None:
    with st.spinner("Processing PDF..."):
        pdf_content = read_pdf_content(upload_pdf)
        st.success("The PDF has been embedded into the database.")
        
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

msgs = StreamlitChatMessageHistory(key="rag_langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Let's chat on your data!")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

for msg in msgs.messages:
    avatar = USER_AVATAR if msg.type == "human" else BOT_AVATAR
    st.chat_message(msg.type,avatar=avatar).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human",avatar=USER_AVATAR).write(prompt)
    msgs.add_user_message(prompt)

    with st.chat_message("assistant",avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        
        messages = st.session_state.rag_langchain_messages[0:40]
        chat_history = [(messages[i].content, messages[i+1].content) for i in range(0, len(messages)-1, 2)]

        with st.spinner("Thinking..."):
            from ..ScaProjectRag.chain import chain as conversation_chain
            response = conversation_chain.stream({"question":prompt,"chat_history":chat_history})

            for res in response:
                full_response += res or "" 
                message_placeholder.markdown(full_response + "|")
                message_placeholder.markdown(full_response)

        msgs.add_ai_message(full_response)
