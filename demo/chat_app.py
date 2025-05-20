# app.py

import streamlit as st
from touche_rad.streamlit import Chat
from touche_rad.core import DebateManager
from touche_rad.ai import TensorZeroClient

st.title("Touche 2025 RAD Demo")
st.markdown(
    """
    This a demo of the Retrieval Augmented Dabate (RAD) system build by DS@GT CLEF Touche.
    """
)
client = TensorZeroClient()
if "manager" not in st.session_state:
    st.session_state.manager = DebateManager(client=client, strategy_name="rag")
Chat(msg_callback=st.session_state.manager.handle_user_message).render()
