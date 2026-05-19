import requests
import time
import pandas as pd

URL = "https://ejercicio-api-997382465313.northamerica-northeast1.run.app/chat"

# Precios USD por token — fuente: platform.openai.com/docs/pricing
PRECIOS = {
    "gpt-4o": {
        "input_per_token":  2.50 / 1_000_000,
        "output_per_token": 10.00 / 1_000_000,
    },
    "gpt-4o-mini": {
        "input_per_token":  0.150 / 1_000_000,
        "output_per_token": 0.600 / 1_000_000,
    },
    "gpt-4.1-mini": {
        "input_per_token":  0.40 / 1_000_000,
        "output_per_token": 1.60 / 1_000_000,
    },
}

PREGUNTAS = [
    "que es la inteligencia artificial?",
    "Quien es el profesor del curso?",
    "Que es un token?",
    "¿Cuales tecnicas de prompt engineering existente?",
    "Cuales metricas de RAG existen?",
    "Que son las tools?",
    "Que es la memoria en los agentes",
    "que es el prompt engineering?",
    "Que es un agente?",
]


URL = "https://ejercicio-api-997382465313.northamerica-northeast1.run.app/chat"
data = {
    "model": 'gpt-4.1-mini',
    "conversation": [{"role": "system", "content": "Eres un asistente util."}],
    "question": PREGUNTAS[0],
}

inicio = time.time()
response = requests.post(URL, json=data)

print(response.content)