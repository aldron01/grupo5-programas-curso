# Descripción General — Gestión de Programas

El sistema controla el ciclo de vida de los programas académicos, desde su creación como borrador hasta su autorización final.

## Componentes
- **Módulo `g5_programas`**: Contiene las rutas FastAPI, la lógica de negocio, la persistencia y el control de acceso basado en roles (Autor, Coordinador, etc.).
- **Servicio de PDF**: Genera el documento institucional en memoria usando `ReportLab` para versiones autorizadas.
- **Frontend**: Interfaz web para la gestión de contenidos.

La seguridad se integra con el middleware de G2 para validar la identidad y roles del usuario. La aplicación común debe registrar `g5_programas.router` y sus manejadores de errores.

El proyecto no mantiene un backend local ni un punto de entrada `main.py`; el módulo se integra en la aplicación compartida.
