# LangGraph Agent Lab

Agente aritmetico construido con LangGraph y Gemini. Este proyecto funciona
como laboratorio para entender herramientas, grafos, memoria de corto plazo y
Human-in-the-Loop (HITL) mediante codigo ejecutable.

> Nota: el modelo inicial `gemini-2.5-flash` produjo un error `404 NOT_FOUND`
> para usuarios nuevos. Se actualizo a `gemini-3.6-flash`, que es el modelo
> estable recomendado por la respuesta de la API y la documentacion actual.

## Que hace

1. Recibe una solicitud en lenguaje natural.
2. Gemini decide si necesita una herramienta.
3. LangGraph ejecuta `add`, `multiply` o `divide`.
4. Si la herramienta es `divide`, el grafo se pausa y solicita aprobacion.
5. El resultado queda guardado en el hilo mediante `InMemorySaver`.

## Arquitectura

```text
Usuario
  |
  v
START --> llm_call --(hay tool_calls)--> tool_node --+--> llm_call
             |                                       |
             +------------(sin tools)--------------> END
                                                     |
                              divide                 |
                         interrupt(approval)         |
                              |                      |
                    Command(resume=yes/no) ----------+
```

### Responsabilidad de cada modulo

```text
app/
├── config.py                 # Carga .env y configura Gemini
├── state.py                  # Define el estado compartido del grafo
├── tools.py                  # Funciones expuestas como herramientas
├── nodes.py                  # Nodos, ejecucion de tools y enrutamiento
├── graph.py                  # Ensambla nodos, edges y checkpointer
├── main.py                   # Demo interactivo del agente
└── langgraph_quickstart.py   # Punto de entrada como modulo

tests/
└── test_tools.py             # Pruebas locales sin consumir API
```

## Conceptos importantes

### Estado

`MessagesState` es un `TypedDict` con dos datos:

- `messages`: historial de mensajes del usuario, modelo y herramientas.
- `llm_calls`: contador de llamadas al modelo.

El anotador `operator.add` indica que los mensajes nuevos se agregan al
historial en vez de reemplazarlo.

### Nodos

- `llm_call`: envia el historial a Gemini y permite que el modelo solicite una
  herramienta.
- `tool_node`: ejecuta las herramientas solicitadas. Antes de `divide`, llama a
  `interrupt` y detiene el grafo.
- `should_continue`: devuelve `tool_node` si Gemini pidio una herramienta o
  `END` si ya existe una respuesta final.

### Edges

- `START -> llm_call`: inicia el flujo.
- `llm_call -> tool_node`: ocurre cuando hay una llamada a herramienta.
- `llm_call -> END`: ocurre cuando Gemini responde sin herramientas.
- `tool_node -> llm_call`: devuelve el resultado de la herramienta al modelo.

### Memoria de corto plazo

`InMemorySaver` guarda checkpoints en RAM. El `thread_id` identifica la
conversacion:

```python
config = {"configurable": {"thread_id": "demo-gemini"}}
agent.invoke(input_data, config)
```

El mismo `thread_id` permite que la segunda solicitud recuerde el resultado de
la primera. Esta memoria desaparece al cerrar el proceso; para produccion se
puede cambiar por PostgreSQL o Redis.

### Human-in-the-Loop

Cuando el modelo pide dividir, `tool_node` ejecuta:

```python
approval = interrupt({"type": "approval", "operation": args})
```

El grafo conserva el estado gracias al checkpointer. `main.py` muestra la
interrupcion y luego continua con:

```python
agent.invoke(Command(resume="yes"), config)
```

Con `yes` o `si`, se ejecuta la division. Con `no`, se genera un
`ToolMessage` que informa que la operacion fue rechazada.

Cuando la aprobacion es negativa, el estado incluye `halted=True`. Esto evita
que el modelo vuelva a solicitar automaticamente la misma herramienta despues
del rechazo.

### Manejo basico de errores

