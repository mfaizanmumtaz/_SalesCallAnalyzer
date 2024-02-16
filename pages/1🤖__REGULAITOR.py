from langchain_openai.chat_models import ChatOpenAI
from pdf_manager import download_pdf
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import streamlit as st

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema.messages import HumanMessage,AIMessage
from langchain_core.runnables import RunnablePassthrough

st.set_page_config(page_title="Chat On Transcription", page_icon="🤖")
st.title("Chat On Transcription 💬")

def main():
    prompt = ChatPromptTemplate(
        messages=[
SystemMessagePromptTemplate.from_template(
"""You are a helpful assistant.Your task is to answer user questions based on this transcription, delimited with ````. If a user asks about this transcription any question, please assist them courteously and always give your best effort.Please do your best because it is very important to my career.

> ```{transcription}```"""),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{question}")])

    prompt = prompt.partial(transcription=st.session_state["transcript"])

    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    if len(msgs.messages) == 0:
        msgs.add_ai_message("Hello! How can I assist you today?")

    llm_chain = prompt | ChatOpenAI(model="gpt-4-1106-preview")
    USER_AVATAR = "👤"
    BOT_AVATAR = "🤖"
    
    chat = st.session_state["langchain_messages"]
    chat_messages = ""
    for mess in chat:
        if isinstance(mess,HumanMessage):
            chat_messages += f"User: {mess.content}\n\n"
        elif isinstance(mess,AIMessage):
            chat_messages += f"Assistant: {mess.content}\n\n"

    download_pdf(chat_messages,"Chat")

    for msg in msgs.messages:
        avatar = USER_AVATAR if msg.type == "human" else BOT_AVATAR
        st.chat_message(msg.type,avatar=avatar).write(msg.content)
    
    if prompt := st.chat_input():
        st.chat_message("human",avatar=USER_AVATAR).write(prompt)

        with st.chat_message("assistant",avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            
            response = llm_chain.stream({"question":prompt,"chat_history":st.session_state.
                                        langchain_messages[0:40]})
            for res in response:
                full_response += res.content or "" 
                message_placeholder.markdown(full_response + "|")
                message_placeholder.markdown(full_response)

            msgs.add_user_message(prompt)
            msgs.add_ai_message(full_response)

if "transcript" in st.session_state:
    main()
else:
    st.info("Please upload your audio first on the homepage.")
