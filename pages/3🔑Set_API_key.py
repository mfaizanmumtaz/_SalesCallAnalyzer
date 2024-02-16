import streamlit as st

def get_api_key():
    st.info("Please Set your OpenAI API Paid Account key.")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

    if st.button('Save API Key'):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
    
        else:
            st.session_state.api_key = openai_api_key
            st.write("API key saved successfully!")
            
get_api_key()