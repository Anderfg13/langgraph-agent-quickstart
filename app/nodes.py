from typing import Literal

from langchain.messages import SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import interrupt

from app.config import model
from app.state import MessagesState
from app.tools import tools, tools_by_name


model_with_tools = model.bind_tools(tools)


def llm_call(state: MessagesState):
    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content=(
                            "Eres un asistente que resuelve operaciones aritmeticas "
                            "usando las herramientas disponibles."
                        )
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def tool_node(state: MessagesState):
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        if tool_call["name"] == "divide":
            approval = interrupt(
                {
                    "type": "approval",
                    "message": "El agente quiere realizar una division. ¿La autorizas?",
                    "operation": tool_call["args"],
                }
            )

            if str(approval).strip().lower() not in {"yes", "si", "sí"}:
                results.append(
                    ToolMessage(
                        content="La division fue rechazada por el usuario.",
                        tool_call_id=tool_call["id"],
                    )
                )
                continue

        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
        )
    return {"messages": results}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END