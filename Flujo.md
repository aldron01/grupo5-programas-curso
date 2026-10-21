# Flujo del sistema

## Componentes

- `frontend/Programa.html` contiene el formulario y los controles.
- `frontend/script.js` carga y guarda los datos, y presenta las acciones según
  el rol y el estado seleccionados.
- `frontend/estilos/style.css` contiene los estilos del formulario y de la
  impresión.
- `backend/main.py` inicia el servidor.
- `backend/app.py` sirve el frontend y maneja las rutas HTTP de la API.
- `backend/config.py` centraliza las rutas, roles, secciones permitidas y
  configuración del servidor.
- `backend/storage.py` lee y guarda `programas.json`.
- `backend/validators.py` valida los datos obligatorios y el rol declarado.
- `backend/services/programas_service.py` contiene operaciones de programas y
  versiones.
- `backend/services/historial_service.py` registra fecha y eventos.
- `backend/pdf_service.py` genera el PDF descargable.
- `programas.json` almacena las colecciones `programas`, `versiones` e
  `historial`.

## Inicio

Desde la raíz del proyecto, instala la dependencia del PDF y ejecuta el servidor:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python backend/main.py
```

Abre `http://127.0.0.1:8000/`. La ruta raíz sirve `frontend/Programa.html`.
También se puede iniciar desde la raíz con `.venv/bin/python -m backend.main`.

El frontend usa actualmente el programa con ID `1`. El selector de rol permite
probar las acciones como Docente, Coordinación académica o Decanatura; no es un
sistema de inicio de sesión. El backend valida el rol que recibe, pero un cliente
puede falsificarlo. No debe considerarse autenticación ni control de acceso
seguro para producción.

## Flujo de una versión

```text
BORRADOR ── Docente envía ──> EN REVISIÓN
                                  ├── Coordinación devuelve ──> DEVUELTO
                                  │                                │
                                  │         Docente corrige y reenvía
                                  │                                └──> EN REVISIÓN
                                  └── Coordinación aprueba ──> APROBADO
                                                                  │
                                                Decanatura autoriza
                                                                  v
                                                               VIGENTE
                                                                  │
                                     Coordinación crea otra versión
                                                                  v
                                         NUEVA VERSIÓN: BORRADOR
```

- El Docente puede editar y guardar cuando la versión está en `borrador` o
  `devuelto`.
- Para enviar a revisión se requieren los campos de información general
  obligatorios y el nombre del docente.
- Coordinación académica puede devolver una versión en revisión; la devolución
  exige una observación. También puede aprobarla.
- Decanatura solo puede autorizar una versión aprobada.
- Las acciones del flujo solo se permiten en la versión más reciente del
  programa.
- Crear una versión requiere que la versión vigente sea la más reciente. La
  versión nueva se crea como borrador y, por defecto, clona las secciones
  vigentes; se limpian los nombres de Coordinación y Decanatura.
- Al autorizar una versión, cualquier otra versión vigente del programa pasa a
  `reemplazado`. Las versiones anteriores permanecen en el historial.

## Guardado y datos

- «Guardar borrador» envía cada sección mediante una petición independiente y
  vuelve a cargar la versión confirmada por el servidor.
- «Cancelar cambios» descarta los cambios no guardados recargando la versión
  desde el servidor.
- El backend serializa las operaciones de escritura, verifica la estructura
  básica del JSON y reemplaza el archivo de datos mediante un temporal.
- `PUT /program-versions/{id}` guarda una versión completa, excepto los campos
  protegidos de identidad y estado.
- `PUT /api/programas` responde `410`; el guardado debe hacerse mediante las
  rutas de versiones y secciones.

## Endpoints implementados

| Método | Ruta | Función |
| --- | --- | --- |
| `GET` | `/api/programas` | Lectura de compatibilidad con la API anterior. |
| `GET` | `/course-programs` | Lista programas. |
| `POST` | `/course-programs` | Crea un programa y su primera versión en borrador. |
| `GET` | `/course-programs/{id}` | Consulta un programa y sus versiones. |
| `POST` | `/course-programs/{id}/versions` | Crea una versión desde la versión vigente. |
| `GET` | `/program-versions/{id}` | Consulta una versión. |
| `PUT` | `/program-versions/{id}` | Guarda una versión completa. |
| `PUT` | `/program-versions/{id}/sections/{section}` | Guarda una sección permitida. |
| `GET` | `/program-versions/{id}/changes` | Compara la versión con la anterior. |
| `POST` | `/program-versions/{id}/submit` | Envía a revisión. |
| `POST` | `/program-versions/{id}/return` | Devuelve con observación. |
| `POST` | `/program-versions/{id}/approve` | Aprueba la versión. |
| `POST` | `/program-versions/{id}/authorize` | Autoriza y marca vigente. |
| `GET` | `/program-versions/{id}/pdf` | Genera y descarga el PDF del backend. |

Las solicitudes de escritura reciben JSON con los datos de la operación y,
cuando corresponde, `usuario` y `rol`.

## Vista previa y PDF

- «Vista previa PDF» crea en el navegador una representación imprimible del
  formulario que está en pantalla.
- «Descargar PDF» solicita el PDF generado por el backend para la versión
  guardada. Guarda los cambios antes de descargar si se quiere incluir la
  información más reciente.
- La vista previa del navegador no es el mismo archivo que genera
  `backend/pdf_service.py`.

## Alcance actual

- El frontend está conectado al programa de ID `1`; aunque el backend tiene una
  ruta para crear programas, la interfaz no tiene un flujo para hacerlo.
- Las filas de prerrequisitos se cargan y guardan como una lista, pero el
  formulario actual no ofrece controles para agregar, eliminar o reordenar
  filas.
- El selector de rol es de demostración; no existe autenticación de usuarios.
- Los datos se guardan en JSON; no hay una base de datos configurada.
- El diseño debe contrastarse con el formulario institucional original antes de
  dar por verificada su equivalencia.

Si el servidor ya estaba activo antes de cambiar el código, reinícialo para
cargar los cambios.
