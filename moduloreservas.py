import tkinter as tk
from abc import ABC, abstractmethod

#Una clase abstracta que representa entidades generales del sistema. (EN CONSTRCUCCION)
class ErrorValidacion(Exception):
    pass
class Entidad:
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad
    @property
    def id_entidad(self):
        return self._id_entidad
class Cliente(Entidad):
    """Clase Cliente con encapsulación de datos personales."""
    def __init__(self, id_cliente, nombre, correo):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ErrorValidacion("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise ErrorValidacion("Formato de correo electrónico inválido.")
        self._correo = valor.strip()

    def obtener_resumen(self):
        return f"Cliente: {self.nombre} (ID: {self.id_entidad}, Email: {self.correo})"
    
#Clase abstracta servicio con metodos abstractos
class Servicio(ABC):
    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametro(self):
        pass
#Clase Reserva: integra cliente, servicio, duración y estado
class Reserva(Entidad):
    def __init__(self, id_reserva, cliente, servicio, duracion):
        super().__init__(id_reserva)
        # Validaciones de los datos recibidos
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva requiere un servicio válido.")
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ErrorValidacion("La duración debe ser un número mayor que 0.")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Pendiente"
        self._costo_total = None

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        # Solo se puede confirmar una reserva pendiente
        if self._estado != "Pendiente":
            raise ErrorValidacion(f"No se puede confirmar una reserva en estado {self._estado}.")
        self._estado = "Confirmada"

    def cancelar(self):
        # No se puede cancelar una reserva ya cancelada o procesada
        if self._estado in ("Cancelada", "Procesada"):
            raise ErrorValidacion(f"No se puede cancelar una reserva en estado {self._estado}.")
        self._estado = "Cancelada"

    def procesar(self):
        try:
            if self._estado != "Confirmada":
                raise ErrorValidacion(f"Solo se procesan reservas confirmadas (estado actual: {self._estado}).")
            costo = self._servicio.calcular_costo() * self._duracion
        except (TypeError, ValueError) as e:
            # Encadenamiento de excepciones: se conserva la causa original
            self._estado = "Fallida"
            raise ErrorValidacion("No se pudo calcular el costo de la reserva.") from e
        else:
            self._costo_total = costo
            self._estado = "Procesada"
            return costo

    def obtener_resumen(self):
        return (f"Reserva {self.id_entidad}: {self._cliente.nombre} | "
                f"duración {self._duracion} | estado {self._estado}")
#Ventana de inicio
class Inicio:
    def __init__(self):
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("1200x700+170+50")
        self.ventana_inicio.title("Modulo reservas")
        self.ventana_inicio.resizable(False, False)

        self.titulo = tk.Label(self.ventana_inicio, text="SOFTWARE FJ", font=("Times new roman", 30))
        self.titulo.pack(side="top", fill="both")

    #Mantener la ventana de inicio abierta
        self.ventana_inicio.mainloop()


class Reservar_sala:
    pass

class Alquilar_equipo:
    pass

class Asesoria_especializada:
    pass

if __name__ == "__main__":
    Inicio()

