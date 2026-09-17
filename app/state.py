"""Tipos de estado compartidos entre los nodos de LangGraph."""

import operator
from typing import Annotated

from langchain.messages import AnyMessage
from typing_extensions import TypedDict


class MessagesState(TypedDict):
    """Estado minimo que viaja por el grafo.

    Attributes:
        messages: Historial acumulado de mensajes del usuario, del modelo y de
            las herramientas. El reducer agrega mensajes nuevos al historial.
        llm_calls: Cantidad de veces que el nodo del modelo fue ejecutado en el
            hilo actual.
        halted: Indica que el flujo debe terminar después de una decisión humana
            de rechazo.
    """

    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    halted: bool