# app.py

import streamlit as st
from touche_rad.ai import TensorZeroClient, TensorZeroModel
from touche_rad.streamlit import Chat
from touche_rad.core.fsm.manager import DebateManager
from touche_rad.core.strategy.engine import StrategyEngine

st.title("Touche 2025 RAD Demo")
st.markdown("""
This a demo of the Retrieval Augmented Dabate (RAD) system build by DS@GT CLEF Touche.
""")

strategy = StrategyEngine()
debate_manager = DebateManager(
    strategy_engine=strategy, config_file="config/transitions.json"
)

ai_client = TensorZeroClient(model=TensorZeroModel.GPT4_O_MINI)
Chat(chat_client=ai_client).render()
