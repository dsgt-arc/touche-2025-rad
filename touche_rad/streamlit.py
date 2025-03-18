import streamlit as st
from touche_rad.ai import Message


class Chat:
    def __init__(self, msg_callback):
        self.callback = msg_callback
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def _handle_user(self, content):
        st.session_state.messages.append(Message(role="user", content=content))

    def _handle_assistant(self):
        new_state = self.callback(st.session_state.messages[-1].content)
        st.session_state.messages.append(Message(role="assistant", content=new_state))

    def _display_messages(self):
        for message in st.session_state.messages:
            with st.chat_message(message.role):
                st.markdown(message.content)

    def render(self):
        if content := st.chat_input("Ask me something."):
            self._handle_user(content)
            self._handle_assistant()
        self._display_messages()
