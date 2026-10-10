# MEMORIA PRINCIPAL — PROYECTO F1, GRUPO 5

## 1. Identificación del proyecto

**Nombre:** Grupo 5 — Programas de curso, versiones y PDF.

**Curso:** Programación Web.

**Universidad:** Universidad Da Vinci de Guatemala (UDV).

**Tipo:** Proyecto integrador de API REST y workflow docente.

**Repositorio de GitHub:** https://github.com/aldron01/grupo5-programas-curso.git

La finalidad es desarrollar un sistema web que permita gestionar programas académicos de cursos mediante formularios por secciones, borradores, versiones, revisión, aprobación, autorización y generación de PDF institucional.

La prioridad es cumplir todos los requisitos del proyecto académico, no solamente crear una página que se vea bien o que guarde información.

## 2. Objetivo general

Construir una aplicación web funcional que permita crear y administrar programas de curso, guardar avances, crear nuevas versiones, revisar cambios, controlar el flujo de autorización y generar documentos PDF institucionales.

El sistema debe mantener el historial de versiones y garantizar que solamente exista una versión autorizada y vigente por cada programa de curso.

## 3. Tecnologías del proyecto

- HTML para la estructura del frontend.
- CSS para los estilos.
- JavaScript para las interacciones y comunicación con el backend.
- Python para el servidor y la API REST.
- `programas.json` como almacenamiento actual de datos.
- Git y GitHub para controlar las versiones del código.
- PDF para la generación del documento institucional.

El almacenamiento actual en JSON es la implementación inicial. Si los requisitos académicos exigen una base de datos, se deberá incorporar sin perder las funcionalidades existentes.

## 4. Estructura actual del proyecto

```text
Proyecto/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── Demo.html
│   ├── estilos/
│   │   └── style.css
│   └── script.js
├── programas.json
├── Formulario.pdf
├── Flujo.md
└── .gitignore
```

Esta es la estructura que el usuario tiene actualmente según la terminal. Puede haber cambios posteriores.

No asumir que existen carpetas, archivos, funciones o módulos que no se hayan comprobado.

## 5. Estado actual del desarrollo

### Frontend

Existe una interfaz en `frontend/Demo.html`, los estilos en `frontend/estilos/style.css` y el JavaScript en `frontend/script.js`.

El proyecto utiliza una interfaz con menú lateral, secciones de formulario, controles de navegación y botones de acciones.

Se ha trabajado en un prototipo de workflow con los roles Docente, Administrador y Decano. Administración revisa, devuelve o aprueba los programas; el Decano autoriza las versiones aprobadas.

Los nombres del docente, del decano y de la persona responsable de Administración se escriben manualmente en campos de texto. La Facultad se registra en Información general.

El selector de rol utilizado para probar el workflow es una simulación; no representa un sistema real de autenticación y permisos.

### Backend

El archivo `backend/main.py` implementa un servidor Python usando `SimpleHTTPRequestHandler` y `ThreadingHTTPServer`.

El servidor se inicia con:

```bash
python3 backend/main.py
```

La dirección local es:

`http://127.0.0.1:8000`

El servidor carga `frontend/Demo.html` al abrir la ruta principal `/`.

Actualmente existen estos endpoints:

- `GET /api/programas`: lee y devuelve el contenido de `programas.json`.
- `PUT /api/programas`: recibe el JSON completo, valida que incluya `programas`, `versiones` e `historial`, y guarda los datos.

El método PUT utiliza un archivo temporal antes de reemplazar el JSON.

Estos endpoints funcionan como una API inicial. No representan todavía el workflow completo solicitado.

### Almacenamiento

El archivo `programas.json` contiene las colecciones `programas`, `versiones` e `historial`.

La estructura inicial contiene información del curso Programación Web, como código, asignatura, programa académico, facultad, departamento, ciclo, año, nivel, área de formación, pensum, modalidad, créditos, horas, sede, docente, versión actual y estado.

Antes de modificar los nombres de los campos o la estructura JSON, revisar los archivos existentes y mantener la compatibilidad con el frontend.

### GitHub

El repositorio del proyecto es:

`https://github.com/aldron01/grupo5-programas-curso.git`

Para registrar y subir cambios se utiliza Git. No confundir guardar archivos en VS Code con subirlos a GitHub.

## 6. Requisitos funcionales obligatorios

El sistema debe incluir:

1. Formularios organizados por secciones.
2. Creación y edición de programas de curso.
3. Guardado de borradores.
4. Guardado parcial de las secciones.
5. Creación y clonación de versiones.
6. Filas dinámicas que permitan agregar, eliminar y ordenar elementos cuando corresponda.
7. Validaciones de los datos requeridos.
8. Comparación de cambios entre versiones.
9. Historial de acciones y modificaciones.
10. Workflow de envío, revisión, devolución, aprobación y autorización.
11. Control de roles y permisos según las responsabilidades de cada usuario.
12. Una sola versión autorizada y vigente por programa.
13. Generación y descarga de PDF institucional.
14. Comunicación real entre frontend y backend.
15. Persistencia de los datos, para que no desaparezcan al recargar la página.

