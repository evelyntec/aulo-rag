# -*- coding: utf-8 -*-
"""Núcleo RAG de Aulo: lectura de documentos, embeddings, índice FAISS y respuesta."""
import os
import json
import time

import numpy as np
import faiss
import pandas as pd
from pypdf import PdfReader
from google import genai
from google.genai import types

# --- Configuración central ---
MODELO_CHAT = "gemini-2.5-flash"
MODELO_EMBEDDINGS = "gemini-embedding-001"
DIMENSION = 768          # dimensión reducida: más liviana y suficiente para este caso
TAM_CHUNK = 1100         # caracteres por chunk
SOLAPE = 150             # solape entre chunks
TOP_K = 4                # chunks recuperados por pregunta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DOCS = os.path.join(RAIZ, "documentos")
DIR_INDICE = os.path.join(RAIZ, "indice")
RUTA_FAISS = os.path.join(DIR_INDICE, "aulo.faiss")
RUTA_CHUNKS = os.path.join(DIR_INDICE, "chunks.json")

PROMPT_SISTEMA = """Eres Aulo, el asistente estudiantil de Aula Andina, una plataforma de cursos online para Latinoamérica.

Reglas estrictas:
1. Responde SOLO con la información del CONTEXTO entregado. No uses conocimiento externo ni inventes datos, plazos, montos o políticas.
2. Si el contexto no contiene la respuesta, di exactamente: "Esa información no está en la documentación de Aula Andina. Te recomiendo escribir a soporte@aulaandina.lat para resolverlo." y nada más.
3. Responde en español, en tono cercano y claro, en máximo 5 frases o una lista breve. Sé concreto: cita plazos, montos y porcentajes tal como aparecen en el contexto.
4. Al final de la respuesta, en una línea nueva, indica la fuente con el formato: "Fuente: <archivo>, página <n>" (una línea por cada fuente usada; para el catálogo CSV omite la página).
5. No des consejos legales ni prometas excepciones a las políticas."""


def obtener_api_key():
    """Busca la API key en variables de entorno, .env o secrets de Streamlit."""
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    # .env en la raíz del proyecto (para scripts locales)
    ruta_env = os.path.join(RAIZ, ".env")
    if os.path.exists(ruta_env):
        with open(ruta_env, encoding="utf-8") as f:
            for linea in f:
                if linea.strip().startswith("GOOGLE_API_KEY"):
                    return linea.split("=", 1)[1].strip().strip('"').strip("'")
    # Secrets de Streamlit (en el deploy)
    try:
        import streamlit as st
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        return None


def crear_cliente():
    key = obtener_api_key()
    if not key:
        raise RuntimeError("No se encontró GOOGLE_API_KEY. Defínela en .env o en los Secrets de Streamlit.")
    return genai.Client(api_key=key)


# ----------------------------------------------------------------- Lectura y chunking
def trocear(texto: str) -> list:
    """Divide un texto largo en chunks con solape."""
    texto = " ".join(texto.split())  # normaliza espacios y saltos
    if len(texto) <= TAM_CHUNK:
        return [texto] if texto else []
    chunks, inicio = [], 0
    while inicio < len(texto):
        chunks.append(texto[inicio:inicio + TAM_CHUNK])
        inicio += TAM_CHUNK - SOLAPE
    return chunks


def cargar_chunks() -> list:
    """Lee los PDFs (por página) y el CSV (por fila) y devuelve la lista de chunks con metadatos."""
    chunks = []
    for archivo in sorted(os.listdir(DIR_DOCS)):
        ruta = os.path.join(DIR_DOCS, archivo)
        if archivo.lower().endswith(".pdf"):
            lector = PdfReader(ruta)
            for num, pagina in enumerate(lector.pages, start=1):
                texto = pagina.extract_text() or ""
                for trozo in trocear(texto):
                    chunks.append({"texto": trozo, "fuente": archivo, "pagina": num})
        elif archivo.lower().endswith(".csv"):
            df = pd.read_csv(ruta)
            for _, fila in df.iterrows():
                # Cada fila del catálogo se convierte en una frase autocontenida
                texto = (
                    f"Curso {fila['codigo']}: '{fila['nombre_curso']}', categoría {fila['categoria']}, "
                    f"nivel {fila['nivel']}, duración {fila['duracion_horas']} horas, "
                    f"precio {fila['precio_usd']} USD, modalidad {fila['modalidad']}, "
                    f"cupos disponibles: {fila['cupos_disponibles']}, fecha de inicio {fila['fecha_inicio']}, "
                    f"docente {fila['docente']}, emite certificado: {fila['certificacion']}."
                )
                chunks.append({"texto": texto, "fuente": archivo, "pagina": None})
    return chunks


