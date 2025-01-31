import streamlit as st


class Chat:
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def _handle_user(self, content):
        st.session_state.messages.append(
            {
                "role": "user",
                "content": content,
            }
        )

    def _handle_assistant(self, content):
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f'You said "{content}"',
            }
        )

    def _display_messages(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render(self):
        if content := st.chat_input("Ask me something."):
            self._handle_user(content)
            self._handle_assistant(content)
        self._display_messages()
