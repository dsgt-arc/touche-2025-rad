from touche_rad.core import DebateContext, DebateMachine
from transitions.extensions import GraphMachine


m = DebateContext()
machine = GraphMachine(
    model=m,
    states=DebateMachine.states,
    transitions=DebateMachine.transitions,
    initial=DebateMachine.initial,
    auto_transitions=False,
)

output_path = "state_machine.png"
machine.get_graph().draw(output_path, prog="dot", format="png")
print(f"State machine diagram saved to {output_path}")