# ----------------------------------------------------------------- Embeddings
def _normalizar(matriz: np.ndarray) -> np.ndarray:
    normas = np.linalg.norm(matriz, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    return matriz / normas


def embeber(cliente, textos: list, tipo_tarea: str) -> np.ndarray:
    """Genera embeddings en lotes pequeños (respeta límites de la capa gratuita)."""
    vectores = []
    LOTE = 20
    for i in range(0, len(textos), LOTE):
        lote = textos[i:i + LOTE]
        resp = cliente.models.embed_content(
            model=MODELO_EMBEDDINGS,
            contents=lote,
            config=types.EmbedContentConfig(task_type=tipo_tarea, output_dimensionality=DIMENSION),
        )
        vectores.extend([e.values for e in resp.embeddings])
        if i + LOTE < len(textos):
            time.sleep(1)  # pausa suave para no golpear el límite de solicitudes
    return _normalizar(np.array(vectores, dtype="float32"))


# ----------------------------------------------------------------- Índice FAISS
def construir_indice(cliente):
    """Construye el índice desde /documentos y lo guarda en /indice."""
    chunks = cargar_chunks()
    if not chunks:
        raise RuntimeError("No hay documentos en /documentos. Ejecuta primero scripts/generar_documentos.py")
    vectores = embeber(cliente, [c["texto"] for c in chunks], "RETRIEVAL_DOCUMENT")
    indice = faiss.IndexFlatIP(DIMENSION)  # producto interno + vectores normalizados = similitud coseno
    indice.add(vectores)
    os.makedirs(DIR_INDICE, exist_ok=True)
    faiss.write_index(indice, RUTA_FAISS)
    with open(RUTA_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    return indice, chunks


def cargar_indice():
    """Carga el índice pre-construido del repo (rápido, sin llamadas a la API)."""
    if not (os.path.exists(RUTA_FAISS) and os.path.exists(RUTA_CHUNKS)):
        return None, None
    indice = faiss.read_index(RUTA_FAISS)
    with open(RUTA_CHUNKS, encoding="utf-8") as f:
        chunks = json.load(f)
    return indice, chunks


def obtener_o_construir_indice(cliente):
    indice, chunks = cargar_indice()
    if indice is None:
        indice, chunks = construir_indice(cliente)
    return indice, chunks


# ----------------------------------------------------------------- Búsqueda y respuesta
def buscar(cliente, indice, chunks, pregunta: str, k: int = TOP_K) -> list:
    vector = embeber(cliente, [pregunta], "RETRIEVAL_QUERY")
    puntajes, indices = indice.search(vector, k)
    resultados = []
    for puntaje, idx in zip(puntajes[0], indices[0]):
        if idx == -1:
            continue
        c = chunks[idx]
        resultados.append({**c, "puntaje": float(puntaje)})
    return resultados


def formatear_fuente(c: dict) -> str:
    if c["pagina"]:
        return f"{c['fuente']}, página {c['pagina']}"
    return c["fuente"]


def responder(cliente, indice, chunks, pregunta: str) -> dict:
    """Pipeline completo: busca contexto y genera la respuesta con cita de fuentes."""
    recuperados = buscar(cliente, indice, chunks, pregunta)
    contexto = "\n\n".join(
        f"[Fragmento {i+1} | Fuente: {formatear_fuente(c)}]\n{c['texto']}"
        for i, c in enumerate(recuperados)
    )
    prompt = f"CONTEXTO:\n{contexto}\n\nPREGUNTA DEL ESTUDIANTE:\n{pregunta}"
    respuesta = cliente.models.generate_content(
        model=MODELO_CHAT,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=PROMPT_SISTEMA, temperature=0.1),
    )
    return {"respuesta": respuesta.text, "fuentes": recuperados}
