# Evaluación de Costos, Modelos y Latencia

Clase 3.2 - Ingeniería de Soluciones con Inteligencia Artificial

## Descripción

API REST construida con **FastAPI** que expone un agente conversacional con RAG. El endpoint recibe una conversación, un modelo y una pregunta, y devuelve la respuesta junto con los tokens utilizados.

## Arquitectura

El agente está construido con **LangGraph** e incluye los siguientes nodos:

- `agent` — modelo LLM que decide qué herramienta usar
- `generate_query` — reformula la pregunta para optimizar la búsqueda RAG
- `tools` — ejecuta `rag_search` contra MongoDB Atlas

El endpoint principal es:

```
POST /chat
```

**Body:**
```json
{
  "model": "gpt-4o-mini",
  "conversation": [
    {"role": "system", "content": "Eres un asistente útil."}
  ],
  "question": "¿Qué es LangGraph?"
}
```

**Respuesta:**
```json
{
  "answer": "LangGraph es...",
  "prompt_tokens": 120,
  "completion_tokens": 45
}
```

## Ejecución

```bash
docker build -t ejercicio-api .
docker run -p 8000:8000 --env-file .env ejercicio-api
```

Documentación interactiva disponible en: `http://localhost:8000/docs`

## Variables de entorno

Crear un archivo `.env` con:
```
OPENAI_API_KEY=...
MONGODB_CONNECTION_STRING=...
```

---

## Actividades

### Actividad 1 — Evaluación de costos, modelos y latencia

Utiliza el endpoint `/chat` para comparar el comportamiento del agente con distintos modelos de OpenAI. Debes realizar al menos **5 consultas por modelo** usando los siguientes:

- `gpt-4o-mini`
- `gpt-4o`
- `gpt-3.5-turbo`

Para cada combinación, registra:

| Modelo | Pregunta | Prompt tokens | Completion tokens | Latencia (ms) | Costo estimado (USD) |
|--------|----------|---------------|-------------------|---------------|----------------------|
| ...    | ...      | ...           | ...               | ...           | ...                  |

> Para medir la latencia puedes usar el tiempo de respuesta del cliente HTTP (Postman, curl, etc.).
> Para el costo estimado consulta los precios oficiales en [https://openai.com/pricing](https://openai.com/pricing).

**Entregable:** tabla completada con los resultados de tus pruebas y un párrafo con tus conclusiones: ¿qué modelo ofrece el mejor balance entre costo, calidad y velocidad para este caso de uso?

---

### Actividad 2 — Propuesta de mejoras para reducir la latencia

A partir de los resultados de la Actividad 1, analiza el código del agente e identifica al menos **3 mejoras concretas** que podrían reducir la latencia de la solución.

Para cada mejora indica:

1. **Qué parte del código afecta** (nodo, función, configuración)
2. **Por qué genera latencia actualmente**
3. **Cómo lo mejorarías**

Algunas áreas a considerar:

- El nodo `generate_query`: ¿es siempre necesario reformular la query?
- Las llamadas al LLM: ¿se pueden reducir o paralelizar?
- El modelo utilizado: ¿afecta la latencia además del costo?
- La búsqueda en MongoDB: ¿hay parámetros que impacten el tiempo?

**Entregable:** documento o comentarios en el código con las 3 mejoras propuestas, justificadas con los datos de la Actividad 1.
