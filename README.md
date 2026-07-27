# 🎓 Aulo — Agente RAG de Aula Andina

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42-red)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-orange)
![FAISS](https://img.shields.io/badge/FAISS-vector_store-green)
![Licencia](https://img.shields.io/badge/licencia-MIT-lightgrey)

**Aulo** es un asistente inteligente tipo RAG (Retrieval-Augmented Generation) que responde preguntas de estudiantes de **Aula Andina**, una academia online ficticia para Latinoamérica, basándose exclusivamente en su documentación oficial (4 PDFs + 1 catálogo CSV) y **citando siempre la fuente y la página**.

🔗 **Demo en vivo:** https://TU-APP.streamlit.app *(reemplazar con tu URL)*

## 🧩 El problema que resuelve

El equipo de soporte de Aula Andina recibe todos los días las mismas preguntas: *"¿cuál es la nota para aprobar?"*, *"¿me devuelven la plata?"*, *"¿cuándo llega mi certificado?"*. Las respuestas existen, pero están dispersas en 5 documentos distintos (reglamento, política de reembolsos, FAQ de certificados, programa de becas y catálogo de cursos). Aulo centraliza ese conocimiento en un chat que:

- responde en segundos, 24/7, en español y con tono estudiantil;
- **cita el documento y la página exacta** de cada respuesta;
- **no inventa**: si algo no está documentado, lo dice y deriva a soporte.

## 🏗️ Arquitectura

```mermaid
flowchart LR
    subgraph Preparación offline
        A[PDFs + CSV<br>/documentos] --> B[pypdf / pandas<br>lectura y chunking]
        B --> C[gemini-embedding-001<br>embeddings 768d]
        C --> D[(FAISS IndexFlatIP<br>/indice, versionado)]
    end
    subgraph App Streamlit
        E[Pregunta del estudiante] --> F[Embedding de la consulta]
        F --> D
        D -->|top-4 chunks| G[Prompt con contexto<br>+ guardrail anti-alucinación]
        G --> H[gemini-2.5-flash]
        H --> I[Respuesta + cita de fuente y página]
    end
```

El índice FAISS se construye una vez (`scripts/construir_indice.py`) y se versiona en el repo: la app en producción **no re-embebe los documentos** al arrancar, solo la pregunta del usuario. Arranque rápido y mínimo consumo de cuota.

## 🛠️ Tecnologías

| Componente | Tecnología | Rol |
|---|---|---|
| LLM | Google Gemini 2.5 Flash (`google-genai`) | Generación de respuestas |
| Embeddings | `gemini-embedding-001` (768 dim.) | Vectorización de chunks y consultas |
| Vector store | FAISS (`faiss-cpu`, IndexFlatIP) | Búsqueda por similitud coseno |
| Interfaz + deploy | Streamlit + Streamlit Community Cloud | Chat web público y gratuito |
| Ingesta | `pypdf` (PDF por página) + `pandas` (CSV por fila) | Lectura de documentos |
| Generación de datos | `fpdf2` | Creación reproducible de los PDFs fuente |

## 📁 Estructura del repositorio

```
aulo-rag/
├── app.py                      # Interfaz Streamlit (chat, chips, sidebar)
├── requirements.txt            # Versiones fijas
├── .env.example                # Plantilla de API key
├── src/
│   └── rag.py                  # Núcleo RAG: chunking, embeddings, FAISS, respuesta
├── scripts/
│   ├── generar_documentos.py   # Crea los 4 PDFs + CSV de Aula Andina
│   ├── construir_indice.py     # Construye y guarda el índice FAISS
│   └── evaluar.py              # Corre 10 preguntas y guarda evidencia en Markdown
├── documentos/                 # Fuentes de conocimiento (generadas)
├── indice/                     # Índice FAISS pre-construido (versionado)
├── assets/                     # Capturas de pantalla
└── resultados_evaluacion.md    # Evidencia de la evaluación
```

## 🚀 Instalación y ejecución local

Requisitos: Python 3.11 y una API key gratuita de [Google AI Studio](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/TU-USUARIO/aulo-rag.git
cd aulo-rag
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Windows  (macOS/Linux: cp .env.example .env)
# Editar .env y pegar tu GOOGLE_API_KEY
python scripts/generar_documentos.py   # genera PDFs y CSV
python scripts/construir_indice.py     # construye el índice FAISS
streamlit run app.py
```

## ❓ Preguntas de ejemplo

| # | Pregunta | Fuente esperada |
|---|---|---|
| 1 | ¿Cuál es la nota mínima para aprobar un curso? | reglamento_estudiante.pdf |
| 2 | ¿Qué asistencia mínima necesito para el certificado? | reglamento / faq_certificados |
| 3 | Compré hace 5 días y avancé un 8%, ¿me devuelven todo? | politica_reembolsos.pdf |
| 4 | Llevo 40% del curso hace 3 semanas, ¿cuánto me reembolsan? | politica_reembolsos.pdf |
| 5 | ¿Cuánto tarda la emisión del certificado? | faq_certificados.pdf |
| 6 | ¿Cuánto cuesta reemitir un certificado corregido? | faq_certificados.pdf |
| 7 | ¿Qué becas existen y qué % de descuento dan? | programa_becas.pdf |
| 8 | ¿Cuándo puedo postular a una beca? | programa_becas.pdf |
| 9 | ¿Cuánto cuesta Machine Learning Aplicado y cuándo empieza? | catalogo_cursos.csv |
| 10 | ¿Aula Andina tiene sedes presenciales? | *(no documentado → guardrail)* |

## 💬 Respuestas reales del agente

> ⚠️ Pega aquí 3 respuestas de `resultados_evaluacion.md` (generado por `python scripts/evaluar.py`). Recomendadas: la 3 (reembolso 100%), la 9 (curso del CSV) y la 10 (guardrail anti-alucinación).

**Pregunta:** *(pegar)*

*(pegar respuesta con su línea "Fuente: ...")*

## 🛡️ Guardrail anti-alucinación

El prompt del sistema obliga al modelo a responder únicamente con el contexto recuperado. Ante preguntas fuera de la documentación (ej.: "¿tienen sedes presenciales?"), Aulo responde que la información no está documentada y deriva a `soporte@aulaandina.lat`, en lugar de inventar.

## 📸 Evidencia de deploy

- **URL pública:** https://TU-APP.streamlit.app
- Captura de la app funcionando en producción:

![Captura del deploy](assets/captura_deploy.png)

## ⚠️ Limitaciones y próximos pasos

- La capa gratuita de Gemini tiene límites de solicitudes por minuto y por día; bajo carga alta habría que agregar reintentos con backoff.
- La búsqueda es puramente semántica (top-4); un re-ranker o búsqueda híbrida (BM25 + vectores) mejoraría preguntas muy específicas del catálogo.
- Próximos pasos: memoria conversacional multi-turno con reformulación de preguntas, métricas de calidad automatizadas (RAGAS) y panel de preguntas frecuentes para el equipo de soporte.

---
Proyecto desarrollado para el challenge de Alura · 2026
