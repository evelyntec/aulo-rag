# -*- coding: utf-8 -*-
"""Aulo — asistente RAG de Aula Andina. Interfaz Streamlit.
Uso local: streamlit run app.py
"""
import streamlit as st

from src.rag import (
    crear_cliente,
    obtener_o_construir_indice,
    responder,
    formatear_fuente,
    MODELO_CHAT,
    MODELO_EMBEDDINGS,
)

st.set_page_config(page_title="Aulo · Aula Andina", page_icon="🎓", layout="centered")

PREGUNTAS_SUGERIDAS = [
    "¿Cuál es la nota mínima para aprobar?",
    "¿Cómo funcionan los reembolsos?",
    "¿Qué becas puedo pedir y cuándo?",
    "¿Cuánto cuesta el curso de Machine Learning?",
]


@st.cache_resource(show_spinner="Cargando índice de documentos...")
def inicializar():
    """Crea el cliente y carga (o construye) el índice una sola vez por proceso."""
    cliente = crear_cliente()
    indice, chunks = obtener_o_construir_indice(cliente)
    return cliente, indice, chunks


try:
    cliente, indice, chunks = inicializar()
except Exception as e:
    st.error(f"Error al inicializar: {e}")
    st.info("Verifica que GOOGLE_API_KEY esté definida (archivo .env en local, Secrets en Streamlit Cloud).")
    st.stop()

# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.title("🎓 Aulo")
    st.caption("Asistente estudiantil de **Aula Andina**")
    st.divider()
    fuentes = sorted({c["fuente"] for c in chunks})
    st.markdown("**Documentos indexados**")
    for f in fuentes:
        st.markdown(f"- `{f}`")
    st.metric("Chunks en el índice", len(chunks))
    st.markdown(f"**Modelo de chat:** `{MODELO_CHAT}`")
    st.markdown(f"**Embeddings:** `{MODELO_EMBEDDINGS}`")
    st.divider()
    if st.button("🧹 Limpiar conversación", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

# ------------------------------------------------------------------ Encabezado
st.title("Aulo 🤖")
st.markdown(
    "Hola, soy **Aulo**, el asistente de Aula Andina. Respondo tus dudas sobre "
    "**reglamento, reembolsos, certificados, becas y cursos**, siempre citando el documento oficial."
)

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Chips de preguntas sugeridas
pregunta_chip = None
cols = st.columns(2)
for i, p in enumerate(PREGUNTAS_SUGERIDAS):
    if cols[i % 2].button(p, key=f"chip_{i}", use_container_width=True):
        pregunta_chip = p

# ------------------------------------------------------------------ Historial
for msg in st.session_state.mensajes:
    with st.chat_message(msg["rol"]):
        st.markdown(msg["contenido"])
        if msg.get("fuentes"):
            with st.expander("📄 Fragmentos consultados"):
                for c in msg["fuentes"]:
                    st.caption(f"**{formatear_fuente(c)}** (similitud {c['puntaje']:.2f})")
                    st.text(c["texto"][:300] + ("..." if len(c["texto"]) > 300 else ""))

# ------------------------------------------------------------------ Entrada
pregunta = st.chat_input("Escribe tu pregunta...") or pregunta_chip

if pregunta:
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)
    with st.chat_message("assistant"):
        with st.spinner("Buscando en la documentación..."):
            try:
                r = responder(cliente, indice, chunks, pregunta)
                st.markdown(r["respuesta"])
                with st.expander("📄 Fragmentos consultados"):
                    for c in r["fuentes"]:
                        st.caption(f"**{formatear_fuente(c)}** (similitud {c['puntaje']:.2f})")
                        st.text(c["texto"][:300] + ("..." if len(c["texto"]) > 300 else ""))
                st.session_state.mensajes.append(
                    {"rol": "assistant", "contenido": r["respuesta"], "fuentes": r["fuentes"]}
                )
            except Exception as e:
                st.error(f"Ocurrió un error al responder: {e}")
