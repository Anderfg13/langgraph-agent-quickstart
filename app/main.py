"""Punto de entrada para ejecutar el demo interactivo del agente."""

from langchain.messages import HumanMessage
from langgraph.types import Command

from app.graph import build_agent


def run_demo():
    """Ejecuta una conversacion de suma y division con aprobacion HITL.

    La primera consulta demuestra continuidad de memoria. La segunda provoca
    una interrupcion antes de dividir y solicita al usuario una respuesta.
    """

    agent = build_agent()
    config = {"configurable": {"thread_id": "demo-gemini"}}

    first_result = agent.invoke(
        {"messages": [HumanMessage(content="Suma 3 y 4.")]},
        config,
    )
    print("Primera respuesta:")
    first_result["messages"][-1].pretty_print()

    paused_result = agent.invoke(
        {"messages": [HumanMessage(content="Ahora divide ese resultado por 2.")]},
        config,
    )
    if "__interrupt__" in paused_result:
        print("El agente solicito aprobacion para dividir:")
        print(paused_result["__interrupt__"][0].value)

        approval = input("¿Autorizas la division? Escribe yes/no: ")
        final_result = agent.invoke(Command(resume=approval), config)
    else:
        final_result = paused_result

    print("Respuesta final usando el mismo thread_id:")
    final_result["messages"][-1].pretty_print()
    print(f"LLM calls en el hilo: {final_result['llm_calls']}")