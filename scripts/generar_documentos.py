# -*- coding: utf-8 -*-
"""Genera los 4 PDFs y el CSV de Aula Andina en /documentos.
Uso: python scripts/generar_documentos.py
"""
import os
import pandas as pd
from fpdf import FPDF

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documentos")
os.makedirs(CARPETA, exist_ok=True)


def limpiar(texto: str) -> str:
    """Reemplaza caracteres fuera de latin-1 (fpdf2 con fuentes core solo soporta latin-1)."""
    reemplazos = {"\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
                  "\u201c": '"', "\u201d": '"', "\u2022": "-", "\u2026": "..."}
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto.encode("latin-1", "replace").decode("latin-1")


class PDFAula(FPDF):
    def __init__(self, titulo):
        super().__init__()
        self.titulo = titulo
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        self.set_font("helvetica", "B", 9)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, limpiar(f"Aula Andina - {self.titulo}"), align="C",
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-14)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Página {self.page_no()}", align="C")

    def seccion(self, titulo):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 7, limpiar(titulo), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def parrafo(self, texto):
        self.set_font("helvetica", "", 10.5)
        self.set_text_color(35, 35, 35)
        self.multi_cell(0, 5.5, limpiar(texto), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


def crear_pdf(nombre_archivo, titulo, secciones):
    pdf = PDFAula(titulo)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.multi_cell(0, 9, limpiar(titulo), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 9)
    pdf.multi_cell(0, 5, limpiar("Aula Andina - Plataforma de cursos online para Latinoamérica. Versión 2026. Documento oficial."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for t, cuerpo in secciones:
        pdf.seccion(t)
        pdf.parrafo(cuerpo)
    ruta = os.path.join(CARPETA, nombre_archivo)
    pdf.output(ruta)
    print(f"[OK] {ruta}")


# ---------------------------------------------------------------- 1. Reglamento
reglamento = [
    ("1. Asistencia mínima",
     "Todo estudiante debe registrar una asistencia mínima del 75% de las clases en vivo o sesiones "
     "sincrónicas del curso. Las clases grabadas vistas dentro de los 7 días posteriores a su emisión "
     "cuentan como asistencia válida. Un estudiante con asistencia inferior al 75% queda en estado "
     "'Reprobado por inasistencia' y no puede optar al certificado."),
    ("2. Nota de aprobación",
     "La escala de evaluación va de 0 a 100 puntos. La nota mínima de aprobación es 70 puntos. "
     "La nota final se calcula como: 40% tareas semanales, 30% proyecto final y 30% evaluaciones parciales. "
     "Los estudiantes con nota final entre 60 y 69 puntos pueden rendir una evaluación de recuperación "
     "dentro de los 10 días corridos siguientes al cierre del curso; la nota máxima alcanzable por esta vía es 70."),
    ("3. Plazos de entrega de tareas",
     "Las tareas semanales deben entregarse dentro de los 7 días corridos desde su publicación en la plataforma. "
     "Se admite una extensión máxima de 3 días adicionales, con una penalización de 10 puntos sobre la nota de esa tarea. "
     "Pasados los 10 días totales, la tarea se califica con 0 puntos. El proyecto final no admite extensiones."),
    ("4. Normas de conducta",
     "Se prohíbe compartir credenciales de acceso, revender contenidos, acosar a otros estudiantes o docentes, "
     "y hacer uso comercial no autorizado del material. El plagio en tareas o en el proyecto final se sanciona "
     "con la calificación 0 en la primera falta y con la suspensión definitiva de la cuenta en caso de reincidencia."),
    ("5. Causales de suspensión de la cuenta",
     "Son causales de suspensión: (a) reincidencia en plagio; (b) compartir o revender credenciales; "
     "(c) acoso comprobado a miembros de la comunidad; (d) fraude en medios de pago; "
     "(e) suplantación de identidad en evaluaciones. La suspensión definitiva no da derecho a reembolso, "
     "conforme a la Política de Reembolsos vigente. El estudiante puede apelar por escrito a "
     "convivencia@aulaandina.lat dentro de los 5 días hábiles siguientes a la notificación."),
    ("6. Soporte y canales oficiales",
     "El canal oficial de soporte es soporte@aulaandina.lat, con tiempo de primera respuesta de 24 horas hábiles. "
     "Las consultas académicas se responden en el foro de cada curso en un máximo de 48 horas hábiles."),
]

# ---------------------------------------------------------------- 2. Reembolsos
reembolsos = [
    ("1. Derecho a retracto (100% de devolución)",
     "El estudiante puede solicitar la devolución del 100% del monto pagado dentro de los 7 días corridos "
     "posteriores a la compra, siempre que haya completado menos del 10% del contenido del curso. "
     "Este derecho aplica a todos los cursos individuales pagados."),
    ("2. Reembolsos parciales según avance",
     "Fuera del período de retracto y hasta 30 días corridos desde la compra, aplican reembolsos parciales: "
     "con menos del 25% del curso completado se devuelve el 75% del monto pagado; "
     "con avance entre 25% y 50% se devuelve el 50% del monto pagado. "
     "Con más del 50% del curso completado, o transcurridos más de 30 días desde la compra, "
     "no procede reembolso alguno."),
    ("3. Casos no reembolsables",
     "No son reembolsables: (a) cursos comprados con descuento promocional igual o superior al 40%; "
     "(b) paquetes o bundles en los que ya se inició más de un curso; "
     "(c) cursos cuyo certificado ya fue emitido; "
     "(d) montos pagados por certificados duplicados; "
     "(e) cuentas suspendidas por infracciones al Reglamento del Estudiante."),
    ("4. Medios y tiempos de devolución",
     "La devolución se realiza siempre por el mismo medio de pago utilizado en la compra. "
     "Tarjetas de crédito o débito: entre 5 y 10 días hábiles según el banco emisor. "
     "Transferencia bancaria o billeteras digitales: hasta 15 días hábiles. "
     "El estudiante recibe un comprobante de reembolso por correo con folio de seguimiento."),
    ("5. Cómo solicitar un reembolso",
     "La solicitud se realiza desde 'Mi cuenta > Mis compras > Solicitar reembolso' o escribiendo a "
     "pagos@aulaandina.lat con el número de orden. El equipo de pagos confirma la procedencia de la "
     "solicitud en un máximo de 3 días hábiles."),
    ("6. Becas y reembolsos",
     "Los cursos cubiertos total o parcialmente por becas solo reembolsan la parte efectivamente pagada "
     "por el estudiante, aplicando las mismas reglas de avance y plazos de este documento."),
]

# ---------------------------------------------------------------- 3. Certificados
certificados = [
    ("1. Requisitos para obtener el certificado",
     "Para obtener el certificado digital de un curso, el estudiante debe cumplir simultáneamente: "
     "(a) nota final igual o superior a 70 puntos; (b) asistencia igual o superior al 75%; "
     "(c) proyecto final entregado y aprobado. Los tres requisitos están definidos en el Reglamento del Estudiante."),
    ("2. Tiempos de emisión",
     "El certificado digital se emite automáticamente dentro de los 5 días hábiles posteriores al cierre "
     "del curso y a la publicación de notas finales. Se descarga en formato PDF desde "
     "'Mi cuenta > Mis certificados'. No se envían certificados físicos."),
    ("3. Verificación de autenticidad",
     "Cada certificado incluye un código único de verificación con formato AA-XXXX-XXXX. "
     "Cualquier persona o empleador puede validar su autenticidad de forma gratuita en "
     "aulaandina.lat/verificar ingresando dicho código."),
    ("4. Certificados duplicados",
     "Si el estudiante pierde el archivo, puede volver a descargarlo sin costo desde su cuenta. "
     "La reemisión con corrección de datos personales (por ejemplo, nombre mal escrito) tiene un costo "
     "de 5 USD y se procesa en un máximo de 3 días hábiles. Este cargo no es reembolsable."),
    ("5. Validez del certificado",
     "Los certificados de Aula Andina tienen validez indefinida y acreditan la aprobación del curso, "
     "su carga horaria y el nombre del docente. No constituyen créditos universitarios ni títulos "
     "profesionales oficiales. Los cursos con campo 'certificacion = Si' en el catálogo son los únicos "
     "que emiten certificado."),
    ("6. Certificados y becas",
     "Los estudiantes becados obtienen el certificado bajo los mismos requisitos académicos, sin costo "
     "adicional, siempre que mantengan su beca activa hasta el cierre del curso."),
]

# ---------------------------------------------------------------- 4. Becas
becas = [
    ("1. Tipos de beca y porcentajes de descuento",
     "Aula Andina ofrece 4 becas: (a) Beca Andina Total: 100% de descuento, orientada a estudiantes en "
     "situación socioeconómica vulnerable; (b) Beca Mujer STEM: 60% de descuento en cursos de las "
     "categorías Programación y Datos para mujeres de Latinoamérica; (c) Beca Impulso: 50% de descuento "
     "para estudiantes de 16 a 24 años; (d) Beca Alumni: 25% de descuento permanente para quienes ya "
     "aprobaron al menos 2 cursos en la plataforma."),
    ("2. Requisitos de postulación",
     "Requisitos comunes: ser mayor de 16 años, residir en Latinoamérica y completar el formulario en "
     "aulaandina.lat/becas. Beca Andina Total exige además documentación socioeconómica y una carta de "
     "motivación. Beca Mujer STEM y Beca Impulso exigen promedio igual o superior a 85 puntos en cursos "
     "previos de la plataforma, o una prueba de admisión online para estudiantes nuevos. "
     "Beca Alumni se activa automáticamente, sin postulación."),
    ("3. Fechas de postulación",
     "Existen dos convocatorias anuales: del 1 al 15 de marzo y del 1 al 15 de agosto. "
     "Los resultados se comunican por correo dentro de los 20 días corridos posteriores al cierre de "
     "cada convocatoria. Fuera de esas fechas no se reciben postulaciones."),
    ("4. Causales de pérdida de la beca",
     "La beca se pierde si el estudiante: (a) obtiene una nota final inferior a 70 puntos en el curso "
     "becado; (b) registra asistencia inferior al 75%; (c) permanece inactivo en la plataforma por más "
     "de 30 días corridos sin justificación; (d) infringe el Reglamento del Estudiante. "
     "Quien pierde una beca puede volver a postular después de 12 meses."),
    ("5. Alcance de las becas",
     "Cada beca cubre 1 curso por convocatoria, salvo la Beca Alumni, que aplica a todas las compras. "
     "Las becas no son acumulables entre sí ni con promociones de descuento igual o superior al 40%. "
     "Las becas no cubren certificados duplicados."),
]

crear_pdf("reglamento_estudiante.pdf", "Reglamento del Estudiante", reglamento)
crear_pdf("politica_reembolsos.pdf", "Política de Reembolsos", reembolsos)
crear_pdf("faq_certificados.pdf", "Preguntas Frecuentes: Certificados", certificados)
crear_pdf("programa_becas.pdf", "Programa de Becas", becas)

# ---------------------------------------------------------------- 5. Catálogo CSV
cursos = [
    ["AA-101", "Python desde Cero", "Programación", "Básico", 40, 49, "Online en vivo", 35, "2026-08-10", "Carla Mendoza", "Si"],
    ["AA-102", "JavaScript Moderno", "Programación", "Básico", 40, 49, "Online en vivo", 28, "2026-08-17", "Diego Fuentes", "Si"],
    ["AA-103", "Java y Programación Orientada a Objetos", "Programación", "Intermedio", 60, 79, "Online en vivo", 22, "2026-09-01", "Diego Fuentes", "Si"],
    ["AA-104", "Desarrollo Web con HTML y CSS", "Programación", "Básico", 30, 39, "A tu ritmo", 100, "2026-08-03", "Valentina Ríos", "Si"],
    ["AA-105", "React y Aplicaciones Frontend", "Programación", "Intermedio", 50, 89, "Online en vivo", 18, "2026-09-07", "Valentina Ríos", "Si"],
    ["AA-106", "APIs REST con FastAPI", "Programación", "Intermedio", 45, 89, "Online en vivo", 25, "2026-09-14", "Carla Mendoza", "Si"],
    ["AA-107", "Git y GitHub Profesional", "Programación", "Básico", 20, 29, "A tu ritmo", 100, "2026-08-03", "Tomás Herrera", "No"],
    ["AA-108", "Testing Automatizado en Python", "Programación", "Avanzado", 40, 99, "Online en vivo", 15, "2026-10-05", "Carla Mendoza", "Si"],
    ["AA-201", "Análisis de Datos con Excel", "Datos", "Básico", 30, 39, "A tu ritmo", 100, "2026-08-03", "Lucía Paredes", "Si"],
    ["AA-202", "SQL para Análisis de Datos", "Datos", "Básico", 35, 49, "Online en vivo", 30, "2026-08-24", "Lucía Paredes", "Si"],
    ["AA-203", "Python para Ciencia de Datos", "Datos", "Intermedio", 60, 99, "Online en vivo", 20, "2026-09-07", "Andrés Soto", "Si"],
    ["AA-204", "Visualización con Power BI", "Datos", "Intermedio", 40, 79, "Online en vivo", 24, "2026-09-14", "Lucía Paredes", "Si"],
    ["AA-205", "Machine Learning Aplicado", "Datos", "Avanzado", 80, 149, "Online en vivo", 12, "2026-10-05", "Andrés Soto", "Si"],
    ["AA-206", "Estadística para Datos", "Datos", "Intermedio", 45, 69, "A tu ritmo", 100, "2026-08-03", "Andrés Soto", "Si"],
    ["AA-301", "Diseño UX/UI desde Cero", "Diseño", "Básico", 40, 59, "Online en vivo", 26, "2026-08-17", "Paula Vidal", "Si"],
    ["AA-302", "Figma Profesional", "Diseño", "Intermedio", 30, 49, "A tu ritmo", 100, "2026-08-03", "Paula Vidal", "Si"],
    ["AA-303", "Ilustración Digital", "Diseño", "Básico", 35, 49, "A tu ritmo", 100, "2026-08-03", "Marco Silva", "No"],
    ["AA-304", "Diseño de Marca e Identidad", "Diseño", "Intermedio", 40, 69, "Online en vivo", 20, "2026-09-21", "Marco Silva", "Si"],
    ["AA-401", "Marketing Digital Integral", "Marketing", "Básico", 45, 59, "Online en vivo", 32, "2026-08-24", "Fernanda Cruz", "Si"],
    ["AA-402", "SEO y Posicionamiento Web", "Marketing", "Intermedio", 30, 59, "A tu ritmo", 100, "2026-08-03", "Fernanda Cruz", "Si"],
    ["AA-403", "Publicidad en Redes Sociales", "Marketing", "Intermedio", 35, 69, "Online en vivo", 27, "2026-09-01", "Javier Morales", "Si"],
    ["AA-404", "Email Marketing y Automatización", "Marketing", "Básico", 25, 39, "A tu ritmo", 100, "2026-08-03", "Javier Morales", "No"],
    ["AA-501", "Gestión de Proyectos con Metodologías Ágiles", "Negocios", "Intermedio", 40, 79, "Online en vivo", 25, "2026-09-07", "Rocío Navarro", "Si"],
    ["AA-502", "Finanzas para Emprendedores", "Negocios", "Básico", 30, 49, "Online en vivo", 30, "2026-08-31", "Rocío Navarro", "Si"],
    ["AA-503", "Excel Financiero Avanzado", "Negocios", "Avanzado", 40, 99, "Online en vivo", 16, "2026-10-12", "Rocío Navarro", "Si"],
]
columnas = ["codigo", "nombre_curso", "categoria", "nivel", "duracion_horas",
            "precio_usd", "modalidad", "cupos_disponibles", "fecha_inicio", "docente", "certificacion"]
df = pd.DataFrame(cursos, columns=columnas)
ruta_csv = os.path.join(CARPETA, "catalogo_cursos.csv")
df.to_csv(ruta_csv, index=False, encoding="utf-8")
print(f"[OK] {ruta_csv} ({len(df)} cursos)")
print("\nListo. Documentos generados en /documentos")
