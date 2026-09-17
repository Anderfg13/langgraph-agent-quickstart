# LangGraph quickstart

Este proyecto sigue el quickstart oficial de LangGraph con la Graph API: un
agente decide cuando usar herramientas de suma, multiplicacion y division. Usa
Gemini mediante la integracion oficial de LangChain, en lugar de Anthropic.

## Estructura del codigo

```text
app/
├── config.py                 # Configuracion de Gemini
├── state.py                  # Estado compartido del grafo
├── tools.py                  # Herramientas aritmeticas
├── nodes.py                  # Nodos y decisiones del agente
├── graph.py                  # Construccion del grafo y memoria
├── main.py                   # Demo ejecutable
└── langgraph_quickstart.py   # Lanzador compatible
```

## 1. Activar el entorno

En PowerShell, desde esta carpeta:

```powershell
\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activacion, puedes ejecutar los comandos usando
directamente `\.venv\Scripts\python.exe`.

## 2. Configurar la clave del modelo

El quickstart necesita una clave de Google AI Studio. Puedes crearla gratis
desde https://aistudio.google.com/apikey y guardarla solo en tu maquina:

```powershell
Copy-Item .env.example .env
notepad .env
```

Reemplaza el valor de `GOOGLE_API_KEY` en `.env`. Tambien se acepta
`GEMINI_API_KEY`. No publiques ese archivo.

## 3. Instalar o actualizar dependencias

```powershell
\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Ejecutar el agente

```powershell
\.venv\Scripts\python.exe -m app.langgraph_quickstart
```

La salida debe mostrar dos respuestas. La segunda usa el resultado de la
primera porque ambas ejecuciones comparten el mismo `thread_id`.

## Que acabamos de agregar: memoria de corto plazo

`InMemorySaver` guarda checkpoints del estado del grafo en RAM. El diccionario
`config` identifica la conversacion mediante `thread_id`. Por eso la segunda
llamada puede entender "ese resultado" sin que le pasemos manualmente todo el
historial.

Esta memoria se pierde al cerrar el programa. Para produccion, LangGraph ofrece
checkpointers persistentes como PostgreSQL o Redis. Mas adelante podemos agregar
uno de esos, o una memoria de largo plazo con `InMemoryStore`.

## Evidencia para la ficha

Captura la terminal mostrando el comando y la salida. Anota tambien:

- Version de Python: `\.venv\Scripts\python.exe --version`
- Versiones instaladas: `\.venv\Scripts\python.exe -m pip show langgraph langchain`
- Cantidad de llamadas al modelo que imprime el agente.
- El primer error que aparezca, si ocurre, y el cambio que lo resolvio.

## Fuentes oficiales

- Quickstart: https://docs.langchain.com/oss/python/langgraph/quickstart
- Integracion Gemini: https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai
- API de Gemini: https://ai.google.dev/gemini-api/docs/quickstart# langgraph-agent-quickstart
