# Programas de curso UDV

Módulo FastAPI para gestionar programas de curso y sus versiones, controlar el
flujo de revisión y autorización, y generar el PDF institucional. G5 se integra
con la aplicación compartida y la base de datos de G1; este repositorio no
incluye un servidor FastAPI independiente ni un `main.py`.

## Estructura

```text
grupo-5-programas-pdf/
├── .env.example
├── .gitignore
├── requirements.txt
├── g5_programas/
│   ├── __init__.py
│   ├── auth.py             # Autenticación G2 y permisos por rol
│   ├── database.py         # Sesiones SQLAlchemy y errores de MySQL
│   ├── domain.py           # Estados y reglas de transición
│   ├── errors.py           # Errores de API
│   ├── pdf.py              # Adaptador del generador de PDF
│   ├── pdf_service.py      # Construcción del documento con ReportLab
│   ├── repository.py       # Consultas y operaciones sobre el esquema G1
│   └── router.py           # Rutas bajo /api/v1
├── frontend/
│   ├── Programa.html
│   ├── script.js
│   ├── assets/
│   │   └── udv-logo.jpg
│   └── estilos/
│       ├── style.css
│       └── udv.css
├── tests/
│   ├── conftest.py
│   └── test_program_flow.py
└── docs/
    ├── README.md
    └── instrucciones.md
```

## Requisitos e integración

- Python 3.10 o posterior.
- Una base MySQL compatible con el esquema compartido de G1, incluyendo sus
  catálogos, tablas, vistas y procedimientos usados por el repositorio. La
  autorización utiliza `sp_autorizar_version`.
- Una aplicación host FastAPI que registre `g5_programas.router`, configure
  `app.state.database_session_factory` (o permita que G5 cree la sesión desde
  `DATABASE_URL`) y tenga disponible el paquete G2 con
  `g2_api.routers.auth.obtener_usuario_actual`.

Instale las dependencias del módulo:

```bash
python -m pip install -r requirements.txt
```

Configure `DATABASE_URL` en el entorno del proceso host con una URL de
SQLAlchemy para MySQL, por ejemplo:

```bash
export DATABASE_URL='mysql+pymysql://usuario:clave@localhost:3306/db_udv'
```

`.env.example` es una plantilla; el proyecto no carga archivos `.env`
automáticamente. En producción, proporcione la variable mediante el mecanismo
de configuración de la aplicación host.

Registre el router desde la aplicación compartida:

```python
from fastapi import FastAPI
from g5_programas import router

app = FastAPI()
app.include_router(router)
```

G5 usa `obtener_usuario_actual` de G2 como dependencia de autenticación. Si
G2 no está disponible, los endpoints protegidos responden con error 503. Si no
configura una fábrica de sesiones propia, G5 usa `DATABASE_URL`.

## Frontend y pruebas

El frontend está en `frontend/`. Actualmente `script.js` apunta a
`http://127.0.0.1:8000/api/v1` y carga el programa con ID `1`; ajuste esos
valores para el entorno donde se publique. El selector de rol y los nombres
mostrados en la página son parte de la interfaz de demostración: no sustituyen
la sesión autenticada ni los permisos que valida el backend.

Ejecute las pruebas disponibles desde la raíz:

```bash
pytest -q
```

Las pruebas actuales cubren transiciones, estados editables, unicidad de la
versión autorizada y permisos; no reemplazan una prueba de integración con
MySQL y la aplicación host.

## Documentación

- [Instrucciones para QA](instrucciones.md): contexto, cambios que revisar,
  pruebas y pendientes de integración.
