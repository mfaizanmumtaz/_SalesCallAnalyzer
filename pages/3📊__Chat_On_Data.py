from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.messages import HumanMessage,AIMessage
from pdf_manager import download_pdf
import streamlit as st

st.set_page_config(page_title="Chat On Data", page_icon="🤖")
st.title("Chat On Data 💬")
        
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

msgs = StreamlitChatMessageHistory(key="rag_langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("Let's chat on your data!")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

chat = st.session_state["rag_langchain_messages"]
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
        # manage history
        messages = st.session_state.rag_langchain_messages[1:40]
        chat_history = [(messages[i].content, messages[i+1].content) for i in range(0, len(messages)-1, 2)]

        with st.spinner("Thinking..."):
            from ScaProjectRag.chain import chain as conversation_chain
            response = conversation_chain.stream({"question":prompt,"chat_history":chat_history})

            for res in response:
                full_response += res or "" 
                message_placeholder.markdown(full_response + "|")
                message_placeholder.markdown(full_response)

        msgs.add_user_message(prompt)
        msgs.add_ai_message(full_response)
