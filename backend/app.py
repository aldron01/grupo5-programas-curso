import json
from functools import wraps
from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlsplit

try:
    from .config import DATA_LOCK, FRONTEND_ROOT, MAX_REQUEST_SIZE, ROLES, SECCIONES_PERMITIDAS
    from .pdf_service import construir_pdf
    from .services.historial_service import fecha_actual, registrar_historial
    from .services.programas_service import (
        aplanar_datos,
        crear_programa,
        crear_version,
    )
    from .storage import buscar_programa, buscar_version, guardar_datos, leer_datos
    from .validators import validar_datos_para_revision, validar_rol as validar_rol_datos
except ImportError:
    from config import DATA_LOCK, FRONTEND_ROOT, MAX_REQUEST_SIZE, ROLES, SECCIONES_PERMITIDAS
    from pdf_service import construir_pdf
    from services.historial_service import fecha_actual, registrar_historial
    from services.programas_service import (
        aplanar_datos,
        crear_programa,
        crear_version,
    )
    from storage import buscar_programa, buscar_version, guardar_datos, leer_datos
    from validators import validar_datos_para_revision, validar_rol as validar_rol_datos


def sincronizado(metodo):
    # Serializa cada cambio para que dos peticiones no sobrescriban el mismo JSON.
    @wraps(metodo)
    def ejecutar(*args, **kwargs):
        with DATA_LOCK:
            return metodo(*args, **kwargs)

    return ejecutar

class ProgramaHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        # El mismo servidor publica la interfaz y la API desde la carpeta frontend.
        super().__init__(*args, directory=str(FRONTEND_ROOT), **kwargs)

    def send_json(self, status, data):
        # Todas las respuestas API se codifican en UTF-8 y llevan longitud explícita.
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def leer_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))

            # Rechaza cuerpos vacíos o demasiado grandes antes de leerlos completos.
            if length <= 0 or length > MAX_REQUEST_SIZE:
                raise ValueError

            body = json.loads(self.rfile.read(length).decode("utf-8"))

            if not isinstance(body, dict):
                raise ValueError

            return body

        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Envía un objeto JSON válido.")

    def error(self, status, mensaje):
        self.send_json(status, {"error": mensaje})

    def usuario(self, body):
        usuario = body.get("usuario")
        return usuario.strip() if isinstance(usuario, str) else ""

    def validar_rol(self, body, rol_esperado):
        rol = body.get("rol")
        usuario = self.usuario(body)
        if isinstance(rol, str):
            rol = rol.strip()
        # La validación de permisos se mantiene fuera del manejador HTTP.
        codigo_error, mensaje = validar_rol_datos(
            rol,
            rol_esperado,
            usuario,
            ROLES,
        )
        if codigo_error is not None:
            self.error(codigo_error, mensaje)
            return False
        return True

    def parsear_id(self, valor, nombre):
        # Centraliza el error para que todos los endpoints respondan igual ante IDs inválidos.
        try:
            return int(valor)
        except (TypeError, ValueError):
            self.error(400, f"ID de {nombre} inválido.")
            return None

    def obtener_programa(self, data, programa_id):
        programa = buscar_programa(data, programa_id)
        if programa is None:
            self.error(404, "Programa no encontrado.")
            return None
        return programa

    def obtener_version(self, data, version_id):
        version = buscar_version(data, version_id)
        if version is None:
            self.error(404, "Versión no encontrada.")
            return None
        return version

    def do_GET(self):
        # Se descarta la query string para resolver la ruta sin parámetros.
        path = urlsplit(self.path).path.rstrip("/") or "/"

        try:
            data = leer_datos()

            # Compatibilidad con la API anterior.
            if path == "/api/programas":
                self.send_json(200, data)
                return

            # Listar programas.
            if path == "/course-programs":
                self.send_json(200, data["programas"])
                return

            # Detalle de programa y sus versiones.
            partes = path.strip("/").split("/")

            if (
                len(partes) == 2
                and partes[0] == "course-programs"
                and partes[1].isdigit()
            ):
                programa_id = self.parsear_id(partes[1], "programa")
                if programa_id is None:
                    return

                programa = self.obtener_programa(data, programa_id)
                if programa is None:
                    return

                versiones = [
                    v for v in data["versiones"]
                    if v["programa_id"] == programa["id"]
                ]

                self.send_json(200, {
                    "programa": programa,
                    "versiones": versiones,
                })
                return

            # Consultar una versión.
            if len(partes) == 2 and partes[0] == "program-versions":
                version_id = self.parsear_id(partes[1], "versión")
                if version_id is None:
                    return

                version = self.obtener_version(data, version_id)
                if version is None:
                    return

                self.send_json(200, version)
                return

            # Comparar una versión con la anterior.
            if (
                len(partes) == 3
                and partes[0] == "program-versions"
                and partes[1].isdigit()
                and partes[2] == "changes"
            ):
                version_id = self.parsear_id(partes[1], "versión")
                if version_id is None:
                    return

                version = self.obtener_version(data, version_id)
                if version is None:
                    return

                anteriores = [
                    v for v in data["versiones"]
                    if v["programa_id"] == version["programa_id"]
                    and v["numero_version"] < version["numero_version"]
                ]

                anterior = max(
                    anteriores,
                    key=lambda v: v["numero_version"],
                    default=None,
                )

                if anterior is None:
                    self.send_json(200, {
                        "version": version,
                        "version_anterior": None,
                        "cambios": [],
                    })
                    return

                # Aplanar ambas versiones permite comparar también campos anidados.
                valores_anteriores = aplanar_datos(
                    anterior.get("secciones", {}),
                    "secciones",
                )
                valores_actuales = aplanar_datos(
                    version.get("secciones", {}),
                    "secciones",
                )
                valores_anteriores["estado"] = anterior.get("estado")
                valores_actuales["estado"] = version.get("estado")

                self.send_json(200, {
                    "version": version["id"],
                    "version_anterior": anterior["id"],
                    "cambios": [
                        {
                            "campo": clave,
                            "anterior": valores_anteriores.get(clave),
                            "actual": valores_actuales.get(clave),
                        }
                        for clave in sorted(
                            set(valores_anteriores) | set(valores_actuales)
                        )
                        if valores_anteriores.get(clave) != valores_actuales.get(clave)
                    ],
                })
                return

            # Descargar el documento institucional como PDF.
            if (
                len(partes) == 3
                and partes[0] == "program-versions"
                and partes[1].isdigit()
                and partes[2] == "pdf"
            ):
                version_id = self.parsear_id(partes[1], "versión")
                if version_id is None:
                    return

                version = self.obtener_version(data, version_id)
                if version is None:
                    return

                programa = self.obtener_programa(data, version["programa_id"])
                if programa is None:
                    return

                contenido_pdf = construir_pdf(programa, version)
                nombre = f"programa-{programa['id']}-version-{version['numero_version']}.pdf"
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{nombre}"',
                )
                self.send_header("Content-Length", str(len(contenido_pdf)))
                self.end_headers()
                self.wfile.write(contenido_pdf)
                return

            # Servir frontend.
            if path.startswith("/api/") or path.startswith(
                ("/course-programs", "/program-versions")
            ):
                self.error(404, "Ruta de API no encontrada.")
                return

            if path == "/":
                self.path = "/Programa.html"

            super().do_GET()

        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.error(500, str(exc))

    @sincronizado
    def do_POST(self):
        path = urlsplit(self.path).path.rstrip("/")

        try:
            body = self.leer_body()
        except ValueError as exc:
            self.error(400, str(exc))
            return

        try:
            data = leer_datos()
            partes = path.strip("/").split("/")

            # Crear programa.
            if path == "/course-programs":
                if not self.validar_rol(body, "docente"):
                    return
                if not body.get("codigo") or not body.get("asignatura"):
                    self.error(400, "El código y la asignatura son obligatorios.")
                    return

                programa, version = crear_programa(data, body)

                registrar_historial(
                    data, version, "Creación",
                    self.usuario(body), "Se creó el programa y su versión 1."
                )

                guardar_datos(data)
                self.send_json(201, {
                    "programa": programa,
                    "version": version,
                })
                return

            # Crear o clonar versión.
            if (
                len(partes) == 3
                and partes[0] == "course-programs"
                and partes[1].isdigit()
                and partes[2] == "versions"
            ):
                programa = buscar_programa(data, int(partes[1]))

                if not programa:
                    self.error(404, "Programa no encontrado.")
                    return
                if not self.validar_rol(body, "coordinador-academico"):
                    return

                versiones = [
                    v for v in data["versiones"]
                    if v["programa_id"] == programa["id"]
                ]

                ultima_version = max(
                    versiones,
                    key=lambda v: v["numero_version"],
                    default=None,
                )
                version_vigente = next(
                    (
                        item for item in versiones
                        if item["numero_version"] == programa.get("version_actual")
                        and item.get("estado") == "vigente"
                    ),
                    None,
                )
                if version_vigente is None:
                    self.error(409, "Solo se puede crear una versión desde una versión vigente.")
                    return
                if (
                    ultima_version is not None
                    and ultima_version["id"] != version_vigente["id"]
                ):
                    self.error(
                        409,
                        "La versión más reciente debe estar autorizada antes de crear otra.",
                    )
                    return

                nueva = crear_version(
                    data,
                    programa,
                    version_vigente,
                    clonar=body.get("clonar", True),
                )

                registrar_historial(
                    data, nueva, "Creación de versión",
                    self.usuario(body),
                    f"Se creó la versión {nueva['numero_version']}."
                )

                guardar_datos(data)
                self.send_json(201, nueva)
                return

            # Acciones del flujo académico.
            if (
                len(partes) == 3
                and partes[0] == "program-versions"
                and partes[1].isdigit()
                and partes[2] in ("submit", "return", "approve", "authorize")
            ):
                version = buscar_version(data, int(partes[1]))

                if not version:
                    self.error(404, "Versión no encontrada.")
                    return

                accion = partes[2]
                estado = version.get("estado", "borrador")
                versiones_programa = [
                    item for item in data["versiones"]
                    if item["programa_id"] == version["programa_id"]
                ]
                ultima_version = max(
                    versiones_programa,
                    key=lambda item: item["numero_version"],
                    default=None,
                )
                if ultima_version is None or ultima_version["id"] != version["id"]:
                    self.error(
                        409,
                        "Solo se puede cambiar el estado de la versión más reciente.",
                    )
                    return

                # Cada acción solo permite una transición de estado y un rol determinado.
                transiciones = {
                    "submit": ("borrador", "en_revision"),
                    "return": ("en_revision", "devuelto"),
                    "approve": ("en_revision", "aprobado"),
                    "authorize": ("aprobado", "vigente"),
                }

                esperado, nuevo_estado = transiciones[accion]
                rol_requerido = {
                    "submit": "docente",
                    "return": "coordinador-academico",
                    "approve": "coordinador-academico",
                    "authorize": "decanatura",
                }[accion]
                if not self.validar_rol(body, rol_requerido):
                    return

                # Un envío puede repetirse después de corregir una versión devuelta.
                estados_esperados = (
                    ("borrador", "devuelto")
                    if accion == "submit"
                    else (esperado,)
                )

                if estado not in estados_esperados:
                    self.error(
                        409,
                        f"No se puede ejecutar {accion} desde el estado '{estado}'."
                    )
                    return

                if accion == "return":
                    observacion = body.get("observacion")
                    if not isinstance(observacion, str) or not observacion.strip():
                        self.error(400, "Debes indicar una observación no vacía.")
                        return
                if accion == "submit" and not self.usuario(body):
                    self.error(400, "Escribe el nombre del docente antes de enviar a revisión.")
                    return
                if accion == "submit":
                    faltantes = validar_datos_para_revision(version)
                    if faltantes:
                        self.error(
                            400,
                            "Completa los campos obligatorios antes de enviar: "
                            + ", ".join(faltantes),
                        )
                        return

                if accion == "return":
                    version.setdefault("observaciones", []).append({
                        "fecha": fecha_actual(),
                        "usuario": self.usuario(body),
                        "texto": observacion.strip(),
                    })

                responsables = version.setdefault("secciones", {}).setdefault(
                    "responsables",
                    {"usuario": self.usuario(body), "contenido": {}},
                )
                contenido_responsables = responsables.setdefault("contenido", {})
                campo_responsable = {
                    "submit": "docente",
                    "return": "coordinador",
                    "approve": "coordinador",
                    "authorize": "decanatura",
                }[accion]
                contenido_responsables[campo_responsable] = self.usuario(body)

                version["estado"] = nuevo_estado
                version["actualizado_en"] = fecha_actual()

                programa = buscar_programa(data, version["programa_id"])

                if programa:
                    programa["estado"] = nuevo_estado

                # Al autorizar una versión nueva, la anterior deja de estar vigente.
                if accion == "authorize" and programa:
                    for anterior in data["versiones"]:
                        if (
                            anterior["programa_id"] == programa["id"]
                            and anterior["id"] != version["id"]
                            and anterior.get("estado") == "vigente"
                        ):
                            anterior["estado"] = "reemplazado"
                    programa["version_actual"] = version["numero_version"]

                registrar_historial(
                    data,
                    version,
                    accion.capitalize(),
                    self.usuario(body),
                    body.get("observacion", f"Estado actualizado a {nuevo_estado}."),
                )

                guardar_datos(data)
                self.send_json(200, {
                    "ok": True,
                    "version": version,
                    "programa": programa,
                })
                return

            self.error(404, "Ruta de API no encontrada.")

        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.error(500, str(exc))

    @sincronizado
    def do_PUT(self):
        path = urlsplit(self.path).path.rstrip("/")

        try:
            body = self.leer_body()
        except ValueError as exc:
            self.error(400, str(exc))
            return

        try:
            data = leer_datos()

            # Compatibilidad con la API anterior.
            if path == "/api/programas":
                self.error(
                    410,
                    "La actualización completa fue retirada; usa las rutas de programas y versiones.",
                )
                return

            partes = path.strip("/").split("/")

            # Guardar una sección específica evita reemplazar datos de otras secciones.
            if (
                len(partes) == 4
                and partes[0] == "program-versions"
                and partes[1].isdigit()
                and partes[2] == "sections"
            ):
                if partes[3] not in SECCIONES_PERMITIDAS:
                    self.error(404, "Sección de programa no reconocida.")
                    return
                version_id = self.parsear_id(partes[1], "versión")
                if version_id is None:
                    return

                version = self.obtener_version(data, version_id)
                if version is None:
                    return

                if not self.validar_rol(body, "docente"):
                    return
                if not isinstance(body.get("contenido"), dict):
                    self.error(400, "El contenido de la sección debe ser un objeto.")
                    return
                if version.get("estado") not in ("borrador", "devuelto"):
                    self.error(409, "Solo se puede editar un borrador o una versión devuelta.")
                    return

                # Actualiza también la ficha general para mantener sincronizadas las vistas.
                version.setdefault("secciones", {})[partes[3]] = body
                version["actualizado_en"] = fecha_actual()
                version.setdefault("secciones", {}).setdefault(
                    "responsables", {"usuario": self.usuario(body), "contenido": {}}
                ).setdefault("contenido", {})["docente"] = self.usuario(body)
                if partes[3] == "general":
                    programa = buscar_programa(data, version["programa_id"])
                    equivalencias = {
                        "programa": "programa_academico",
                        "ciclo": "ciclo_academico",
                        "anio": "anio",
                        "nivel": "nivel_academico",
                        "horas": "horas_semanales",
                    }
                    for campo, valor_campo in body["contenido"].items():
                        if campo in {
                            "codigo",
                            "asignatura",
                            "departamento",
                            "facultad",
                            "modalidad",
                            "creditos",
                            "sede",
                        }:
                            programa[campo] = valor_campo
                        elif campo in equivalencias:
                            programa[equivalencias[campo]] = valor_campo
                elif partes[3] == "responsables":
                    programa = buscar_programa(data, version["programa_id"])
                    docente = body["contenido"].get("docente")
                    if docente is not None:
                        programa["profesor"] = docente

                registrar_historial(
                    data, version, "Guardado de sección",
                    self.usuario(body),
                    f"Se guardó la sección '{partes[3]}'."
                )

                guardar_datos(data)
                self.send_json(200, {"ok": True, "version": version})
                return

            # Guardar una versión completa.
            if len(partes) == 2 and partes[0] == "program-versions":
                version_id = self.parsear_id(partes[1], "versión")
                if version_id is None:
                    return

                version = self.obtener_version(data, version_id)
                if version is None:
                    return

                if not self.validar_rol(body, "docente"):
                    return
                if version.get("estado") not in ("borrador", "devuelto"):
                    self.error(409, "La versión ya no se puede editar.")
                    return

                # El cliente no puede cambiar identidad ni estado al guardar el contenido.
                campos_protegidos = {
                    "id", "programa_id", "numero_version", "estado"
                }

                for clave, valor in body.items():
                    if clave not in campos_protegidos:
                        version[clave] = valor

                version["actualizado_en"] = fecha_actual()

                registrar_historial(
                    data, version, "Guardado",
                    self.usuario(body), "Se guardaron los datos de la versión."
                )

                guardar_datos(data)
                self.send_json(200, {"ok": True, "version": version})
                return

            self.error(404, "Ruta de API no encontrada.")

        except (OSError, json.JSONDecodeError, ValueError) as exc:
            self.error(500, str(exc))
