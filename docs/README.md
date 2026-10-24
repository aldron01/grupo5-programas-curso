# Programas de curso UDV

Aplicación para gestionar programas de curso, sus versiones y el flujo de revisión hasta la generación del PDF institucional.

## Estructura
- `backend/`: API en FastAPI, servicios de PDF y lógica de negocio.
- `frontend/`: Interfaz web y recursos estáticos.
- `grupos/`: Módulo core G5 (Router y persistencia).
- `tests/`: Pruebas automatizadas de transiciones.

## Arranque rápido
1. Configure `.env` con su `DATABASE_URL`.
2. Instale dependencias: `pip install -r requirements.txt`.
3. Ejecute: `uvicorn main:app --reload --env-file .env`.

API Docs: `/api/v1/docs` | Interfaz: `/`
