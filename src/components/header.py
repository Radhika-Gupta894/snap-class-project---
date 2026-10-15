import streamlit as st

def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px; margin-top:30px; white-space:nowrap;">
            <img src='{logo_url}' style='height:100px;' />
            <h1 style='text-align:center; color:#E0E3FF; font-size:3.5rem; line-height:1.0; margin-top:10px; word-break:keep-all; overflow-wrap:normal;'>SNAP<br/>CLASS</h1>
        </div>   
        """, unsafe_allow_html=True)
    
def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:start; gap:15px; margin-top:30px; white-space:nowrap;">
            <img src='{logo_url}' style='height:75px;' />
            <h1 style='text-align:left; color:#5865F2; font-size:2.5rem; line-height:1.0; margin:0; word-break:keep-all; overflow-wrap:normal;'>SNAP<br/>CLASS</h1>
        </div>   
        """, unsafe_allow_html=True)