La herramienta `divide` valida el divisor y lanza un `ValueError` si es cero.
Ademas, `tool_node` captura errores de argumentos o valores y los devuelve como
un `ToolMessage`, de modo que el modelo pueda explicar el problema sin cerrar
todo el flujo.

## Instalacion

Requisito: Python 3.11 o superior.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configurar Gemini

1. Crea una clave en [Google AI Studio](https://aistudio.google.com/apikey).
2. Copia la plantilla:

```powershell
Copy-Item .env.example .env
notepad .env
```

3. Completa el archivo `.env`:

```env
GOOGLE_API_KEY=tu_clave_de_google_ai_studio
```

Tambien se acepta `GEMINI_API_KEY`. No compartas `.env` ni incluyas claves en
Git. El nivel gratuito tiene limites de solicitudes y puede cambiar según la
cuenta y el modelo.

## Quickstart ejecutable

Desde la raiz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m app.langgraph_quickstart
```

El programa suma 3 y 4, intenta dividir el resultado entre 2 y solicita
aprobacion. Escribe `yes` para aprobar o `no` para rechazar.

## Pruebas locales

Las herramientas se prueban sin API porque son funciones Python:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Validaciones adicionales:

```powershell
.\.venv\Scripts\python.exe -m py_compile app\*.py
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip show langgraph langchain-google-genai
```

## Ficha para el catalogo vivo

### Madurez y adopcion

LangGraph es un framework de orquestacion de agentes de LangChain. Su modelo de
grafos explicitos es apropiado cuando se necesita controlar estados, ciclos,
checkpoints e interrupciones.

### Curva de aprendizaje

Media. Hay que entender estado, nodos, edges, reducers y configuracion por
`thread_id`, pero el flujo es visible y depurable.

### Capacidades observadas

- Tool use: si, mediante `@tool` y `bind_tools`.
- Memoria: si, corto plazo con `InMemorySaver`.
- Multiagente: posible mediante subgraphs, aun no implementado en este demo.
- HITL: si, mediante `interrupt` y `Command(resume=...)`.
- Observabilidad: el grafo se puede inspeccionar y conectar con LangSmith; no se
  configura una cuenta de observabilidad en este prototipo.

### Costo

LangGraph se instala como paquete Python. El costo real del quickstart es el
consumo del proveedor de modelo; Gemini puede ofrecer nivel gratuito con cuotas
y limites. La persistencia administrada y la observabilidad pueden agregar
costos según el servicio elegido.

### Riesgo principal

La complejidad aumenta cuando crecen los estados, ciclos y proveedores. Si no se
definen contratos de estado y limites de reintentos, el grafo puede ser difícil
de mantener.

### Recomendacion

**Si**, cuando se necesita control explicito del flujo, memoria, aprobaciones o
recuperacion. **Depende** si el caso solo requiere una cadena lineal sencilla.

### Evidencia de uso

Conserva una captura de la terminal con el quickstart ejecutado, el prompt de
aprobacion HITL y la respuesta `yes` o `no`. Registra tambien el primer error
real y como se resolvio. La suite de pruebas locales aporta evidencia
reproducible sin consumir API.

### Primer error y solucion

Durante la primera ejecucion, Gemini devolvio:

```text
404 NOT_FOUND: This model models/gemini-2.5-flash is no longer available to new users.
```

La causa no estaba en LangGraph ni en el grafo: el identificador del modelo
configurado ya no estaba disponible para cuentas nuevas. Se resolvio cambiando
el modelo en `app/config.py` a `gemini-3.6-flash` y ejecutando nuevamente el
quickstart.

## Limitaciones y riesgos tecnicos

- `InMemorySaver` pierde datos al reiniciar.
- Gemini depende de internet, cuota y disponibilidad del modelo.
- HITL reduce el riesgo de una division no autorizada, pero no sustituye
  validacion de negocio.
- No se deben guardar secretos, datos sensibles ni historiales reales en este
  prototipo sin controles adicionales.

## Fuentes oficiales

- [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangChain Gemini integration](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
- [Gemini API quickstart](https://ai.google.dev/gemini-api/docs/quickstart)