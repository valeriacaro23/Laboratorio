"""
Pruebas unitarias del módulo auth_service.

Cubre: hash_password, verify_password, crear_access_token, login, registrar.
Todas usan SQLite en memoria via fixture `db` del conftest.
"""
import datetime
import pytest
from fastapi import HTTPException
from jose import jwt

from app.services.auth_service import (
    hash_password,
    verify_password,
    crear_access_token,
    login,
    registrar,
)
from app.schemas.usuario_schema import UsuarioCreate
from app.models.usuario import Usuario
from app.security.config import JWT_SECRET, ALGORITHM


# ---------------------------------------------------------------------------
# hash_password / verify_password
# ---------------------------------------------------------------------------

def test_hash_password_produce_hash_bcrypt_verificable():
    """hash_password genera un hash que bcrypt puede verificar directamente."""
    # Arrange
    plain = "MiClave$ecreta99"

    # Act
    hashed = hash_password(plain)

    # Assert: el hash es diferente al texto plano
    assert hashed != plain
    # El hash comienza con el prefijo bcrypt
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    # verify_password lo reconoce como válido
    assert verify_password(plain, hashed) is True


def test_verify_password_retorna_true_con_password_correcto():
    """verify_password devuelve True cuando el plain coincide con el hash."""
    # Arrange
    plain = "ClaveCorrecta123"
    hashed = hash_password(plain)

    # Act
    resultado = verify_password(plain, hashed)

    # Assert
    assert resultado is True


def test_verify_password_retorna_false_con_password_incorrecto():
    """verify_password devuelve False cuando el plain NO coincide con el hash."""
    # Arrange
    plain = "ClaveCorrecta123"
    hashed = hash_password(plain)

    # Act
    resultado = verify_password("ClaveEquivocada!", hashed)

    # Assert
    assert resultado is False


# ---------------------------------------------------------------------------
# crear_access_token
# ---------------------------------------------------------------------------

def test_crear_access_token_genera_jwt_con_campos_requeridos():
    """crear_access_token incluye sub, email, rol y exp en el payload."""
    # Arrange
    data = {"sub": "42", "email": "test@uni.edu", "rol": "DOCENTE"}

    # Act
    token = crear_access_token(data)

    # Assert: decodificar sin verificar expiración para inspecccionar campos
    payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["email"] == "test@uni.edu"
    assert payload["rol"] == "DOCENTE"
    assert "exp" in payload


def test_crear_access_token_exp_es_futuro():
    """El campo exp del JWT debe ser una marca de tiempo en el futuro."""
    # Arrange
    data = {"sub": "1", "email": "a@b.com", "rol": "ADMIN"}

    # Act
    token = crear_access_token(data)

    # Assert
    payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    ahora = datetime.datetime.now(datetime.timezone.utc).timestamp()
    assert payload["exp"] > ahora


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

def test_login_retorna_token_response_con_credenciales_correctas(db):
    """login() devuelve TokenResponse cuando email y password son válidos."""
    # Arrange
    u = Usuario(
        email="usuario@test.com",
        password_hash=hash_password("clave_correcta"),
        rol="DOCENTE",
        activo=True,
    )
    db.add(u)
    db.commit()

    # Act
    resultado = login(db, "usuario@test.com", "clave_correcta")

    # Assert
    assert resultado.access_token is not None
    assert resultado.token_type == "bearer"
    # El token es decodificable y tiene los campos esperados
    payload = jwt.decode(resultado.access_token, JWT_SECRET, algorithms=[ALGORITHM])
    assert payload["email"] == "usuario@test.com"
    assert payload["rol"] == "DOCENTE"


def test_login_lanza_401_con_password_incorrecto(db):
    """login() lanza HTTPException 401 cuando la password no coincide."""
    # Arrange
    u = Usuario(
        email="otro@test.com",
        password_hash=hash_password("clave_real"),
        rol="ADMIN",
        activo=True,
    )
    db.add(u)
    db.commit()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        login(db, "otro@test.com", "clave_incorrecta")
    assert exc_info.value.status_code == 401


def test_login_lanza_401_con_email_inexistente(db):
    """login() lanza HTTPException 401 cuando el email no existe en BD."""
    # Arrange: no se crea ningún usuario con ese email

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        login(db, "noexiste@uni.edu", "cualquier_clave")
    assert exc_info.value.status_code == 401


def test_login_lanza_401_si_usuario_inactivo(db):
    """login() lanza HTTPException 401 cuando el usuario tiene activo=False."""
    # Arrange
    u = Usuario(
        email="inactivo@test.com",
        password_hash=hash_password("clave123"),
        rol="DOCENTE",
        activo=False,
    )
    db.add(u)
    db.commit()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        login(db, "inactivo@test.com", "clave123")
    assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# registrar
# ---------------------------------------------------------------------------

def test_registrar_crea_usuario_con_hash_nunca_texto_plano(db):
    """registrar() almacena password_hash — nunca la contraseña en texto plano."""
    # Arrange
    data = UsuarioCreate(email="nuevo@uni.edu", password="SecretPass1!", rol="DOCENTE")  # NOSONAR

    # Act
    usuario_creado = registrar(db, data)

    # Assert
    assert usuario_creado.usuario_id is not None
    # El hash nunca es igual al texto plano
    assert usuario_creado.password_hash != "SecretPass1!"
    # El hash es verificable con bcrypt
    assert verify_password("SecretPass1!", usuario_creado.password_hash) is True
    # El campo email quedó guardado correctamente
    assert usuario_creado.email == "nuevo@uni.edu"
    assert usuario_creado.rol == "DOCENTE"


def test_registrar_lanza_400_si_email_ya_existe(db):
    """registrar() lanza HTTPException 400 cuando el email ya está en uso."""
    # Arrange: crear usuario con ese email primero
    data = UsuarioCreate(email="duplicado@uni.edu", password="Pass1234!", rol="ADMIN")  # NOSONAR
    registrar(db, data)

    # Act & Assert: intentar registrar de nuevo con el mismo email
    with pytest.raises(HTTPException) as exc_info:
        registrar(db, UsuarioCreate(
            email="duplicado@uni.edu",
            password="OtraClave9!",  # NOSONAR
            rol="DOCENTE"
        ))
    assert exc_info.value.status_code == 400
