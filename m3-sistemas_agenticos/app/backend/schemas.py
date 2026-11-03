"""Esquemas Pydantic v2 de la app de empleados."""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, field_validator

DEPARTAMENTOS_VALIDOS = [
    "Tecnología",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
]


class EmpleadoCrear(BaseModel):
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        if not (2 <= len(valor.strip()) <= 80):
            raise ValueError("El campo nombre debe tener de 2 a 80 caracteres")
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        correo = valor.strip().lower()
        if not correo.endswith("@empresa.com"):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return correo

    @field_validator("puesto")
    @classmethod
    def validar_puesto(cls, valor: str) -> str:
        if not (2 <= len(valor.strip()) <= 60):
            raise ValueError("El campo puesto debe tener de 2 a 60 caracteres")
        return valor

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS_VALIDOS:
            opciones = ", ".join(DEPARTAMENTOS_VALIDOS)
            raise ValueError(f"El campo departamento debe ser uno de: {opciones}")
        return valor

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")
        return valor


class EmpleadoSalida(BaseModel):
    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class ErrorRespuesta(BaseModel):
    detail: str
    campo: str | None = None
