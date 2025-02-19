"""Streamlit entry point for the Touch 2025 RAD demo."""

import streamlit as st
from touche_rad.ai import TensorZeroClient, TensorZeroModel
from touche_rad.streamlit import Chat

st.title("Touche 2025 RAD Demo")
st.markdown("""
This a demo of the Retrieval Augmented Dabate (RAD) system build by DS@GT CLEF Touche.
""")

ai_client = TensorZeroClient(model=TensorZeroModel.GPT4_O_MINI)
Chat(chat_client=ai_client).render()