No marcar una funcionalidad como completada si solamente muestra un mensaje visual, pero no realiza la operación correspondiente.

## 7. Secciones del programa de curso

El formulario debe contemplar las siguientes secciones:

### Información general
Código, asignatura, programa académico, departamento, facultad, ciclo, año, nivel, área de formación, pensum, modalidad, créditos, horas semanales, sede y docente.

### Prerrequisitos
Asignatura, código y orden de los prerrequisitos.

### Descripción
Descripción general del curso.

### Competencias
Competencia general y competencias específicas.

### Perfil de egreso
Código y contribución de la asignatura al perfil de egreso.

### Contenidos
Organización de los contenidos del curso, incluyendo filas dinámicas si el formulario lo requiere.

### Bibliografía
Referencias bibliográficas del curso.

### Evaluación
Actividades, criterios, distribución de puntos y otros campos que establezca el formulario institucional.

### Autorización
Información relacionada con responsables, revisión, aprobación y autorización del programa.

Estas secciones deben verificarse contra `Formulario.pdf`. Si el documento contiene campos adicionales, deben incluirse según los requisitos originales.

## 8. Workflow del sistema

El flujo general esperado es:

**Borrador → Enviado → En revisión → Devuelto o Aprobado → Autorizado → Vigente**

Comportamiento:

- **Docente:** crea y edita el programa, guarda borradores y lo envía a revisión.
- **Administrador:** revisa el contenido, puede devolverlo o aprobarlo, y crea nuevas versiones a partir de una versión autorizada.
- **Decano:** autoriza las versiones aprobadas.

Reglas importantes:

- No enviar a revisión si faltan datos obligatorios.
- La devolución debe registrar una observación.
- No permitir autorizar una versión que no haya sido aprobada.
- Una versión autorizada debe conservarse como registro histórico.
- Las modificaciones posteriores deben realizarse en una nueva versión.
- Al autorizar una nueva versión, la anterior deja de ser vigente, sin borrar su historial.
- No permitir transiciones de estado que incumplan el workflow.

Los permisos deben validarse en el backend. Ocultar botones en JavaScript no constituye seguridad suficiente.

## 9. Endpoints REST planificados

Los siguientes endpoints son los objetivos de la API. Deben implementarse y probarse antes de considerarlos terminados.

### Programas

- `GET /course-programs`: listar programas.
- `POST /course-programs`: crear un programa.
- `GET /course-programs/{id}`: consultar un programa y sus versiones.

### Versiones

- `POST /course-programs/{id}/versions`: crear una versión o clonar un borrador.
- `GET /program-versions/{id}`: consultar una versión.
- `PUT /program-versions/{id}`: guardar una versión completa.
- `PUT /program-versions/{id}/sections/{section}`: guardar una sección específica.
- `GET /program-versions/{id}/changes`: comparar con la versión anterior.

### Workflow

- `POST /program-versions/{id}/submit`: enviar a revisión.
- `POST /program-versions/{id}/return`: devolver con observaciones.
- `POST /program-versions/{id}/approve`: aprobar contenido.
- `POST /program-versions/{id}/authorize`: autorizar y declarar vigente.

### PDF

- `GET /program-versions/{id}/pdf`: generar o descargar el PDF institucional.

**Importante:** estos endpoints usan las rutas previstas en los requisitos. La API actual utiliza `/api/programas`. Antes de cambiar las rutas, definir una estructura coherente y actualizar tanto el backend como el frontend. Si se adopta `/api/v1`, mantener todas las rutas bajo ese prefijo de forma consistente.

## 10. Fases originales del proyecto

### Fase 1: propuesta y estructura

- Definir el objetivo.
- Identificar las secciones del programa de curso.
- Seleccionar tecnologías.
- Preparar la estructura de carpetas.
- Crear el repositorio.
- Elaborar el README inicial.
- Preparar un primer diseño de la interfaz.

Entregable: estructura inicial del proyecto y prototipo sencillo de la pantalla principal.

### Fase 2: prototipo visual básico

- Crear la página HTML principal.
- Diseñar el menú lateral.
- Organizar las secciones.
- Agregar los campos básicos del formulario.
- Incorporar botones de navegación, guardar y cancelar.
- Probar con datos de ejemplo.

Entregable: página HTML funcional para realizar pruebas.

### Siguientes fases de desarrollo

Completar el JavaScript, conectar la API REST, persistir los datos, implementar versiones e historial, desarrollar el workflow y generar el PDF. Después, probar las reglas de permisos y autorización.

