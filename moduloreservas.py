import sys
sys.dont_write_bytecode = True

import tkinter as tk
from abc import ABC, abstractmethod

# Importar el sistema de logs
from logs import logger

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
        logger.info(f"Reserva {self.id_entidad} confirmada correctamente.")

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
        logger.info("Iniciando SOFTWARE FJ")
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("1200x700+170+50")
        self.ventana_inicio.title("Sistema Integral de Gestión de Clientes, Servicios y Reservas")
        self.ventana_inicio.resizable(False, False)

        #Columnas para la distribución de los frames principales (No se estan usando)
        # self.ventana_inicio.columnconfigure(0, weight=1)
        # self.ventana_inicio.columnconfigure(1, weight=1)
        # self.ventana_inicio.columnconfigure(2, weight=1)

        #Titulo de la ventana principal
        self.titulo = tk.Label(self.ventana_inicio, text="SOFTWARE FJ", font=("Times new roman", 30), bg="#EFEFEF")
        self.titulo.pack(side="top", fill="both", pady=10, expand=True)

        boton_iniciar_sesion = tk.Button(self.titulo, text="Iniciar sesión", font=("Times new roman", 10), relief="groove")
        boton_iniciar_sesion.pack(side="right")

        #Frame de reservas
        self.frame_reservas = tk.Frame(self.ventana_inicio, bg="#FFBB0C")
        self.frame_reservas.pack(fill="both", expand=True, side="left")

        #Titulo del frame de reservas
        #self.titulo.reserva_sala = tk.Label(self.frame_reservas, text="Reservar sala", font=("Times new roman", 15), bg="#B8AEAE")
        #self.titulo.reserva_sala.pack(side="top", fill="x")

        #Logica para regresar a la interfaz principal
        def volver_inicio():
            self.frame_interfaz_reserva.pack_forget()
            self.titulo.pack(side="top", fill="both")
            self.frame_reservas.pack(fill="both", expand=True, side="left")
            self.frame_alquiler.pack(fill="both", expand=True, side="left")
            self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #Interfaz del modulo de reserva
        def interfaz_reserva():
            self.titulo.pack_forget()
            self.frame_reservas.pack_forget()
            self.frame_alquiler.pack_forget()
            self.frame_asesoria.pack_forget()
            self.frame_interfaz_reserva = tk.Frame(self.ventana_inicio, bg="#12BCFF")
            self.frame_interfaz_reserva.pack(fill="both", expand=True)
            tk.Button(self.frame_interfaz_reserva, text="←", font=("Times new roman", 20), command=volver_inicio,).pack(side="top", anchor="nw", padx=10, pady=10)
            tk.Label(self.frame_interfaz_reserva, text="Reserva de sala", font=("Times new roman", 30), bg="#12BCFF",).pack(side="top", fill="x")

        #Boton del menu principal para abrir la interfaz de reserva
        boton_reserva_sala = tk.Button(self.frame_reservas, text="Reservar sala", font=("Times new roman", 20), width=15, height=60, bg="#2F4371", fg="#FFFFFF", command=interfaz_reserva)
        boton_reserva_sala.pack(side="top", pady=200)


        #Frame de alquiler
        self.frame_alquiler = tk.Frame(self.ventana_inicio, bg="#F7F4E9")
        self.frame_alquiler.pack(fill="both", expand=True, side="left")

        #Titulo del frame de alquiler
        #self.titulo.alquiler = tk.Label(self.frame_alquiler, text="Alquilar equipo", font=("Times new roman", 15))
        #self.titulo.alquiler.pack(side="top", fill="x")

        boton_alquiler= tk.Button(self.frame_alquiler, text= "Alquilar equipo", font= ("times new roman", 20), width=15, height=60, bg="#FFBB0C") 
        boton_alquiler.pack(side="top", pady=200)
        
        #Frame de asesoria
        self.frame_asesoria = tk.Frame(self.ventana_inicio, bg="#2F4371")
        self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #Titulo del frame de asesoria
        #self.titulo.asesoria = tk.Label(self.frame_asesoria, text="Asesoria especializada", font=("Times new roman", 15))
        #self.titulo.asesoria.pack(side="top", fill="x")

        boton_asesoria= tk.Button(self.frame_asesoria, text= "Asesoria \nespecializada", font= ("times new roman", 20), width=15, height=60, bg="#F4F7E9") 
        boton_asesoria.pack(side="top", pady=200)
        


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
