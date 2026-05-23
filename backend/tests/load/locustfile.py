import os
import random
import datetime
from locust import HttpUser, task, between

ADMIN_EMAIL      = os.getenv("LOAD_ADMIN_EMAIL",      "admin@universidad.edu")
ADMIN_PASSWORD   = os.getenv("LOAD_ADMIN_PASSWORD",   "admin1234")  # NOSONAR
DOCENTE_EMAIL    = os.getenv("LOAD_DOCENTE_EMAIL",     "jp@universidad.edu")
DOCENTE_PASSWORD = os.getenv("LOAD_DOCENTE_PASSWORD",  "test1234")  # NOSONAR

_HORAS = [
    ("08:00:00", "10:00:00"),
    ("10:00:00", "12:00:00"),
    ("12:00:00", "14:00:00"),
    ("14:00:00", "16:00:00"),
    ("16:00:00", "18:00:00"),
]


class DocenteUser(HttpUser):
    weight    = 7
    wait_time = between(1, 3)

    def on_start(self):
        resp = self.client.post("/auth/login", json={
            "email":    DOCENTE_EMAIL,
            "password": DOCENTE_PASSWORD,
        })
        token = resp.json().get("access_token", "") if resp.status_code == 200 else ""
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(3)
    def listar_laboratorios(self):
        self.client.get("/laboratorios", headers=self.headers)

    @task(2)
    def listar_reservas(self):
        self.client.get("/reservas/", headers=self.headers)

    @task(1)
    def crear_reserva(self):
        dias = random.randint(1, 90)
        fecha = (datetime.date.today() + datetime.timedelta(days=dias)).isoformat()
        inicio, fin = random.choice(_HORAS)
        self.client.post("/reservas/", json={
            "laboratorio_id": 1,
            "curso":          "Carga Test",
            "fecha":          fecha,
            "hora_inicio":    inicio,
            "hora_fin":       fin,
        }, headers=self.headers, name="/reservas/ [POST]")


class AdminUser(HttpUser):
    weight    = 3
    wait_time = between(1, 3)

    def on_start(self):
        resp = self.client.post("/auth/login", json={
            "email":    ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        })
        token = resp.json().get("access_token", "") if resp.status_code == 200 else ""
        self.headers = {"Authorization": f"Bearer {token}"}

    @task(2)
    def reporte_uso(self):
        self.client.get("/reportes/uso-laboratorio", headers=self.headers)

    @task(2)
    def reporte_docente(self):
        self.client.get("/reportes/por-docente", headers=self.headers)

    @task(1)
    def listar_usuarios(self):
        self.client.get("/usuarios", headers=self.headers)

    @task(1)
    def reporte_ocupacion(self):
        self.client.get("/reportes/ocupacion-mensual?mes=1&anio=2024", headers=self.headers)


# Carga normal:
#   locust -f locustfile.py --headless -u 50 -r 5 -t 2m --host=http://localhost:8000
#
# Criterio de éxito: p95 < 500ms, error rate < 1%
#
# Variables de entorno opcionales (tienen defaults de prueba):
#   LOAD_ADMIN_EMAIL, LOAD_ADMIN_PASSWORD
#   LOAD_DOCENTE_EMAIL, LOAD_DOCENTE_PASSWORD
