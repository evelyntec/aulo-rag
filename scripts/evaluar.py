# -*- coding: utf-8 -*-
"""Corre 10 preguntas de prueba contra el agente y guarda la evidencia en Markdown.
Uso: python scripts/evaluar.py
Genera: resultados_evaluacion.md (para pegar en el README)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag import crear_cliente, obtener_o_construir_indice, responder, formatear_fuente

PREGUNTAS = [
    "¿Cuál es la nota mínima para aprobar un curso?",
    "¿Qué asistencia mínima necesito para obtener el certificado?",
    "Compré un curso hace 5 días y avancé un 8%, ¿me devuelven todo el dinero?",
    "Llevo un 40% del curso y lo compré hace 3 semanas, ¿cuánto me reembolsan?",
    "¿Cuánto tarda la emisión del certificado y dónde lo descargo?",
    "¿Cuánto cuesta reemitir un certificado con el nombre corregido?",
    "¿Qué becas existen y qué porcentaje de descuento da cada una?",
    "¿Cuándo puedo postular a una beca?",
    "¿Cuánto cuesta el curso de Machine Learning Aplicado y cuándo empieza?",
    "¿Aula Andina tiene sedes presenciales en Santiago?",  # NO está documentado: debe activarse el guardrail
]

if __name__ == "__main__":
    cliente = crear_cliente()
    indice, chunks = obtener_o_construir_indice(cliente)
    lineas = ["# Resultados de evaluación de Aulo\n"]
    for i, pregunta in enumerate(PREGUNTAS, 1):
        print(f"\n[{i}/10] {pregunta}")
        r = responder(cliente, indice, chunks, pregunta)
        fuentes = sorted({formatear_fuente(c) for c in r["fuentes"]})
        print(r["respuesta"])
        lineas.append(f"### {i}. {pregunta}\n\n{r['respuesta']}\n")
        lineas.append(f"*Chunks recuperados de:* {', '.join(fuentes)}\n")
        time.sleep(8)  # respeta el límite de solicitudes por minuto de la capa gratuita
    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resultados_evaluacion.md")
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    print(f"\n[OK] Evidencia guardada en {salida}")
