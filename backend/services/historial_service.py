from datetime import datetime

try:
    from ..storage import buscar_programa, buscar_version
except ImportError:
    from storage import buscar_programa, buscar_version


def fecha_actual():
    # Conserva la zona horaria para que los eventos se puedan ordenar correctamente.
    return datetime.now().astimezone().isoformat(timespec="seconds")


def registrar_historial(data, version, accion, usuario, descripcion):
    # Cada evento guarda referencias a programa y versión para facilitar consultas.
    data["historial"].append({
        "fecha": fecha_actual(),
        "accion": accion,
        "usuario": usuario,
        "descripcion": descripcion,
        "programa_id": version.get("programa_id"),
        "version_id": version.get("id"),
    })


__all__ = [
    "buscar_programa",
    "buscar_version",
    "fecha_actual",
    "registrar_historial",
]
