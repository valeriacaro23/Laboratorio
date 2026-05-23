from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.horario_schema import HorarioCreate, HorarioUpdate, BloqueoCreate
from app.models.horario import HorarioLaboratorio
from app.models.laboratorio import Laboratorio
import app.repositories.horario_repository as horario_repo


def _obtener_laboratorio_activo(db: Session, laboratorio_id: int) -> Laboratorio:
    lab = db.query(Laboratorio).filter(
        Laboratorio.laboratorio_id == laboratorio_id
    ).first()
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Laboratorio con ID {laboratorio_id} no existe"
        )
    if not lab.estado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El laboratorio '{lab.nombre}' está inactivo"
        )
    return lab


def _obtener_horario_o_404(db: Session, horario_id: int) -> HorarioLaboratorio:
    horario = horario_repo.obtener_por_id(db, horario_id)
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario con ID {horario_id} no encontrado"
        )
    return horario


def crear_horario(db: Session, datos: HorarioCreate) -> HorarioLaboratorio:
    _obtener_laboratorio_activo(db, datos.laboratorio_id)
    dias = {1:"Lunes", 2:"Martes", 3:"Miércoles",
            4:"Jueves", 5:"Viernes", 6:"Sábado", 7:"Domingo"}
    if horario_repo.existe_horario_mismo_dia(db, datos.laboratorio_id, datos.dia_semana):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un horario para ese laboratorio el día {dias[datos.dia_semana]}"
        )
    return horario_repo.crear_horario(db, datos.model_dump())


def listar_horarios_laboratorio(db: Session, laboratorio_id: int) -> list[HorarioLaboratorio]:
    _obtener_laboratorio_activo(db, laboratorio_id)
    return horario_repo.listar_por_laboratorio(db, laboratorio_id)


def obtener_horario(db: Session, horario_id: int) -> HorarioLaboratorio:
    return _obtener_horario_o_404(db, horario_id)


def actualizar_horario(db: Session, horario_id: int, datos: HorarioUpdate) -> HorarioLaboratorio:
    horario = _obtener_horario_o_404(db, horario_id)
    dias = {1:"Lunes", 2:"Martes", 3:"Miércoles",
            4:"Jueves", 5:"Viernes", 6:"Sábado", 7:"Domingo"}
    if datos.dia_semana and datos.dia_semana != horario.dia_semana and horario_repo.existe_horario_mismo_dia(
        db, horario.laboratorio_id, datos.dia_semana, excluir_id=horario_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un horario para el día {dias[datos.dia_semana]}"
        )
    datos_actualizar = {k: v for k, v in datos.model_dump().items() if v is not None}
    return horario_repo.actualizar_horario(db, horario, datos_actualizar)


def bloquear_fecha(db: Session, horario_id: int, datos: BloqueoCreate) -> HorarioLaboratorio:
    horario = _obtener_horario_o_404(db, horario_id)
    if not horario.disponible and horario.fecha_bloqueo == datos.fecha_bloqueo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Este horario ya está bloqueado para la fecha {datos.fecha_bloqueo}"
        )
    return horario_repo.bloquear_fecha(db, horario, datos.fecha_bloqueo, datos.motivo_bloqueo)


def desbloquear_horario(db: Session, horario_id: int) -> HorarioLaboratorio:
    horario = _obtener_horario_o_404(db, horario_id)
    if horario.disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El horario ya está disponible"
        )
    return horario_repo.desbloquear_horario(db, horario)
