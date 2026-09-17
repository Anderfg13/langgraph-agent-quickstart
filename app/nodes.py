"""Nodos y reglas de enrutamiento del agente aritmetico."""

from typing import Literal

from langchain.messages import SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import interrupt

from app.config import model
from app.state import MessagesState
from app.tools import tools, tools_by_name


model_with_tools = model.bind_tools(tools)


def llm_call(state: MessagesState):
    """Invoca Gemini con el historial y las herramientas disponibles.

    Args:
        state: Estado actual del grafo, incluyendo el historial de mensajes.

    Returns:
        Actualizacion del estado con la respuesta del modelo y el contador de
        llamadas incrementado.
    """

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
    """Ejecuta las herramientas solicitadas por el ultimo mensaje del modelo.

    Las divisiones requieren aprobacion humana mediante `interrupt`. Los
    errores de argumentos o de valores se convierten en `ToolMessage` para que
    el modelo pueda explicarlos sin terminar todo el grafo.

    Args:
        state: Estado con el ultimo mensaje del modelo y sus tool calls.

    Returns:
        Mensajes con los resultados o errores de las herramientas ejecutadas.
    """

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
                return {"messages": results, "halted": True}

        tool = tools_by_name[tool_call["name"]]
        try:
            observation = tool.invoke(tool_call["args"])
        except (TypeError, ValueError, ZeroDivisionError) as error:
            observation = f"Error al ejecutar {tool.name}: {error}"
        results.append(
            ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
        )
    return {"messages": results}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide si el grafo debe ejecutar tools o terminar.

    Args:
        state: Estado actual del grafo.

    Returns:
        `tool_node` si el modelo solicito una herramienta y el flujo no esta
        detenido; `END` en caso contrario.
    """

    if not state.get("halted", False) and state["messages"][-1].tool_calls:
        return "tool_node"
    return END


def after_tool(state: MessagesState) -> Literal["llm_call", END]:
    """Decide si el grafo vuelve al modelo despues de ejecutar una tool.

    Un rechazo HITL marca el estado como detenido. En ese caso no se vuelve a
    llamar al modelo, porque podria intentar repetir la operacion rechazada.

    Args:
        state: Estado actualizado por `tool_node`.

    Returns:
        `END` si el flujo fue detenido; `llm_call` en cualquier otro caso.
    """

    if state.get("halted", False):
        return END
    return "llm_call"