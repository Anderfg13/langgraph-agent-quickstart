"""Construccion del grafo y configuracion de persistencia temporal."""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.nodes import after_tool, llm_call, should_continue, tool_node
from app.state import MessagesState


def build_agent():
    """Construye y compila el agente aritmetico.

    Returns:
        Un grafo compilado con nodos para llamar al modelo y ejecutar tools,
        memoria de corto plazo en RAM y soporte para interrupciones HITL.
    """

    agent_builder = StateGraph(MessagesState)
    agent_builder.add_node("llm_call", llm_call)
    agent_builder.add_node("tool_node", tool_node)
    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges(
        "llm_call", should_continue, ["tool_node", END]
    )
    agent_builder.add_conditional_edges(
        "tool_node", after_tool, ["llm_call", END]
    )

    checkpointer = InMemorySaver()
    return agent_builder.compile(checkpointer=checkpointer)