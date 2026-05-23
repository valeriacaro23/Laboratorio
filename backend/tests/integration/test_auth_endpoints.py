"""
Pruebas de integración para los endpoints de autenticación y usuarios.

Endpoints cubiertos:
  POST /auth/login
  POST /auth/register
  GET  /usuarios/me
  GET  /usuarios/

Usa SQLite en memoria y TestClient de FastAPI (via fixture `client`).
"""
import datetime
import pytest
from jose import jwt

from app.security.config import JWT_SECRET, ALGORITHM


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

def test_login_con_credenciales_correctas_devuelve_200_y_jwt(client, usuario_admin):
    """POST /auth/login con email y password válidos responde 200 con access_token."""
    # Arrange
    payload_req = {"email": usuario_admin.email, "password": "admin1234"}  # NOSONAR

    # Act
    resp = client.post("/auth/login", json=payload_req)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    # Verificar que el token es un JWT válido con los campos del contrato
    decoded = jwt.decode(body["access_token"], JWT_SECRET, algorithms=[ALGORITHM])
    assert decoded["email"] == usuario_admin.email
    assert decoded["rol"] == "ADMIN"
    assert "sub" in decoded
    assert "exp" in decoded


def test_login_con_password_incorrecto_devuelve_401(client, usuario_admin):
    """POST /auth/login con password equivocada responde 401."""
    # Arrange
    payload_req = {"email": usuario_admin.email, "password": "wrong_password"}

    # Act
    resp = client.post("/auth/login", json=payload_req)

    # Assert
    assert resp.status_code == 401


def test_login_con_email_inexistente_devuelve_401(client):
    """POST /auth/login con email que no existe en BD responde 401."""
    # Arrange
    payload_req = {"email": "fantasma@uni.edu", "password": "cualquier"}  # NOSONAR

    # Act
    resp = client.post("/auth/login", json=payload_req)

    # Assert
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /usuarios/me
# ---------------------------------------------------------------------------

def test_get_me_con_bearer_valido_devuelve_200_y_perfil(client, usuario_docente, token_docente):
    """GET /usuarios/me con token válido responde 200 con datos del usuario."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_docente}"}

    # Act
    resp = client.get("/usuarios/me", headers=headers)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == usuario_docente.email
    assert body["rol"] == "DOCENTE"
    assert "usuario_id" in body
    assert "activo" in body


def test_get_me_sin_bearer_devuelve_401(client):
    """GET /usuarios/me sin encabezado Authorization responde 401."""
    # Arrange: sin headers

    # Act
    resp = client.get("/usuarios/me")

    # Assert
    assert resp.status_code == 401


def test_get_me_con_jwt_expirado_devuelve_401(client, usuario_admin):
    """GET /usuarios/me con JWT cuyo exp ya pasó responde 401."""
    # Arrange: crear token con expiración en el pasado
    payload = {
        "sub": usuario_admin.usuario_id,
        "email": usuario_admin.email,
        "rol": usuario_admin.rol,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
    }
    expired_token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    headers = {"Authorization": f"Bearer {expired_token}"}

    # Act
    resp = client.get("/usuarios/me", headers=headers)

    # Assert
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

def test_register_con_rol_admin_crea_usuario_y_devuelve_201(client, token_admin):
    """POST /auth/register con ADMIN Bearer crea el usuario y responde 201."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}
    nuevo_usuario = {
        "email": "prof.nuevo@uni.edu",
        "password": "NuevaPass99!",  # NOSONAR
        "rol": "DOCENTE",
    }

    # Act
    resp = client.post("/auth/register", json=nuevo_usuario, headers=headers)

    # Assert
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "prof.nuevo@uni.edu"
    assert body["rol"] == "DOCENTE"
    assert "usuario_id" in body
    # La contraseña NUNCA debe aparecer en la respuesta
    assert "password" not in body
    assert "password_hash" not in body


def test_register_con_rol_docente_devuelve_403(client, token_docente):
    """POST /auth/register con token DOCENTE responde 403."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_docente}"}
    nuevo_usuario = {
        "email": "otro@uni.edu",
        "password": "Pass1234!",  # NOSONAR
        "rol": "CONSULTA",
    }

    # Act
    resp = client.post("/auth/register", json=nuevo_usuario, headers=headers)

    # Assert
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /usuarios/
# ---------------------------------------------------------------------------

def test_listar_usuarios_con_rol_admin_devuelve_lista(client, token_admin, usuario_admin, usuario_docente):
    """GET /usuarios/ con token ADMIN responde 200 con lista de usuarios."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Act
    resp = client.get("/usuarios/", headers=headers)

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    # Verificar estructura del primer elemento
    primer = body[0]
    assert "usuario_id" in primer
    assert "email" in primer
    assert "rol" in primer
    assert "activo" in primer


def test_listar_usuarios_con_rol_docente_devuelve_403(client, token_docente):
    """GET /usuarios/ con token DOCENTE responde 403."""
    # Arrange
    headers = {"Authorization": f"Bearer {token_docente}"}

    # Act
    resp = client.get("/usuarios/", headers=headers)

    # Assert
    assert resp.status_code == 403
