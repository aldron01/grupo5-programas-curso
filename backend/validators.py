"""Validaciones de entrada y de estado del programa académico."""

from collections.abc import Collection, Mapping
from typing import TypeAlias

ResultadoRol: TypeAlias = tuple[int | None, str | None]

CAMPOS_OBLIGATORIOS = (
    ("codigo", "Código"),
    ("asignatura", "Asignatura"),
    ("programa", "Programa académico"),
    ("facultad", "Facultad"),
    ("ciclo", "Ciclo"),
    ("anio", "Año"),
)


def _contenido_seccion(
    secciones: Mapping[str, object],
    nombre: str,
) -> Mapping[str, object]:
    # Un contenido malformado se trata como vacío para informar los campos faltantes.
    seccion = secciones.get(nombre)
    if not isinstance(seccion, Mapping):
        return {}

    contenido = seccion.get("contenido")
    return contenido if isinstance(contenido, Mapping) else {}


def _tiene_valor(valor: object) -> bool:
    if isinstance(valor, str):
        return bool(valor.strip())
    if isinstance(valor, bool):
        # bool hereda de int en Python, pero True/False no cuentan como campos numéricos.
        return False
    return isinstance(valor, (int, float))


def validar_datos_para_revision(version: object) -> list[str]:
    """Devuelve las etiquetas de campos requeridos que están vacíos o malformados."""
    if not isinstance(version, Mapping):
        return [etiqueta for _, etiqueta in CAMPOS_OBLIGATORIOS] + ["Docente"]

    secciones = version.get("secciones")
    if not isinstance(secciones, Mapping):
        secciones = {}

    general = _contenido_seccion(secciones, "general")
    responsables = _contenido_seccion(secciones, "responsables")

    # El envío a revisión requiere los datos generales y el nombre del docente.
    faltantes = [
        etiqueta
        for campo, etiqueta in CAMPOS_OBLIGATORIOS
        if not _tiene_valor(general.get(campo))
    ]
    if not _tiene_valor(responsables.get("docente")):
        faltantes.append("Docente")

    return faltantes


def validar_rol(
    rol: object,
    rol_esperado: str,
    usuario: object,
    roles_permitidos: Collection[str],
) -> ResultadoRol:
    """Devuelve (código HTTP, mensaje); ambos son None cuando el rol es válido."""
    if (
        not isinstance(rol, str)
        or rol not in roles_permitidos
        or rol != rol_esperado
    ):
        return 403, "El rol no tiene permiso para realizar esta acción."

    if not isinstance(usuario, str) or not usuario.strip():
        return 400, "Debes indicar el nombre de la persona responsable."

    return None, None
