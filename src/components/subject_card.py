import streamlit as st

def subject_card(name, code, section, stats=None, footer_callback=None):
    html = f"""
        <div style="background: white; border: 1px solid #cbd5e1; border-left: 8px solid #EB459E; padding: 25px; border-radius: 20px; margin-bottom: 20px; font-family: 'Outfit', sans-serif;">
            <h3 style="margin:0; color:#1e293b; font-size:1.5rem; font-family: 'Outfit', sans-serif;">{name}</h3>
            <p style="color:#64748b; margin:10px 0; font-family: 'Outfit', sans-serif;">Code: <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:5px; font-family: 'Outfit', sans-serif;">{code}</span> | Section: {section}</p>
        """
    
    if stats:
        html += """
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:15px; font-family: 'Outfit', sans-serif;">
        """
        for icon, label, value in stats:
            html += f'<div style="background:#EB459E10; padding:5px 12px; border-radius:12px; font-size:0.9rem; font-family: \'Outfit\', sans-serif;"> {icon} <b>{value} </b> {label} </div>'
        html += "</div>"
        
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
    if footer_callback:
        footer_callback()
