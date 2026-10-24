# Flujo del sistema

## Componentes

- `frontend/` contiene la interfaz del programa de curso.
- `backend/app.py` integra FastAPI, los routers disponibles y el frontend.
- `grupos/grupo-5-programas-pdf/g5_programas/` implementa las rutas de G5,
  autenticación delegada a G2 y persistencia en el esquema MySQL de G1.
- `backend/pdf_service.py` genera el documento institucional.

## Inicio

La API requiere una base MySQL inicializada con el esquema y las semillas de G1.
Copia `.env.example` a `.env`, configura `DATABASE_URL` con tus credenciales y
ejecuta desde la raíz:

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --env-file .env
```

La documentación OpenAPI está en `/api/v1/docs`. Las rutas de G5 usan el
prefijo `/api/v1`; requieren el principal autenticado que instala G2.

## Estados de una versión

```text
draft -> submitted -> under_review -> approved -> authorized
                         |                         |
                         v                         v
                      returned                 superseded
                         |
                         +------> submitted
```

Solo `draft` y `returned` son editables. `POST /program-versions/{id}/review`
toma una versión enviada y la cambia de `submitted` a `under_review`.
La autorización la procesa `sp_autorizar_version` en MySQL; la base protege
la inmutabilidad de versiones autorizadas y la unicidad de la versión vigente.

El PDF se descarga desde `/api/v1/program-versions/{id}/pdf` y solo se genera
para versiones `authorized` o `superseded`.
