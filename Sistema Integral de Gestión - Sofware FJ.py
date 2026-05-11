# ==================================================
# SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ
# Asignatura: Programación | Código: 213023 | UNAD
# FASE 4 - COMPONENTE PRÁCTICO
# Grupo de 5 estudiantes | Objetivo: Estabilidad, robustez, manejo de errores
# ==================================================

# ---------------------------
# IMPORTACIONES
# ---------------------------
from abc import ABC, abstractmethod  # Permite crear clases abstractas (Abstracción)
from datetime import datetime        # Manejo de fechas para las reservas
import logging                       # Herramienta para registrar errores y eventos
import re                            # Validación de formatos (correo, teléfono, etc.)

# ==================================================
# 1. DEFINICIÓN DE EXCEPCIONES PERSONALIZADAS
# Creadas para identificar y controlar cada tipo de error
# ==================================================
class ErrorSistema(Exception):
    """Excepción base: todos los errores del sistema heredan de esta clase"""
    def __init__(self, mensaje: str, codigo: int = 1000):
        self.mensaje = mensaje  # Texto explicativo del error
        self.codigo = codigo    # Código único para identificar el fallo
        super().__init__(f"[Código {codigo}] {mensaje}")


class DatoInvalidoError(ErrorSistema):
    """Se lanza cuando un dato no cumple el formato o regla establecida"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=2001)


class ParametroFaltanteError(ErrorSistema):
    """Falta información obligatoria para realizar la operación"""
    def __init__(self, campo: str):
        super().__init__(f"Falta el dato obligatorio: {campo}", codigo=2002)


class OperacionNoPermitidaError(ErrorSistema):
    """La acción solicitada no se puede hacer en el estado actual"""
    def __init__(self, accion: str):
        super().__init__(f"Operación no permitida: {accion}", codigo=3001)


class ServicioNoDisponibleError(ErrorSistema):
    """El servicio solicitado está ocupado o no existe"""
    def __init__(self, nombre_servicio: str):
        super().__init__(f"Servicio no disponible: {nombre_servicio}", codigo=3002)


class ReservaInvalidaError(ErrorSistema):
    """La reserva tiene datos inconsistentes o viola reglas de negocio"""
    def __init__(self, motivo: str):
        super().__init__(f"Reserva inválida: {motivo}", codigo=4001)

# ==================================================
# 2. CONFIGURACIÓN DEL SISTEMA DE LOGS
# Guarda todo evento y error en archivo para revisión
# ==================================================
logging.basicConfig(
    filename='errores.log',          # Nombre del archivo donde se guarda todo
    level=logging.INFO,              # Nivel: guarda desde información hasta errores graves
    format='%(asctime)s | %(levelname)s | %(message)s',  # Formato: Fecha | Tipo | Mensaje
    datefmt='%d/%m/%Y %H:%M:%S',     # Formato de fecha y hora legible
    filemode='w'                     # Sobrescribe archivo cada vez que se ejecuta
)

# ==================================================
# 3. CLASES ABSTRACTAS (PRINCIPIO: ABSTRACCIÓN)
# Definen estructura general, no se crean objetos de estas clases
# ==================================================
class EntidadBase(ABC):
    """Clase raíz: estructura común para Clientes, Servicios, etc."""
    @abstractmethod
    def validar_datos(self) -> bool:
        """Toda entidad debe saber validar su propia información"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Toda entidad debe tener una representación en texto"""
        pass


class ServicioBase(ABC):
    """Clase base para TODOS los servicios que ofrece la empresa"""
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, disponible: bool = True):
        # Atributos protegidos: accesibles solo para clases hijas
        self._id_servicio = id_servicio.strip()
        self._nombre = nombre.strip()
        self._precio_base = precio_base
        self._disponible = disponible

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """POLIMORFISMO: cada servicio calcula su precio distinto"""
        pass

    @abstractmethod
    def describir(self) -> str:
        """POLIMORFISMO: cada servicio se describe diferente"""
        pass

    def verificar_disponibilidad(self) -> bool:
        """Devuelve True si está libre, False si está ocupado"""
        return self._disponible

    def cambiar_estado(self, estado: bool):
        """Cambia entre estado LIBRE / OCUPADO"""
        self._disponible = estado

# ==================================================
# 4. CLASE CLIENTE (PRINCIPIO: ENCAPSULAMIENTO)
# Datos privados: solo se modifican/leen por métodos
# ==================================================
class Cliente(EntidadBase):
    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str):
        # ATRIBUTOS PRIVADOS: (__nombre) NO se ven ni cambian desde fuera
        self.__id_cliente = id_cliente.strip()
        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__telefono = telefono.strip()
        self.__activo = True  # Estado: cliente habilitado

        # Validación obligatoria al crear el objeto
        if not self.validar_datos():
            raise DatoInvalidoError("Los datos del cliente no cumplen el formato requerido.")

    # ---------------------------
    # MÉTODOS GETTER (Lectura controlada de datos privados)
    # ---------------------------
    @property
    def id_cliente(self): return self.__id_cliente
    @property
    def nombre(self): return self.__nombre
    @property
    def correo(self): return self.__correo
    @property
    def telefono(self): return self.__telefono
    @property
    def activo(self): return self.__activo

    # ---------------------------
    # MÉTODOS SETTER (Modificación con reglas)
    # ---------------------------
    def desactivar(self): self.__activo = False
    def activar(self): self.__activo = True

    # ---------------------------
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS
    # ---------------------------
    def validar_datos(self) -> bool:
        """Reglas estrictas: longitud mínima, formato correo, teléfono"""
        if len(self.__id_cliente) < 3: return False
        if len(self.__nombre) < 2: return False
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.__correo): return False
        if not re.match(r'^\+?\d{7,15}$', self.__telefono): return False
        return True

    def __str__(self) -> str:
        return f"👤 Cliente: {self._nombre} | ID: {self.id_cliente} | Correo: {self._correo}"

