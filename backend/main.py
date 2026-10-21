"""Punto de entrada para iniciar el servidor del backend."""

from http.server import ThreadingHTTPServer

# Permite arrancar el servidor tanto como módulo como desde la carpeta backend.
if __package__:
    from .app import ProgramaHandler
    from .config import SERVER_HOST, SERVER_PORT
else:
    from app import ProgramaHandler
    from config import SERVER_HOST, SERVER_PORT


def main():
    # ThreadingHTTPServer puede atender varias solicitudes al mismo tiempo.
    servidor = ThreadingHTTPServer((SERVER_HOST, SERVER_PORT), ProgramaHandler)
    print(f"Aplicación disponible en http://{SERVER_HOST}:{SERVER_PORT}")
    try:
        # Mantiene el proceso activo y esperando solicitudes HTTP.
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        # Libera el socket incluso si el servidor se detiene con Ctrl+C.
        servidor.server_close()


# Ejecuta el servidor solo cuando este archivo se inicia directamente.
if __name__ == "__main__":
    main()
