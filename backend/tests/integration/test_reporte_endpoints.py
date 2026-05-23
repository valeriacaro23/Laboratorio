"""
Pruebas de integración para los endpoints de reportes.

Endpoints cubiertos:
  GET /reportes/uso-laboratorio
  GET /reportes/uso-laboratorio/csv
  GET /reportes/ocupacion-mensual
  GET /reportes/por-docente
  GET /reportes/por-docente/csv

Usa SQLite en memoria y TestClient de FastAPI (via fixture `client`).
Para COORDINADOR se crea fixture local ya que conftest no lo provee.

NOTA: El repositorio usa funciones SQL Server-specific (datediff, month, year)
incompatibles con SQLite. Para los tests que verifican control de acceso Y
que se espera que lleguen al repositorio, se mockea reporte_service para
devolver listas vacías y validar solo HTTP status y estructura de respuesta.
"""
import pytest
from unittest.mock import patch
from app.models.usuario import Usuario
from app.services.auth_service import hash_password
from app.schemas.reporte_schema import ReporteUsoLaboratorio, ReporteDocente


# ---------------------------------------------------------------------------
# Fixtures locales (COORDINADOR no existe en conftest)
# ---------------------------------------------------------------------------

@pytest.fixture()
def usuario_coordinador(db):
    """Usuario con rol COORDINADOR, activo."""
    u = Usuario(
        email="coordinador@uni.edu",
        password_hash=hash_password("coord1234"),
        rol="COORDINADOR",
        activo=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def token_coordinador(client, usuario_coordinador):
    """JWT de un COORDINADOR obtenido a través del endpoint real."""
    resp = client.post("/auth/login", json={
        "email": usuario_coordinador.email,
        "password": "coord1234",  # NOSONAR
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# GET /reportes/uso-laboratorio
# ---------------------------------------------------------------------------

def test_uso_laboratorio_sin_token(client):
    """GET /reportes/uso-laboratorio sin Authorization responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/reportes/uso-laboratorio")

    # Assert
    assert resp.status_code == 401


def test_uso_laboratorio_rol_docente(client, token_docente):
    """GET /reportes/uso-laboratorio con token DOCENTE responde 403."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_docente}"}

    # Act
    resp = client.get("/reportes/uso-laboratorio", headers=headers)

    # Assert
    assert resp.status_code == 403


def test_uso_laboratorio_rol_admin(client, token_admin):
    """GET /reportes/uso-laboratorio con token ADMIN responde 200 y body es lista."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act: mockear el service para evitar SQL Server-specific functions en SQLite
    with patch(
        "app.controller.reporte_controller.reporte_service.generar_uso_laboratorio",
        return_value=[],
    ):
        resp = client.get("/reportes/uso-laboratorio", headers=headers)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


# ---------------------------------------------------------------------------
# GET /reportes/ocupacion-mensual
# ---------------------------------------------------------------------------

def test_ocupacion_mensual_mes_invalido(client, token_admin):
    """GET /reportes/ocupacion-mensual?mes=13&anio=2024 con ADMIN responde 422."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act
    resp = client.get("/reportes/ocupacion-mensual?mes=13&anio=2024", headers=headers)

    # Assert
    assert resp.status_code == 422


def test_ocupacion_mensual_valido(client, token_admin):
    """GET /reportes/ocupacion-mensual?mes=1&anio=2024 con ADMIN responde 200."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act: mockear el service para evitar SQL Server-specific functions en SQLite
    with patch(
        "app.controller.reporte_controller.reporte_service.generar_ocupacion_mensual",
        return_value=[],
    ):
        resp = client.get("/reportes/ocupacion-mensual?mes=1&anio=2024", headers=headers)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


def test_ocupacion_mensual_sin_token(client):
    """GET /reportes/ocupacion-mensual sin token responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/reportes/ocupacion-mensual?mes=1&anio=2024")

    # Assert
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /reportes/por-docente
# ---------------------------------------------------------------------------

def test_por_docente_coordinador(client, token_coordinador):
    """GET /reportes/por-docente con token COORDINADOR responde 200."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_coordinador}"}

    # Act: mockear el service para evitar SQL Server-specific functions en SQLite
    with patch(
        "app.controller.reporte_controller.reporte_service.generar_por_docente",
        return_value=[],
    ):
        resp = client.get("/reportes/por-docente", headers=headers)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


def test_por_docente_sin_token(client):
    """GET /reportes/por-docente sin token responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/reportes/por-docente")

    # Assert
    assert resp.status_code == 401


def test_por_docente_rol_docente(client, token_docente):
    """GET /reportes/por-docente con token DOCENTE responde 403."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_docente}"}

    # Act
    resp = client.get("/reportes/por-docente", headers=headers)

    # Assert
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /reportes/uso-laboratorio/csv
# ---------------------------------------------------------------------------

def test_uso_laboratorio_csv(client, token_admin):
    """GET /reportes/uso-laboratorio/csv con ADMIN responde 200 y Content-Type tiene text/csv."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act: mockear el service para evitar SQL Server-specific functions en SQLite
    with patch(
        "app.controller.reporte_controller.reporte_service.generar_uso_laboratorio",
        return_value=[],
    ):
        resp = client.get("/reportes/uso-laboratorio/csv", headers=headers)

    # Assert
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


def test_uso_laboratorio_csv_sin_token(client):
    """GET /reportes/uso-laboratorio/csv sin token responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/reportes/uso-laboratorio/csv")

    # Assert
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /reportes/por-docente/csv
# ---------------------------------------------------------------------------

def test_por_docente_csv(client, token_admin):
    """GET /reportes/por-docente/csv con ADMIN responde 200 y Content-Type tiene text/csv."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act: mockear el service para evitar SQL Server-specific functions en SQLite
    with patch(
        "app.controller.reporte_controller.reporte_service.generar_por_docente",
        return_value=[],
    ):
        resp = client.get("/reportes/por-docente/csv", headers=headers)

    # Assert
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")


def test_por_docente_csv_sin_token(client):
    """GET /reportes/por-docente/csv sin token responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/reportes/por-docente/csv")

    # Assert
    assert resp.status_code == 401
