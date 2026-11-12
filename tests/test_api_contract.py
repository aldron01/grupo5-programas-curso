import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import FastAPI, HTTPException, Request

from g5_programas import auth as g5_auth
from g5_programas.database import get_session
from g5_programas.errors import ApiError, registrar_errores
from g5_programas.repository import _assignment_origin_id, list_programs
from g5_programas.router import router


def _asgi_request(app, method, path, *, headers=(), body=b""):
    messages = []
    request_sent = False

    async def receive():
        nonlocal request_sent
        if request_sent:
            return {"type": "http.disconnect"}
        request_sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": list(headers),
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }
    asyncio.run(app(scope, receive, send))
    start = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start["status"], json.loads(response_body) if response_body else None


class ApiContractTests(unittest.TestCase):
    def test_api_error_is_compatible_with_fastapi_handlers(self):
        error = ApiError(409, "CONFLICT", "No se puede continuar.", {"estado": "inválido"})

        self.assertIsInstance(error, HTTPException)
        self.assertEqual(error.status_code, 409)
        self.assertEqual(
            error.detail,
            {
                "code": "CONFLICT",
                "message": "No se puede continuar.",
                "details": {"estado": "inválido"},
            },
        )

    def test_registered_error_handler_returns_common_http_json(self):
        app = FastAPI()
        registrar_errores(app)

        @app.get("/missing")
        def missing():
            raise ApiError(404, "NOT_FOUND", "Programa no encontrado.", {"id": 99})

        messages = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/missing",
            "raw_path": b"/missing",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        }
        asyncio.run(app(scope, receive, send))
        response_start = next(message for message in messages if message["type"] == "http.response.start")
        response_body = b"".join(
            message.get("body", b"")
            for message in messages
            if message["type"] == "http.response.body"
        )

        self.assertEqual(response_start["status"], 404)
        self.assertEqual(
            json.loads(response_body),
            {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Programa no encontrado.",
                    "details": {"id": 99},
                }
            },
        )

    def test_program_list_filters_are_applied_to_count_and_data(self):
        session = Mock()
        count_result = Mock()
        count_result.scalar_one.return_value = 1
        rows_result = Mock()
        rows_result.mappings.return_value = []
        session.execute.side_effect = [count_result, rows_result]

        result = list_programs(
            session,
            2,
            10,
            curso_id=7,
            periodo_id=3,
            sede_id=2,
            estado="draft",
            version=4,
        )

        self.assertEqual(result, {"page": 2, "per_page": 10, "total": 1, "data": []})
        count_call, rows_call = session.execute.call_args_list
        count_sql = str(count_call.args[0])
        rows_sql = str(rows_call.args[0])
        expected_filters = (
            "pc.curso_id = :curso_id",
            "pv.periodo_id = :periodo_id",
            "pc.sede_id = :sede_id",
            "pv.estado_codigo = :estado",
            "pv.numero_version = :version",
        )
        for expression in expected_filters:
            self.assertIn(expression, count_sql)
            self.assertIn(expression, rows_sql)
        expected_params = {
            "curso_id": 7,
            "periodo_id": 3,
            "sede_id": 2,
            "estado": "draft",
            "version": 4,
        }
        self.assertEqual(count_call.args[1], expected_params)
        self.assertEqual(
            rows_call.args[1],
            {**expected_params, "limit": 10, "offset": 10},
        )

    def test_program_list_filters_are_in_openapi(self):
        app = FastAPI()
        app.include_router(router)

        parameters = app.openapi()["paths"]["/api/v1/course-programs"]["get"]["parameters"]

        self.assertEqual(
            {parameter["name"] for parameter in parameters},
            {"page", "per_page", "curso_id", "periodo_id", "sede_id", "estado", "version"},
        )

    def test_assignment_origin_id_is_optional_and_validated(self):
        self.assertIsNone(_assignment_origin_id({}))
        self.assertEqual(_assignment_origin_id({"tarea_destinatario_origen_id": "17"}), 17)
        for invalid_id in ("abc", 0, -1, 1.5, True):
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(ApiError) as caught:
                    _assignment_origin_id({"tarea_destinatario_origen_id": invalid_id})
                self.assertEqual(caught.exception.status, 422)

    def test_authorize_endpoint_accepts_g2_authority_principal_over_http(self):
        app = FastAPI()
        registrar_errores(app)
        app.include_router(router)

        test_users = {
            "authority-token": SimpleNamespace(
                id=6,
                nombres="Alberto",
                apellidos="Director",
                roles=[SimpleNamespace(codigo="authority")],
            ),
            "teacher-token": SimpleNamespace(
                id=3,
                nombres="Diana",
                apellidos="Docente",
                roles=[SimpleNamespace(codigo="teacher")],
            ),
            "auditor-token": SimpleNamespace(
                id=7,
                nombres="Laura",
                apellidos="Auditora",
                roles=[SimpleNamespace(codigo="auditor")],
            ),
        }

        async def g2_user(request: Request):
            authorization = request.headers.get("authorization", "")
            scheme, _, token = authorization.partition(" ")
            user = test_users.get(token) if scheme.lower() == "bearer" else None
            if user is None:
                raise ApiError(401, "UNAUTHENTICATED", "Token de prueba inválido.")
            return user

        def test_session():
            yield Mock()

        app.dependency_overrides[g5_auth.obtener_usuario_actual] = g2_user
        app.dependency_overrides[get_session] = test_session

        with patch(
            "g5_programas.router.repository.transition",
            return_value={"id": 41, "estado": "authorized"},
        ) as transition:
            status, body = _asgi_request(
                app,
                "POST",
                "/api/v1/program-versions/41/authorize",
                headers=[(b"content-type", b"application/json")],
                body=b"{}",
            )
            self.assertEqual(status, 401)

            status, body = _asgi_request(
                app,
                "POST",
                "/api/v1/program-versions/41/authorize",
                headers=[
                    (b"authorization", b"Bearer teacher-token"),
                    (b"content-type", b"application/json"),
                ],
                body=b"{}",
            )
            self.assertEqual(status, 403)
            transition.assert_not_called()

            status, body = _asgi_request(
                app,
                "POST",
                "/api/v1/program-versions/41/authorize",
                headers=[
                    (b"authorization", b"Bearer authority-token"),
                    (b"content-type", b"application/json"),
                ],
                body=b"{}",
            )

        self.assertEqual(status, 200)
        self.assertEqual(body, {"ok": True, "version": {"id": 41, "estado": "authorized"}})
        transition.assert_called_once()

    def test_g2_auditor_bearer_can_read_but_not_create_programs_over_http(self):
        app = FastAPI()
        registrar_errores(app)
        app.include_router(router)
        auditor = SimpleNamespace(
            id=7,
            nombres="Laura",
            apellidos="Auditora",
            roles=[SimpleNamespace(codigo="auditor")],
        )

        async def g2_user(request: Request):
            if request.headers.get("authorization") != "Bearer auditor-token":
                raise ApiError(401, "UNAUTHENTICATED", "Token de prueba inválido.")
            return auditor

        def test_session():
            yield Mock()

        app.dependency_overrides[g5_auth.obtener_usuario_actual] = g2_user
        app.dependency_overrides[get_session] = test_session

        with patch(
            "g5_programas.router.repository.list_programs",
            return_value={"page": 1, "per_page": 20, "total": 0, "data": []},
        ) as list_programs_mock, patch(
            "g5_programas.router.repository.create_program",
        ) as create_program_mock:
            status, body = _asgi_request(
                app,
                "GET",
                "/api/v1/course-programs",
                headers=[(b"authorization", b"Bearer auditor-token")],
            )
            self.assertEqual(status, 200)
            self.assertEqual(body["data"], [])
            list_programs_mock.assert_called_once()

            status, body = _asgi_request(
                app,
                "POST",
                "/api/v1/course-programs",
                headers=[
                    (b"authorization", b"Bearer auditor-token"),
                    (b"content-type", b"application/json"),
                ],
                body=b"{}",
            )

        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["code"], "FORBIDDEN")
        create_program_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
