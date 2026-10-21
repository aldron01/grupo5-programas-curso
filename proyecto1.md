# Memoria del proyecto — Grupo 5

## Identificación

- **Proyecto:** gestión de programas de curso, versiones y PDF.
- **Curso:** Programación Web.
- **Universidad:** Universidad Da Vinci de Guatemala.
- **Repositorio:** https://github.com/aldron01/grupo5-programas-curso

El proyecto es una aplicación web para consultar y editar un programa de curso,
guardar sus secciones, administrar versiones y seguir un flujo de revisión,
aprobación y autorización.

## Estructura comprobada

```text
Proyecto/
├── backend/
│   ├── main.py
│   ├── app.py
│   ├── config.py
│   ├── storage.py
│   ├── validators.py
│   ├── pdf_service.py
│   ├── requirements.txt
│   └── services/
│       ├── __init__.py
│       ├── historial_service.py
│       └── programas_service.py
├── frontend/
│   ├── Programa.html
│   ├── script.js
│   └── estilos/
│       └── style.css
├── programas.json
├── Flujo.md
└── proyecto1.md
```

`backend/main.py` es el punto de entrada. La carpeta `backend` no necesita un
`__init__.py`: Python permite importarla como paquete de espacio de nombres.
`backend/services/__init__.py` sí existe para el paquete de servicios.

## Tecnologías y almacenamiento

- HTML, CSS y JavaScript para la interfaz.
- Python y `http.server` para servir el frontend y la API.
- ReportLab para generar el PDF (`backend/requirements.txt`).
- `programas.json` como almacenamiento local: contiene las listas
  `programas`, `versiones` e `historial`.

No hay una base de datos configurada. El guardado JSON usa un archivo temporal
y reemplazo atómico; un bloqueo compartido coordina las operaciones de
escritura dentro del proceso del servidor.

## Responsabilidades del backend

- `main.py`: configura y ejecuta `ThreadingHTTPServer`.
- `app.py`: sirve `frontend/Programa.html` y maneja los endpoints HTTP.
- `config.py`: contiene rutas, host, puerto, límite del cuerpo, roles, bloqueo
  y nombres de secciones editables.
- `storage.py`: lee y guarda el JSON y busca programas/versiones.
- `validators.py`: comprueba los campos obligatorios para revisión y el rol
  declarado en la solicitud.
- `services/programas_service.py`: crea programas y versiones, calcula IDs y
  aplana estructuras para comparar versiones.
- `services/historial_service.py`: registra fecha y eventos del workflow.
- `pdf_service.py`: crea el documento PDF a partir de una versión guardada.

## Interfaz actual

La interfaz está en `frontend/Programa.html`; su comportamiento está en
`frontend/script.js` y los estilos en `frontend/estilos/style.css`.
El formulario incluye responsables, información general, prerrequisitos,
descripción, competencias, perfil de egreso, metodología, contenidos,
bibliografía y evaluación.

El JavaScript carga actualmente el programa de ID `1`; no proporciona una
pantalla de selección o creación de programas, aunque la API sí contiene una
ruta para crear uno. Los prerrequisitos se representan como lista de
asignaturas, pero el HTML actual no tiene controles para agregar, eliminar o
reordenar sus filas.

La aplicación presenta dos formas de documento:

- «Vista previa PDF» construye en el navegador una copia imprimible del
  formulario visible.
- «Descargar PDF» solicita el documento generado por el backend para los datos
  guardados de la versión seleccionada.

Si hay cambios sin guardar, primero se debe guardar para que aparezcan en el
PDF del backend.

## Flujo y roles

```text
borrador → en_revision → aprobado → vigente
              │                         │
              └→ devuelto → en_revision └→ nueva versión en borrador
```

- **Docente:** puede editar secciones en estado `borrador` o `devuelto`,
  guardar y enviar a revisión.
- **Coordinación académica:** puede devolver una versión en revisión con una
  observación, aprobarla y crear otra versión cuando la vigente es la más
  reciente.
- **Decanatura:** puede autorizar una versión aprobada.
- Al autorizar una versión, cualquier otra versión vigente del programa pasa a
  `reemplazado`; no se elimina el historial.
- Las acciones del workflow solo se aplican a la versión más reciente.
- Para el envío a revisión se requieren código, asignatura, programa académico,
  facultad, ciclo, año y nombre del docente.

El selector de rol solo simula los perfiles para una demostración. El backend
valida el rol recibido, pero no autentica a la persona ni evita que un cliente
falsifique ese valor. No es un mecanismo de seguridad apto para producción.

## API implementada

### Programas

- `GET /course-programs`: lista los programas.
- `POST /course-programs`: crea un programa y su primera versión en borrador.
- `GET /course-programs/{id}`: devuelve un programa y sus versiones.
- `GET /api/programas`: lectura de compatibilidad con la API anterior.
- `PUT /api/programas`: retirado; devuelve `410`.

### Versiones y secciones

- `GET /program-versions/{id}`: devuelve una versión.
- `PUT /program-versions/{id}`: guarda una versión completa sin permitir
  cambiar sus campos protegidos.
- `PUT /program-versions/{id}/sections/{section}`: guarda una sección
  permitida.
- `POST /course-programs/{id}/versions`: crea una versión en borrador desde la
  versión vigente; permite clonar sus secciones.
- `GET /program-versions/{id}/changes`: compara la versión con la versión
  anterior.

### Workflow y documento

- `POST /program-versions/{id}/submit`: envía una versión a revisión.
- `POST /program-versions/{id}/return`: devuelve con observación.
- `POST /program-versions/{id}/approve`: aprueba.
- `POST /program-versions/{id}/authorize`: autoriza y marca vigente.
- `GET /program-versions/{id}/pdf`: genera el PDF descargable.

## Datos actuales

En la copia de trabajo revisada hay un programa de ejemplo con ID `1` y cuatro
versiones. Las versiones 1 y 2 figuran como `reemplazado`, la 3 como `vigente`
y la 4 como `borrador`. El programa apunta a la versión actual 3. Los datos
pueden cambiar al probar la aplicación porque las acciones se persisten en
`programas.json`.

## Ejecutar localmente

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python backend/main.py
```

Luego abre `http://127.0.0.1:8000/`. También se puede arrancar desde la raíz con
`.venv/bin/python -m backend.main`. Reinicia el servidor después de modificar
el backend.

## Pendiente / límites conocidos

- Implementar autenticación real y asociar permisos a usuarios autenticados.
- Añadir a la interfaz la selección y creación de programas si se requiere
  administrar más de un programa desde el navegador.
- Añadir controles para administrar dinámicamente las filas de prerrequisitos
  si lo exige el formulario.
- Contrastar las secciones y el PDF con el formulario institucional original.
  No hay una copia de `Formulario.pdf` en la estructura revisada.
- Añadir pruebas automatizadas para endpoints y transiciones del workflow.
- Evaluar una base de datos si los requisitos de despliegue o concurrencia
  superan el alcance del almacenamiento JSON local.

## Criterios para cambios futuros

- Leer el código actual antes de modificarlo y mantener frontend, API y
  almacenamiento compatibles.
- No documentar como implementada una función que solo muestre mensajes o
  controles sin completar la operación.
- Conservar las versiones y el historial; no actualizar una versión autorizada
  en lugar de crear otra.
- Usar comentarios breves para explicar intención o reglas no obvias.
- Verificar las rutas, la persistencia y los errores reales tras los cambios.
