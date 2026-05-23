import os
import random
import datetime
from locust import HttpUser, task, between, constant

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


class DocenteStress(HttpUser):
    weight    = 7
    wait_time = constant(0.5)

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

    @task(2)
    def crear_reserva(self):
        dias = random.randint(1, 180)
        fecha = (datetime.date.today() + datetime.timedelta(days=dias)).isoformat()
        inicio, fin = random.choice(_HORAS)
        self.client.post("/reservas/", json={
            "laboratorio_id": 1,
            "curso":          "Stress Test",
            "fecha":          fecha,
            "hora_inicio":    inicio,
            "hora_fin":       fin,
        }, headers=self.headers, name="/reservas/ [POST]")

    @task(1)
    def horarios_laboratorio(self):
        lab_id = 1
        self.client.get(f"/horarios/laboratorio/{lab_id}", headers=self.headers)


class AdminStress(HttpUser):
    weight    = 3
    wait_time = constant(0.5)

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
        mes = random.randint(1, 12)
        anio = random.choice([2024, 2025, 2026])
        self.client.get(
            f"/reportes/ocupacion-mensual?mes={mes}&anio={anio}",
            headers=self.headers,
        )

    @task(1)
    def horarios_laboratorio(self):
        lab_id = 1
        self.client.get(f"/horarios/laboratorio/{lab_id}", headers=self.headers)


# Estrés:
#   locust -f locustfile_stress.py --headless -u 200 -r 20 -t 3m --host=http://localhost:8000
#
# Criterio: el sistema degrada con gracia (no crash).
#   Error rate puede superar 1% (409 de solapamiento son esperados),
#   pero NO debe devolver 5xx sin estructura JSON.
#
# Variables de entorno opcionales (tienen defaults de prueba):
#   LOAD_ADMIN_EMAIL, LOAD_ADMIN_PASSWORD
#   LOAD_DOCENTE_EMAIL, LOAD_DOCENTE_PASSWORD
