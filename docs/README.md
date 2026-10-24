# Programas de curso UDV

Aplicación para gestionar programas de curso, sus versiones, el flujo de
revisión y los PDF institucionales. El backend está en FastAPI y persiste en
MySQL mediante el esquema compartido del Grupo 1.

## Estructura

```text
backend/                         Aplicación FastAPI y servicios de PDF
frontend/                        Interfaz web, estilos y recursos
grupos/grupo-5-programas-pdf/    Router y lógica del módulo G5
tests/                           Pruebas automatizadas
docs/                            Guías del proyecto y del flujo
main.py                          Exporta backend.app:app para Uvicorn
requirements.txt                 Dependencias Python
```

## Requisitos y arranque

1. Inicializa MySQL con el esquema y las semillas del Grupo 1.
2. Crea un `.env` local a partir de `.env.example` y configura `DATABASE_URL`
   con las credenciales de Railway. `.env` está excluido de Git; no compartas
   ni subas ese archivo.

3. Desde la raíz del repositorio instala y ejecuta:

   ```sh
   pip install -r requirements.txt
   uvicorn main:app --reload --env-file .env
   ```

OpenAPI está disponible en `/api/v1/docs`. La interfaz se sirve en `/` y los
endpoints del módulo usan el prefijo `/api/v1`.

## Pruebas

```sh
python -m unittest discover -s tests -v
```

Consulta [overview.md](overview.md), [workflow.md](workflow.md) y
[documentación del módulo G5](g5-programas.md) para más detalles.
