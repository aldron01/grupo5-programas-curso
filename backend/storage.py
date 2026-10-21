import json
import os
import tempfile
from pathlib import Path

try:
    from .config import DATA_FILE, DATA_LOCK, PROJECT_ROOT
except ImportError:
    from config import DATA_FILE, DATA_LOCK, PROJECT_ROOT


def leer_datos():
    # Evita leer el archivo mientras otra petición está guardando cambios.
    with DATA_LOCK:
        with DATA_FILE.open(encoding="utf-8") as archivo:
            data = json.load(archivo)

        # Comprueba la estructura mínima antes de que la usen las rutas.
        for clave in ("programas", "versiones", "historial"):
            if not isinstance(data.get(clave), list):
                raise ValueError(f"Falta la lista '{clave}' en programas.json")

        return data


def guardar_datos(data):
    with DATA_LOCK:
        temporal = None
        try:
            # Se escribe primero en un temporal para no dejar JSON incompleto.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=PROJECT_ROOT,
                prefix=".programas-",
                suffix=".tmp",
                delete=False,
            ) as archivo:
                temporal = Path(archivo.name)
                json.dump(data, archivo, ensure_ascii=False, indent=2)
                archivo.write("\n")

            # Reemplazo atómico: el archivo visible queda completo en todo momento.
            os.replace(temporal, DATA_FILE)
        except OSError:
            # Si falla la escritura, elimina el temporal y conserva el error original.
            if temporal:
                temporal.unlink(missing_ok=True)
            raise


def buscar_programa(data, programa_id):
    # El identificador estable permite enlazar versiones con su programa.
    return next((p for p in data["programas"] if p["id"] == programa_id), None)


def buscar_version(data, version_id):
    # Devuelve None cuando el ID ya no existe o nunca fue registrado.
    return next((v for v in data["versiones"] if v["id"] == version_id), None)