# Grupo 5 — Programas de curso, versiones y PDF

La aplicación gestiona programas de curso, sus versiones y el flujo de
revisión, aprobación y autorización. El backend usa FastAPI; los datos se
persisten en el esquema compartido MySQL de G1. No se usa `programas.json`.

## Estructura principal

```text
backend/
  app.py                 Compatibilidad de importación de la aplicación
  main.py                Aplicación FastAPI
  pdf_service.py         Generación del PDF institucional
grupos/
  grupo-5-programas-pdf/
    g5_programas/        Router, autenticación, reglas y persistencia de G5
frontend/                Interfaz web
tests/                   Pruebas de transiciones e invariantes
main.py                  Punto de entrada para Uvicorn
requirements.txt         Dependencias del proyecto
```

## Ejecutar

Inicializa MySQL con el esquema/semillas de G1. Copia `.env.example` a `.env`,
configura `DATABASE_URL` con tus credenciales locales y, desde la raíz:

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --env-file .env
```

OpenAPI se publica en `/api/v1/docs`. Los endpoints de G5 tienen el prefijo
`/api/v1`. El middleware de G2 debe instalar el usuario autenticado en la
petición; G5 toma de ese principal el ID y los roles, nunca del JSON enviado
por el cliente.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
