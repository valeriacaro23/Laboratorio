import os
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key-for-tests"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.db import get_db
from app.models.base import Base

# Registrar todos los modelos en Base antes de create_all
from app.models import laboratorio, reserva, historial_reserva  # noqa: F401
from app.models import usuario  # noqa: F401
from app.models.laboratorio import Laboratorio
from app.models.usuario import Usuario

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def db(create_tables):
    session = TestingSessionLocal()
    yield session
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def laboratorio_activo(db):
    lab = Laboratorio(
        nombre="Lab Computo A",
        ubicacion="Edificio Principal Piso 1",
        capacidad_maxima=30,
        tipo_laboratorio="COMPUTO",
        estado=True,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


@pytest.fixture()
def laboratorio_inactivo(db):
    lab = Laboratorio(
        nombre="Lab Inactivo B",
        ubicacion="Edificio Sur Piso 2",
        capacidad_maxima=20,
        tipo_laboratorio="ELECTRONICA",
        estado=False,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


# ---------------------------------------------------------------------------
# Fixtures de usuarios para pruebas de auth
# ---------------------------------------------------------------------------

@pytest.fixture()
def usuario_admin(db):
    """Usuario con rol ADMIN, activo."""
    from app.services.auth_service import hash_password
    u = Usuario(
        email="admin@uni.edu",
        password_hash=hash_password("admin1234"),
        rol="ADMIN",
        activo=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def usuario_docente(db):
    """Usuario con rol DOCENTE, activo."""
    from app.services.auth_service import hash_password
    u = Usuario(
        email="docente@uni.edu",
        password_hash=hash_password("docente1234"),
        rol="DOCENTE",
        activo=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def usuario_inactivo(db):
    """Usuario con rol DOCENTE pero inactivo."""
    from app.services.auth_service import hash_password
    u = Usuario(
        email="inactivo@uni.edu",
        password_hash=hash_password("inactivo1234"),
        rol="DOCENTE",
        activo=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture()
def token_admin(client, usuario_admin):
    """JWT de un ADMIN obtenido a través del endpoint real."""
    resp = client.post("/auth/login", json={
        "email": usuario_admin.email,
        "password": "admin1234",  # NOSONAR
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
def token_docente(client, usuario_docente):
    """JWT de un DOCENTE obtenido a través del endpoint real."""
    resp = client.post("/auth/login", json={
        "email": usuario_docente.email,
        "password": "docente1234",  # NOSONAR
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]
