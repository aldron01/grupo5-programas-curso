import json
import os
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


# Ubicación principal del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Carpeta donde están los archivos del frontend
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

# Archivo donde se guardan los datos
DATA_FILE = PROJECT_ROOT / "programas.json"

# Tamaño máximo permitido para enviar datos
MAX_REQUEST_SIZE = 1_000_000


class ProgramaHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # Indica que los archivos HTML, CSS y JS están en frontend
        super().__init__(*args, directory=str(FRONTEND_ROOT), **kwargs)

    def send_json(self, status, data):
        # Convierte los datos a formato JSON para enviarlos al navegador
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        # Obtiene la ruta que está solicitando el navegador
        path = urlsplit(self.path).path

        # Devuelve la información de programas.json
        if path == "/api/programas":
            try:
                with DATA_FILE.open(encoding="utf-8") as data_file:
                    data = json.load(data_file)

            except (OSError, json.JSONDecodeError) as error:
                self.send_json(
                    500,
                    {"error": f"No se pudo leer programas.json: {error}"}
                )
                return

            self.send_json(200, data)
            return

        # Si se solicita una API que no existe
        if path.startswith("/api/"):
            self.send_json(
                404,
                {"error": "Ruta de API no encontrada."}
            )
            return

        # Al entrar a la página principal se carga Demo.html
        if path == "/":
            self.path = "/Demo.html"

        # Muestra los archivos del frontend
        super().do_GET()

    def do_PUT(self):
        # Verifica que se esté actualizando la ruta correcta
        if urlsplit(self.path).path != "/api/programas":
            self.send_json(
                404,
                {"error": "Ruta de API no encontrada."}
            )
            return

        try:
            # Obtiene el tamaño de los datos enviados
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            if content_length <= 0 or content_length > MAX_REQUEST_SIZE:
                raise ValueError

            # Lee el JSON enviado por el frontend
            data = json.loads(
                self.rfile.read(content_length)
            )

        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(
                400,
                {"error": "La solicitud debe contener JSON válido."}
            )
            return

        # Verifica que el JSON tenga las partes necesarias
        if (
            not isinstance(data, dict)
            or not isinstance(data.get("programas"), list)
            or not isinstance(data.get("versiones"), list)
            or not isinstance(data.get("historial"), list)
        ):
            self.send_json(
                400,
                {"error": "El JSON debe incluir programas, versiones e historial."}
            )
            return

        temp_path = None

        try:
            # Primero crea un archivo temporal para guardar los cambios
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=PROJECT_ROOT,
                prefix=".programas-",
                suffix=".tmp",
                delete=False,
            ) as temp_file:

                temp_path = Path(temp_file.name)

                json.dump(
                    data,
                    temp_file,
                    ensure_ascii=False,
                    indent=2
                )

                temp_file.write("\n")

            # Reemplaza el archivo anterior por el nuevo
            os.replace(temp_path, DATA_FILE)

        except OSError as error:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

            self.send_json(
                500,
                {"error": f"No se pudo guardar programas.json: {error}"}
            )
            return

        # Informa que los cambios se guardaron correctamente
        self.send_json(200, {"ok": True})


if __name__ == "__main__":
    # Inicia el servidor local en el puerto 8000
    server = ThreadingHTTPServer(
        ("127.0.0.1", 8000),
        ProgramaHandler
    )

    print("Aplicación disponible en http://127.0.0.1:8000")

    try:
        # Mantiene el servidor funcionando
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServidor detenido.")

    finally:
        # Cierra el servidor correctamente
        server.server_close()