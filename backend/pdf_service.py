import json
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

try:
    from .services.programas_service import aplanar_datos
except ImportError:
    from services.programas_service import aplanar_datos

def construir_pdf(programa, version):
    # ReportLab construye el documento en memoria para devolverlo como descarga HTTP.
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"Programa de curso - {programa.get('asignatura', '')}",
        author="Universidad Da Vinci de Guatemala",
    )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="TituloInstitucional",
        parent=estilos["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#001D4A"),
        fontSize=15,
        leading=19,
        spaceAfter=5 * mm,
    ))
    estilos.add(ParagraphStyle(
        name="SeccionPrograma",
        parent=estilos["Heading2"],
        textColor=colors.HexColor("#001D4A"),
        fontSize=11,
        leading=14,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    ))
    estilos.add(ParagraphStyle(
        name="TextoPrograma",
        parent=estilos["BodyText"],
        fontSize=9,
        leading=12,
    ))

    def texto(valor):
        # Escapa el texto para que caracteres del usuario no se interpreten como markup.
        if isinstance(valor, (dict, list)):
            return json.dumps(valor, ensure_ascii=False)
        return escape(str(valor if valor is not None else ""))

    general = (
        version.get("secciones", {})
        .get("general", {})
        .get("contenido", {})
    )
    programa_pdf = dict(programa)
    # Las etiquetas del formulario usan nombres distintos a los de la ficha del programa.
    equivalencias = {
        "programa": "programa_academico",
        "ciclo": "ciclo_academico",
        "anio": "anio",
        "nivel": "nivel_academico",
        "horas": "horas_semanales",
    }
    for campo, valor_general in general.items():
        programa_pdf[equivalencias.get(campo, campo)] = valor_general

    historia = [
        Paragraph("UNIVERSIDAD DA VINCI DE GUATEMALA", estilos["TituloInstitucional"]),
        Paragraph("PROGRAMA DE CURSO", estilos["Heading1"]),
        Spacer(1, 3 * mm),
    ]
    resumen = [
        ["Asignatura", texto(programa_pdf.get("asignatura"))],
        ["Código", texto(programa_pdf.get("codigo"))],
        ["Programa académico", texto(programa_pdf.get("programa_academico"))],
        ["Versión", texto(version.get("numero_version"))],
        ["Estado", texto(version.get("estado", "")).replace("_", " ").upper()],
        ["Departamento", texto(programa_pdf.get("departamento"))],
        ["Facultad", texto(programa_pdf.get("facultad"))],
        ["Ciclo", texto(programa_pdf.get("ciclo_academico"))],
        ["Año", texto(programa_pdf.get("anio"))],
        ["Nivel", texto(programa_pdf.get("nivel_academico"))],
        ["Modalidad", texto(programa_pdf.get("modalidad"))],
        ["Créditos", texto(programa_pdf.get("creditos"))],
        ["Horas", texto(programa_pdf.get("horas_semanales"))],
        ["Sede", texto(programa_pdf.get("sede"))],
    ]
    tabla_resumen = Table(resumen, colWidths=[35 * mm, 130 * mm])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E7EDF7")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#001D4A")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    historia.append(tabla_resumen)

    # Cada sección con contenido se presenta como una tabla independiente.
    for seccion, datos in version.get("secciones", {}).items():
        contenido = datos.get("contenido", {}) if isinstance(datos, dict) else {}
        if not contenido:
            continue

        historia.extend([
            Paragraph(seccion.replace("_", " ").title(), estilos["SeccionPrograma"]),
        ])
        filas = []
        for clave, valor in aplanar_datos(contenido).items():
            filas.append([
                Paragraph(clave.replace("_", " ").title(), estilos["TextoPrograma"]),
                Paragraph(texto(valor).replace("\n", "<br/>"), estilos["TextoPrograma"]),
            ])
        tabla = Table(filas, colWidths=[45 * mm, 120 * mm], repeatRows=0)
        tabla.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#A0A0A0")),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F6F8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        historia.append(tabla)

    documento.build(historia)
    return buffer.getvalue()