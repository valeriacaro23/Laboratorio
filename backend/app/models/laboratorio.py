from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base


class Laboratorio(Base):
    __tablename__ = "LABORATORIO"

    laboratorio_id       = Column(Integer, primary_key=True, index=True)
    nombre               = Column(String(150), nullable=False)
    ubicacion            = Column(String(200), nullable=False)
    capacidad_maxima     = Column(Integer, nullable=False)
    tipo_laboratorio     = Column(String(50), nullable=False)
    recursos_disponibles = Column(String(500), nullable=True)
    descripcion          = Column(String(500), nullable=True)
    estado               = Column(Boolean, default=True, nullable=False)
    created_at           = Column(DateTime, server_default=func.now(), nullable=False)

    horarios = relationship("HorarioLaboratorio", back_populates="laboratorio")
    recursos = relationship("RecursoLaboratorio", back_populates="laboratorio")
    reservas = relationship("Reserva", back_populates="laboratorio")


class RecursoLaboratorio(Base):
    __tablename__ = "RECURSO_LABORATORIO"

    recurso_id     = Column(Integer, primary_key=True, index=True)
    laboratorio_id = Column(Integer, ForeignKey("LABORATORIO.laboratorio_id"), nullable=False)
    nombre_recurso = Column(String(150), nullable=False)
    cantidad       = Column(Integer, default=0, nullable=False)
    descripcion    = Column(String(300), nullable=True)

    laboratorio = relationship("Laboratorio", back_populates="recursos")