Las fases posteriores deben ajustarse a la planificación académica completa si el documento original especifica entregables adicionales.

## 11. Flujo de datos

Cuando el usuario consulta un programa, el frontend solicita los datos al backend.

Cuando el usuario guarda cambios, el frontend envía la información a la API.

El backend valida la solicitud, actualiza el almacenamiento y devuelve una respuesta.

La interfaz debe mostrar un mensaje de éxito o error según el resultado real del servidor.

El sistema no debe fingir que guardó los cambios cuando la solicitud falla o cuando todavía no existe conexión con la API.

## 12. Reglas de trabajo para la IA de VS Code

- Leer los archivos actuales antes de proponer cambios.
- Trabajar sobre el proyecto existente, no empezar uno nuevo.
- Conservar las funciones que ya funcionan.
- Evitar reemplazar todos los archivos si solo se necesita modificar una parte.
- Explicar los cambios en español sencillo, casual y natural.
- Usar comentarios cortos y útiles en el código.
- Entregar archivos completos cuando el usuario solicite expresamente reemplazarlos.
- No inventar funciones implementadas ni afirmar que se hicieron pruebas que no se ejecutaron.
- Explicar cómo probar cada funcionalidad.
- Mantener los nombres de campos y rutas consistentes.
- Comprobar errores, validaciones y persistencia.
- Priorizar los requisitos académicos y el funcionamiento real sobre las mejoras visuales innecesarias.

## 13. Próximo paso recomendado

Primero, inspeccionar `main.py`, `programas.json`, `Demo.html`, `script.js`, `style.css` y `Formulario.pdf`.

Después, identificar qué funciones están realmente terminadas y cuáles faltan.

A continuación, implementar los endpoints de programas y versiones, conectar los formularios con la API, desarrollar el workflow, registrar el historial, agregar la comparación de versiones y terminar la generación del PDF.

Trabajar por etapas, probando cada parte antes de continuar.

**Objetivo final:** tener una aplicación funcional que cumpla los requisitos del Grupo 5 y permita administrar programas de curso con formularios por secciones, versiones, workflow docente, autorización de una única versión vigente y generación de PDF institucional.

## 14. Estado verificado del proyecto y roles (2026-10-09)

Se leyeron `proyecto1.md` y todos los archivos dentro de `backend/` y `frontend/`. No se ejecutó la aplicación. `backend/requirements.txt` está vacío.

### Roles del prototipo

- `docente` / Docente: puede guardar un borrador y enviarlo a revisión cuando hay un nombre de docente.
- `administrador` / Administrador: puede devolver o aprobar una versión en revisión cuando se escribió su nombre, y crear una nueva versión desde una versión autorizada.
- `decano` / Decano: puede autorizar una versión aprobada cuando se escribió su nombre.

El selector de roles solo simula quién usa la pantalla; no es autenticación y no protege acciones en el servidor. En Responsables del programa se escriben los nombres del Docente, del Decano y de la persona responsable de Administración; la Facultad se captura en Información general. El rol Coordinador se quitó; Administración realiza la revisión, devolución y aprobación, mientras el Decano autoriza. El Administrador también puede crear versiones según el workflow descrito arriba.

### Implementación observada

- `backend/main.py` sirve los archivos de `frontend/` y expone `GET /api/programas` y `PUT /api/programas`. El PUT valida las colecciones `programas`, `versiones` e `historial`, escribe un temporal y reemplaza `programas.json`.
- `frontend/script.js` no hace solicitudes a la API. El botón de guardar solo cambia el estado en memoria del navegador; las transiciones del workflow y el contador de versión tampoco persisten ni crean registros en JSON.
- Devolver una versión no solicita ni registra observaciones. El botón Cancelar solo muestra una confirmación y un mensaje; no restaura valores.
- La vista previa del PDF se construye en el navegador y `window.print()` permite imprimirla o guardarla. No se observó generación de PDF en el backend.
- `frontend/Demo.html` contiene secciones de información general, prerrequisitos, descripción, competencias, perfil de egreso, metodología y evaluación. Aún se debe contrastar con `Formulario.pdf` para confirmar campos y secciones faltantes.
- `frontend/estilos/style.css` define estilos propios para la interfaz, el flujo visual de roles, la vista previa/impresión y el diseño adaptable.

Se quitó el rol Coordinador. Administración realiza la revisión, devolución y aprobación, y el Decano autoriza las versiones aprobadas. En Responsables del programa están los campos de nombre del Docente, del Decano y del Responsable de Administración, en ese orden; la Facultad se usa desde Información general. El programa solo se edita con el rol Docente en estado borrador o devuelto; el nombre de Administración se edita durante la revisión y antes de crear una versión; y el nombre del Decano se edita al autorizar. La vista PDF muestra esos responsables y sus firmas. No se ejecutaron pruebas ni la aplicación.
