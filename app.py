# app.py

import streamlit as st
from touche_rad.streamlit import Chat
from touche_rad.core import DebateManager

st.title("Touche 2025 RAD Demo")
st.markdown(
    """
    This a demo of the Retrieval Augmented Dabate (RAD) system build by DS@GT CLEF Touche.
    """
)

if "manager" not in st.session_state:
    st.session_state.manager = DebateManager()
Chat(msg_callback=st.session_state.manager.handle_user_message).render()
