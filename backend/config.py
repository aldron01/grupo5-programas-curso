from pathlib import Path
import threading

# Las rutas se calculan desde este módulo para que no dependan del directorio actual.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DATA_FILE = PROJECT_ROOT / "programas.json"

# Limita el tamaño del JSON recibido por cada petición.
MAX_REQUEST_SIZE = 1_000_000
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

# El mismo bloqueo protege las operaciones concurrentes sobre el archivo de datos.
ROLES = {"docente", "coordinador-academico", "decanatura"}
DATA_LOCK = threading.RLock()

# Solo estas secciones pueden modificarse mediante la ruta de guardado por sección.
SECCIONES_PERMITIDAS = {
    "responsables",
    "general",
    "prerrequisitos",
    "descripcion",
    "competencias",
    "perfil",
    "metodologia",
    "contenidos",
    "bibliografia",
    "evaluacion",
}