# ==================================================
# 5. SERVICIOS ESPECIALIZADOS (HERENCIA + POLIMORFISMO)
# Heredan todo de ServicioBase y redefinen comportamiento
# ==================================================
class ReservaSala(ServicioBase):
    """Servicio 1: Reserva de salas de reuniones"""
    def __init__(self, id_servicio, nombre, precio_base, capacidad: int):
        # Llamada al constructor de la clase padre (HERENCIA)
        super().__init__(id_servicio, nombre, precio_base)
        # Atributo exclusivo de este servicio
        self.__capacidad = capacidad

    # ---------------------------
    # MÉTODO SOBREESCRITO (POLIMORFISMO)
    # ---------------------------
    def calcular_costo(self, horas: float = 1, descuento: float = 0.0) -> float:
        """Cálculo: precio * horas - descuento | Parámetros opcionales = SOBRECARGA"""
        if horas <= 0: raise DatoInvalidoError("Las horas deben ser mayor a cero")
        if descuento < 0 or descuento > 1: raise DatoInvalidoError("Descuento debe estar entre 0 y 1")
        costo = self._precio_base * horas
        return round(costo * (1 - descuento), 2)

    def describir(self) -> str:
        return f"🏢 Servicio: {self.nombre} | Capacidad: {self._capacidad} pers. | Precio base: ${self._precio_base}"


class AlquilerEquipo(ServicioBase):
    """Servicio 2: Alquiler de equipos tecnológicos"""
    def __init__(self, id_servicio, nombre, precio_base, tipo_equipo: str):
        super().__init__(id_servicio, nombre, precio_base)
        self.__tipo_equipo = tipo_equipo

    # ---------------------------
    # MÉTODO SOBREESCRITO
    # ---------------------------
    def calcular_costo(self, dias: float = 1, impuesto: float = 0.16) -> float:
        """Cálculo: precio * días + impuesto"""
        if dias <= 0: raise DatoInvalidoError("Los días deben ser mayor a cero")
        costo = self._precio_base * dias
        return round(costo * (1 + impuesto), 2)

    def describir(self) -> str:
        return f"💻 Servicio: {self._nombre} | Tipo: {self.__tipo_equipo} | Precio base: ${self._precio_base}"


class AsesoriaEspecializada(ServicioBase):
    """Servicio 3: Asesoría profesional especializada"""
    def __init__(self, id_servicio, nombre, precio_base, especialista: str):
        super().__init__(id_servicio, nombre, precio_base)
        self.__especialista = especialista

    # ---------------------------
    # MÉTODO SOBREESCRITO + SOBRECARGA
    # ---------------------------
    def calcular_costo(self, horas: float = 1, urgencia: bool = False) -> float:
        """Cálculo: precio * horas + recargo si es urgente"""
        if horas <= 0: raise DatoInvalidoError("Las horas deben ser mayor a cero")
        costo = self._precio_base * horas
        if urgencia: costo *= 1.3  # Recargo del 30%
        return round(costo, 2)

    def describir(self) -> str:
        return f"👨‍🏫 Servicio: {self.nombre} | Especialista: {self._especialista} | Precio base: ${self._precio_base}"

# ==================================================
# 6. CLASE RESERVA (LÓGICA DE NEGOCIO)
# Une Cliente y Servicio, maneja estados y reglas
# ==================================================
class Reserva:
    """Gestiona todo el ciclo de vida de una reserva"""
    ESTADOS_PERMITIDOS = ["PENDIENTE", "CONFIRMADA", "CANCELADA", "FINALIZADA"]

    def __init__(self, id_reserva: str, cliente: Cliente, servicio: ServicioBase,
                 fecha: datetime, duracion: float):
        # Atributos privados
        self.__id_reserva = id_reserva.strip()
        self.__cliente = cliente
        self.__servicio = servicio
        self.__fecha = fecha
        self.__duracion = duracion
        self.__estado = "PENDIENTE"  # Estado inicial
        self.__costo_final = 0.0

        # Validaciones al crear
        if not self.__validar_datos_internos():
            raise ReservaInvalidaError("Datos inconsistentes o valores no permitidos")

        if not self.__servicio.verificar_disponibilidad():
            raise ServicioNoDisponibleError(servicio._nombre)

    def __validar_datos_internos(self) -> bool:
        """Reglas internas: no fechas pasadas, duración válida"""
        if not self.__id_reserva: return False
        if not isinstance(self.__cliente, Cliente): return False
        if not isinstance(self.__servicio, ServicioBase): return False
        if self.__duracion <= 0: return False
        if self.__fecha < datetime.now(): return False  # No se reserva en el pasado
        return True

    # ---------------------------
    # ACCIONES SOBRE LA RESERVA
    # ---------------------------
    def confirmar(self, **parametros_calculo):
        """Confirma, calcula precio y marca servicio como ocupado"""
        if self.__estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar en estado: {self.__estado}")
        self._costo_final = self._servicio.calcular_costo(**parametros_calculo)
        self.__estado = "CONFIRMADA"
        self.__servicio.cambiar_estado(False)
        logging.info(f"Reserva {self.__id_reserva} CONFIRMADA")

    def cancelar(self):
        """Cancela y libera el servicio para otros"""
        if self.__estado in ["CANCELADA", "FINALIZADA"]:
            raise OperacionNoPermitidaError(f"No se puede cancelar en estado: {self.__estado}")
        self.__estado = "CANCELADA"
        self.__servicio.cambiar_estado(True)
        logging.info(f"Reserva {self.__id_reserva} CANCELADA")

    def
