from transitions import Machine


class DebateMachine(Machine):
    """The Debate FSM"""

    states = ["user_turn", "system_turn", "conclusion"]

    transitions = [
        {
            "trigger": "user_input",
            "source": "user_turn",
            "dest": "system_turn",
            "after": "add_user_utterance",
        },
        {
            "trigger": "system_response",
            "source": "system_turn",
            "dest": "user_turn",
            "after": "add_system_utterance",
        },
        {
            "trigger": "request_conclusion",
            "source": "system_turn",
            "dest": "conclusion",
        },
        {
            "trigger": "user_approves_to_conclude",
            "source": "conclusion",
            "dest": "user_turn",
            "after": "reset_debate",
        },
        {
            "trigger": "user_rejects_to_conclude",
            "source": "conclusion",
            "dest": "system_turn",
        },
        {
            "trigger": "start_new_debate",
            "source": "system_turn",
            "dest": "user_turn",
            "after": "reset_debate",
        },
    ]

    initial = "user_turn"

    def __init__(self, model, **kwargs):
        super().__init__(
            model=model,
            states=DebateMachine.states,
            transitions=DebateMachine.transitions,
            initial=DebateMachine.initial,
            auto_transitions=False,
            **kwargs,
        )
