import tkinter as tk
from abc import ABC, abstractmethod

# Excepción personalizada requerida para las validaciones
class ErrorValidacion(Exception):
    pass
class Entidad(ABC):
    """Clase abstracta que representa entidades generales con identificación."""
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self):
        return self._id_entidad

    @abstractmethod
    def obtener_resumen(self):
        pass

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

#Una clase abstracta que representa entidades generales del sistema. (EN CONSTRCUCCION)
#class Entidades(ABC):
    #@abstractmethod
    
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

#Ventana de inicio
class Inicio:
    def __init__(self):
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("1200x700+170+50")
        self.ventana_inicio.title("Sistema Integral de Gestión de Clientes, Servicios y Reservas")
        self.ventana_inicio.resizable(False, False)

        #Columnas para la distribución de los frames principales (No se estan usando)
        # self.ventana_inicio.columnconfigure(0, weight=1)
        # self.ventana_inicio.columnconfigure(1, weight=1)
        # self.ventana_inicio.columnconfigure(2, weight=1)

        #Titulo de la ventana principal
        self.titulo = tk.Label(self.ventana_inicio, text="SOFTWARE FJ", font=("Times new roman", 30))
        self.titulo.pack(side="top", fill="both")

        #Frame de reservas
        self.frame_reservas = tk.Frame(self.ventana_inicio, bg="#DDC721")
        self.frame_reservas.pack(fill="both", expand=True, side="left")

        #Frame de alquiler
        self.frame_alquiler = tk.Frame(self.ventana_inicio, bg="#16C63C")
        self.frame_alquiler.pack(fill="both", expand=True, side="left")

        #Frame de asesoria
        self.frame_asesoria = tk.Frame(self.ventana_inicio, bg="#154FCC")
        self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #Titulo del frame de reservas
        self.titulo.reserva_sala = tk.Label(self.frame_reservas, text="Reservar sala", font=("Times new roman", 15))
        self.titulo.reserva_sala.pack(side="top", fill="x")

        #Titulo del frame de alquiler
        self.titulo.alquiler = tk.Label(self.frame_alquiler, text="Alquilar equipo", font=("Times new roman", 15))
        self.titulo.alquiler.pack(side="top", fill="x")

        #Titulo del frame de asesoria
        self.titulo.asesoria = tk.Label(self.frame_asesoria, text="Asesoria especializada", font=("Times new roman", 15))
        self.titulo.asesoria.pack(side="top", fill="x")

    #Mantener la ventana de inicio abierta
        self.ventana_inicio.mainloop()


class Reservar_sala(Servicio):
    pass

class Alquilar_equipo(Servicio):
    pass

class Asesoria_especializada(Servicio):
    pass

if __name__ == "__main__":
    Inicio()
