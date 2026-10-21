"""Lógica de negocio para programas y versiones."""

import json

try:
    from .historial_service import fecha_actual
except ImportError:
    from historial_service import fecha_actual


def siguiente_id(items):
    # Usa el mayor ID existente para evitar colisiones tras borrar registros.
    return max((item["id"] for item in items), default=0) + 1


def aplanar_datos(valor, prefijo=""):
    # Convierte estructuras anidadas en rutas comparables, por ejemplo seccion.campo.
    if isinstance(valor, dict):
        resultado = {}
        for clave, contenido in valor.items():
            ruta = f"{prefijo}.{clave}" if prefijo else clave
            resultado.update(aplanar_datos(contenido, ruta))
        return resultado

    if isinstance(valor, list):
        resultado = {}
        for indice, contenido in enumerate(valor):
            ruta = f"{prefijo}[{indice}]"
            resultado.update(aplanar_datos(contenido, ruta))
        return resultado

    return {prefijo: valor} if prefijo else {}


def crear_programa(data, body):
    # Los datos de autenticación no forman parte de la ficha académica.
    programa = {clave: valor for clave, valor in body.items() if clave not in ("rol", "usuario")}
    programa["id"] = siguiente_id(data["programas"])
    programa["version_actual"] = None
    programa["estado"] = "borrador"
    data["programas"].append(programa)

    # Todo programa comienza con una primera versión editable en borrador.
    version = {
        "id": siguiente_id(data["versiones"]),
        "programa_id": programa["id"],
        "numero_version": 1,
        "estado": "borrador",
        "secciones": {},
        "observaciones": [],
        "creado_en": fecha_actual(),
        "actualizado_en": fecha_actual(),
    }
    data["versiones"].append(version)
    return programa, version


def crear_version(data, programa, version_vigente, clonar=True):
    versiones = [
        version for version in data["versiones"]
        if version["programa_id"] == programa["id"]
    ]
    ultima_version = max(
        versiones,
        key=lambda version: version["numero_version"],
        default=None,
    )
    # Copia las secciones para que editar la nueva versión no altere la vigente.
    secciones = (
        json.loads(json.dumps(version_vigente.get("secciones", {})))
        if clonar else {}
    )
    responsables = secciones.get("responsables")
    if isinstance(responsables, dict):
        # Las nuevas aprobaciones deben ser asignadas de nuevo en cada versión.
        contenido = responsables.setdefault("contenido", {})
        contenido["coordinador"] = ""
        contenido["decanatura"] = ""

    nueva = {
        "id": siguiente_id(data["versiones"]),
        "programa_id": programa["id"],
        "numero_version": (
            ultima_version["numero_version"] + 1 if ultima_version else 1
        ),
        "estado": "borrador",
        "secciones": secciones,
        "observaciones": [],
        "creado_en": fecha_actual(),
        "actualizado_en": fecha_actual(),
    }
    data["versiones"].append(nueva)
    programa["estado"] = "borrador"
    return nueva
