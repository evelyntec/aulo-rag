# -*- coding: utf-8 -*-
"""Construye el índice FAISS y lo guarda en /indice (se versiona en el repo).
Uso: python scripts/construir_indice.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag import crear_cliente, construir_indice, cargar_chunks

if __name__ == "__main__":
    print("Leyendo documentos y contando chunks...")
    chunks = cargar_chunks()
    fuentes = sorted({c["fuente"] for c in chunks})
    print(f"Documentos: {len(fuentes)} | Chunks totales: {len(chunks)}")
    for f in fuentes:
        print(f"  - {f}: {sum(1 for c in chunks if c['fuente'] == f)} chunks")
    print("\nGenerando embeddings y construyendo el índice FAISS...")
    cliente = crear_cliente()
    construir_indice(cliente)
    print("[OK] Índice guardado en /indice (aulo.faiss + chunks.json)")
