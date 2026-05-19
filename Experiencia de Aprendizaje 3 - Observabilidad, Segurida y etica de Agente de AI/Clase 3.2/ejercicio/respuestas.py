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


resultados = []

for modelo in PRECIOS:
    print(f"\n>>> Modelo: {modelo}")
    for i, pregunta in enumerate(PREGUNTAS, 1):
        data = {
            "model": modelo,
            "conversation": [{"role": "system", "content": "Eres un asistente util."}],
            "question": pregunta,
        }

        inicio = time.time() ### el tiempo 14;50:10 
        ###
        response = requests.post(URL, json=data)
        latencia_s = (time.time() - inicio) ## el tiempo en esta linea  14:50:15 (time.time()) 
        #


        if response.status_code == 200:
            resp = response.json()
            prompt_tokens = resp.get("prompt_tokens", 0)
            completion_tokens = resp.get("completion_tokens", 0)
            precio = PRECIOS[modelo]
            costo = (
                prompt_tokens * precio["input_per_token"]
                + completion_tokens * precio["output_per_token"]
            )
            resultados.append({
                "Modelo":               modelo,
                "Pregunta":             pregunta,
                "Prompt tokens":        prompt_tokens,
                "Completion tokens":    completion_tokens,
                "Latencia (s)":        round(latencia_s, 4),
                "Costo estimado (USD)": round(costo, 6),
            })
            print(f"  [{i:02d}] OK - {prompt_tokens}p + {completion_tokens}c tokens | {latencia_s:.2f} s")
        else:
            print(f"  [{i:02d}] ERROR {response.status_code}: {pregunta}")

df = pd.DataFrame(resultados)

pd.set_option("display.max_colwidth", 45)
pd.set_option("display.float_format", "{:.4f}".format)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", 140)

print("\n" + "=" * 140)
print("RESULTADOS POR MODELO")
print("=" * 140)

for modelo, grupo in df.groupby("Modelo"):
    print(f"\n--- {modelo} ---")
    print(grupo.drop(columns="Modelo").to_string(index=False))
    print(
        f"  TOTAL | prompt={grupo['Prompt tokens'].sum()} | "
        f"completion={grupo['Completion tokens'].sum()} | "
        f"latencia_avg={grupo['Latencia (s)'].mean():.0f} s | "
        f"costo_total=${grupo['Costo estimado (USD)'].sum():.6f}"
    )
