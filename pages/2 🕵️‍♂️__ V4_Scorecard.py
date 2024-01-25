import sys,os
import streamlit as st
from pdf_manager import download_pdf

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir)

from main import *

st.set_page_config(page_title="Analyzer", page_icon="🕵️‍♂️")
st.title("V4 Scorecard 🕵️‍♂️")

def perform_and_display_analysis(chain_key, analysis_function, expander_title):
    if st.button(f"Analyze {expander_title}"):
        if chain_key not in st.session_state:
            with st.spinner("Please wait..."):
                res = analysis_function.invoke({"transcription": st.session_state["transcript"]})
                st.session_state[chain_key] = res

    if chain_key in st.session_state:
        with st.expander(expander_title):
            st.markdown(st.session_state[chain_key], unsafe_allow_html=True)
            if Quality_Assurance_Scorecard_Chain:
                
                fixing_line_issue = st.session_state[chain_key].replace("<br>","\n")
                download_pdf(fixing_line_issue, expander_title)
            else:
                download_pdf(st.session_state[chain_key], expander_title)

if "transcript" in st.session_state:

    perform_and_display_analysis("Quality_Assurance_Scorecard_Chain", Quality_Assurance_Scorecard_Chain, "Quality Assurance For Mortgage And Equity Release")

    perform_and_display_analysis("vulnerability_prompt_chain", vulnerability_prompt_chain, "Vulnerability")

    perform_and_display_analysis("objection_prompt", objection_prompt, "Customer Objections")
    
    perform_and_display_analysis("sales_techniques", sales_techniques, "Employee Sales Techniques")

    perform_and_display_analysis("summary_chain", summarizer_prompt, "Summary")
    
    perform_and_display_analysis("sentiment_chain", sentiment_chain, "Overall Customer Sentiment")

else:
    st.info("Please upload your audio first on the homepage.")