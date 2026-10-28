# Programas de curso UDV

Módulo para gestionar programas de curso, sus versiones y la generación del PDF institucional.

## Estructura del proyecto

```text
grupo-5-programas-pdf/
├── .env.example
├── .gitignore
├── requirements.txt
├── g5_programas/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── domain.py
│   ├── errors.py
│   ├── pdf.py
│   ├── pdf_service.py
│   ├── repository.py
│   └── router.py
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
    ├── overview.md
    └── workflow.md
```

## Arranque rápido

1. Configure `.env` con su `DATABASE_URL`.
2. Instale dependencias: `pip install -r requirements.txt`.
3. Ejecute las pruebas: `pytest -q`.

El paquete `g5_programas` es un módulo de integración: expone `router` para que la aplicación común lo registre, y no contiene un servidor independiente ni un `main.py` local.

## Módulos principales

- `g5_programas/router.py`: endpoints de programas, versiones, transiciones y PDF.
- `g5_programas/domain.py`: reglas de estados y validaciones de negocio.
- `g5_programas/repository.py`: consultas y operaciones sobre MySQL.
- `g5_programas/auth.py`: actor autenticado y validación de roles.
- `g5_programas/pdf_service.py`: generación del documento institucional.
