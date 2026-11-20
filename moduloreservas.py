import sys
sys.dont_write_bytecode = True

import tkinter as tk
from tkinter import messagebox, ttk   # se agrega ttk porque es necesario para el menú desplegable de salas.
from abc import ABC, abstractmethod
import re

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
        logger.info(f"Cliente creado correctamente. ID: {id_cliente}")

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            logger.warning("Intento de registrar un nombre inválido.")
            raise ErrorValidacion("El nombre debe tener al menos 3 caracteres.")
        if any(char.isdigit() for char in valor):
            logger.warning("Intento de registrar un nombre con números.")
            raise ErrorValidacion("El nombre no puede contener números.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not valor or not isinstance(valor, str) or not re.match(patron, valor.strip()):
            logger.warning("Intento de registrar un correo inválido.")
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
            logger.warning("Intento de crear reserva sin cliente válido.")
            raise ErrorValidacion("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            logger.warning("Intento de crear reserva sin servicio válido.")
            raise ErrorValidacion("La reserva requiere un servicio válido.")
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)) or duracion <= 0:
            logger.warning("Intento de crear reserva con duración inválida.")
            raise ErrorValidacion("La duración debe ser un número mayor que 0.")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "Pendiente"
        self._costo_total = None
        logger.info(f"Reserva {id_reserva} creada correctamente.")

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        # Solo se puede confirmar una reserva pendiente
        if self._estado != "Pendiente":
            logger.warning(f"Intento de confirmar reserva {self.id_entidad} " f"en estado {self._estado}.")
            raise ErrorValidacion(f"No se puede confirmar una reserva en estado {self._estado}.")
        self._estado = "Confirmada"
        logger.info(f"Reserva {self.id_entidad} confirmada correctamente.")

    def cancelar(self):
        # No se puede cancelar una reserva ya cancelada o procesada
        if self._estado in ("Cancelada", "Procesada"):
            logger.warning(f"Intento de cancelar reserva {self.id_entidad} " f"en estado {self._estado}.")
            raise ErrorValidacion(f"No se puede cancelar una reserva en estado {self._estado}.")
        self._estado = "Cancelada"
        logger.info(f"Reserva {self.id_entidad} cancelada correctamente.")

    def procesar(self):
        try:
            if self._estado != "Confirmada":
                logger.warning(f"Intento de procesar reserva {self.id_entidad} " f"sin estar confirmada.")
                raise ErrorValidacion(f"Solo se procesan reservas confirmadas (estado actual: {self._estado}).")
            costo = self._servicio.calcular_costo() * self._duracion
        except (TypeError, ValueError) as e:
            # Encadenamiento de excepciones: se conserva la causa original
            self._estado = "Fallida"
            logger.exception(f"Error al procesar reserva {self.id_entidad}.")
            raise ErrorValidacion("No se pudo calcular el costo de la reserva.") from e
        else:
            self._costo_total = costo
            self._estado = "Procesada"
            logger.info(f"Reserva {self.id_entidad} procesada correctamente. " f"Costo: {costo}")
            return costo

    def obtener_resumen(self):
        return (f"Reserva {self.id_entidad}: {self._cliente.nombre} | "
                f"duración {self._duracion} | estado {self._estado}")
# henry: coloque el modulo de reservas aca para que no quede abajo separado de las demas clases.
class Reservar_sala(Servicio):
    """Servicio especializado: reserva de salas (tarifa por hora)."""
    HORAS_MIN = 1
    HORAS_MAX = 12

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        # Validaciones estrictas de los datos de la sala
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise self._rechazar("El nombre de la sala debe tener al menos 3 caracteres.")
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise self._rechazar("La tarifa por hora debe ser un número mayor que 0.")
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise self._rechazar("La capacidad debe ser un entero mayor que 0.")
        if not isinstance(disponible, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._nombre = nombre.strip()
        self._tarifa_hora = tarifa_hora
        self._capacidad = capacidad
        self._disponible = disponible
        logger.info(f"Sala creada correctamente: {self._nombre}")

    @staticmethod
    def _rechazar(mensaje):
        # Registra la advertencia en el log y devuelve la excepción para lanzarla
        logger.warning(f"Sala: {mensaje}")
        return ErrorValidacion(mensaje)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def capacidad(self):
        return self._capacidad

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._disponible = valor

    def validar_parametro(self, horas=1):
        # La duración debe ser un número entre HORAS_MIN y HORAS_MAX
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise self._rechazar("Las horas deben ser un número.")
        if not self.HORAS_MIN <= horas <= self.HORAS_MAX:
            raise self._rechazar(f"Las horas deben estar entre {self.HORAS_MIN} y {self.HORAS_MAX}.")
        return True

    def calcular_costo(self, horas=1, impuesto=0.0, descuento=0.0):
        # Variantes (sobrecarga con parámetros opcionales):
        #   calcular_costo()               -> 1 hora   (así lo usa Reserva.procesar)
        #   calcular_costo(3)              -> 3 horas
        #   calcular_costo(3, 0.19)        -> 3 horas con 19% de impuesto
        #   calcular_costo(3, 0.19, 0.10)  -> 3 horas con impuesto y 10% de descuento
        self.validar_parametro(horas)
        for etiqueta, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not 0 <= valor <= 1:
                raise self._rechazar(f"El {etiqueta} debe ser un número entre 0 y 1.")
        total = self._tarifa_hora * horas * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise self._rechazar("El costo calculado es inconsistente.")
        return round(total, 2)

    def describir_servicio(self):
        estado = "disponible" if self._disponible else "NO disponible"
        return (f"Sala '{self._nombre}' | capacidad: {self._capacidad} personas | "
                f"${self._tarifa_hora:,.0f} por hora | {estado}")

#Ventana de inicio
class Inicio:
    def __init__(self):
        logger.info("Iniciando SOFTWARE FJ")
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("1200x700+170+50")
        self.ventana_inicio.title("Sistema Integral de Gestión de Clientes, Servicios y Reservas")
        self.ventana_inicio.resizable(False, False)

        self.cliente_activo = None

        #Titulo de la ventana principal
        self.titulo = tk.Label(self.ventana_inicio, text="SOFTWARE FJ", font=("Times new roman", 30), bg="#EFEFEF")
        self.titulo.pack(side="top", fill="both", pady=10, expand=True)

        #Ventana emergente conectada a la clase Cliente sin tocar los frames principales
        def abrir_inicio_sesion():
            ventana_login = tk.Toplevel(self.ventana_inicio)
            ventana_login.title("Iniciar Sesión")
            ventana_login.geometry("400x300+550+250")
            ventana_login.resizable(False, False)
            ventana_login.grab_set()

            tk.Label(ventana_login, text="ID Cliente:", font=("Times new roman", 12)).pack(pady=(20, 2))
            entry_id = tk.Entry(ventana_login, font=("Times new roman", 12), width=30)
            entry_id.pack(pady=2)

            tk.Label(ventana_login, text="Nombre:", font=("Times new roman", 12)).pack(pady=(10, 2))
            entry_nombre = tk.Entry(ventana_login, font=("Times new roman", 12), width=30)
            entry_nombre.pack(pady=2)

            tk.Label(ventana_login, text="Correo:", font=("Times new roman", 12)).pack(pady=(10, 2))
            entry_correo = tk.Entry(ventana_login, font=("Times new roman", 12), width=30)
            entry_correo.pack(pady=2)

            def validar_cliente():
                id_val = entry_id.get().strip()
                if not id_val:
                    logger.warning("Intento de inicio de sesión sin ID de cliente.")
                    messagebox.showerror("Error", "El ID del cliente es obligatorio.", parent=ventana_login)
                    return
                try:
                    cliente = Cliente(id_val, entry_nombre.get(), entry_correo.get())
                    self.cliente_activo = cliente
                    boton_iniciar_sesion.config(text=f"Cliente: {cliente.nombre}")
                    logger.info(f"Sesión iniciada: {cliente.obtener_resumen()}")
                    messagebox.showinfo("Éxito", f"Bienvenido(a)\n{cliente.obtener_resumen()}", parent=ventana_login)
                    ventana_login.destroy()
                except ErrorValidacion as e:
                    logger.warning(f"Error de validación de cliente: {e}")
                    messagebox.showerror("Error de Validación", str(e), parent=ventana_login)

            tk.Button(ventana_login, text="Ingresar", font=("Times new roman", 12), bg="#2F4371", fg="#FFFFFF", command=validar_cliente).pack(pady=20)

        boton_iniciar_sesion = tk.Button(self.titulo, text="Iniciar sesión", font=("Times new roman", 10), relief="groove", command=abrir_inicio_sesion)
        boton_iniciar_sesion.pack(side="right")

        #Frame de reservas
        self.frame_reservas = tk.Frame(self.ventana_inicio, bg="#FFBB0C")
        self.frame_reservas.pack(fill="both", expand=True, side="left")

        #Logica para regresar a la interfaz principal
        def volver_inicio():
            logger.info("El usuario regresó al menú principal.")
            self.frame_interfaz_reserva.destroy()   #henry: antes era pack_forget(); destroy evita acumular frames
            self.titulo.pack(side="top", fill="both")
            self.frame_reservas.pack(fill="both", expand=True, side="left")
            self.frame_alquiler.pack(fill="both", expand=True, side="left")
            self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #henry: aca esta la interfaz del modulo de reserva
        def interfaz_reserva():
            logger.info("El usuario ingresó al módulo de reservas.")
            self.titulo.pack_forget()
            self.frame_reservas.pack_forget()
            self.frame_alquiler.pack_forget()
            self.frame_asesoria.pack_forget()
            self.frame_interfaz_reserva = tk.Frame(self.ventana_inicio, bg="#12BCFF")
            self.frame_interfaz_reserva.pack(fill="both", expand=True)
            tk.Button(self.frame_interfaz_reserva, text="←", font=("Times new roman", 20), command=volver_inicio,).pack(side="top", anchor="nw", padx=10, pady=10)
            tk.Label(self.frame_interfaz_reserva, text="Reserva de sala", font=("Times new roman", 30), bg="#12BCFF",).pack(side="top", fill="x")

        # def interfaz_alquiler():
        #     logger.info("El usuario ingresó al módulo de alquiler.")
        #     self.titulo.pack_forget()
        #     self.frame_reservas.pack_forget()
        #     self.frame_alquiler.pack_forget()
        #     self.frame_asesoria.pack_forget()
        #     self.frame_interfaz_alquiler = tk.Frame(self.ventana_inicio, bg="#12BCFF")
        #     self.frame_interfaz_alquiler.pack(fill="both", expand=True)
        #     tk.Button(self.frame_interfaz_alquiler, text="←", font=("Times new roman", 20), command=volver_inicio,).pack(side="top", anchor="nw", padx=10, pady=10)
        #     tk.Label(self.frame_interfaz_alquiler, text="Alquiler de equipos", font=("Times new roman", 30), bg="#12BCFF",).pack(side="top", fill="x")

        #Boton del menu principal para abrir la interfaz de reserva
        boton_reserva_sala = tk.Button(self.frame_reservas, text="Reservar sala", font=("Times new roman", 20), width=15, height=60, bg="#2F4371", fg="#F4F7E9", command=interfaz_reserva)
        boton_reserva_sala.pack(side="top", pady=200)

        #Frame de alquiler
        self.frame_alquiler = tk.Frame(self.ventana_inicio, bg="#F7F4E9")
        self.frame_alquiler.pack(fill="both", expand=True, side="left")

        boton_alquiler= tk.Button(self.frame_alquiler, text= "Alquilar equipo", font= ("times new roman", 20), width=15, height=60, bg="#FFBB0C") #command=interfaz_alquiler 
        boton_alquiler.pack(side="top", pady=200)
        
        #Frame de asesoria
        self.frame_asesoria = tk.Frame(self.ventana_inicio, bg="#2F4371")
        self.frame_asesoria.pack(fill="both", expand=True, side="left")
        #--- Módulo de asesoría especializada: lista interna de asesorías y de sus reservas ---
        self.asesorias = [
            Asesoria_especializada("Asesoría en Python", 50000, "junior"),
            Asesoria_especializada("Arquitectura de software", 80000, "senior"),
            Asesoria_especializada("Bases de programación", 40000, "junior"),
        ]
        self.reservas_asesoria = []  # cada elemento es una tupla (Reserva, Asesoria_especializada)

        boton_asesoria= tk.Button(self.frame_asesoria, text= "Asesoria \nespecializada", font= ("times new roman", 20), width=15, height=60, bg="#F4F7E9") 
        boton_asesoria.pack(side="top", pady=200)
        


    #Mantener la ventana de inicio abierta
        self.ventana_inicio.mainloop()

class Alquilar_equipo(Servicio):
    """Servicio especializado: alquiler de equipos (tarifa por día + seguro porcentual)."""
    DIAS_MIN = 1
    DIAS_MAX = 30
    SEGURO = 0.05   # el seguro del equipo es el 5% de la tarifa diaria

    def __init__(self, nombre, tarifa_dia, categoria, disponible=True):
        # Validaciones estrictas de los datos del equipo
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise self._rechazar("El nombre del equipo debe tener al menos 3 caracteres.")
        if isinstance(tarifa_dia, bool) or not isinstance(tarifa_dia, (int, float)) or tarifa_dia <= 0:
            raise self._rechazar("La tarifa por día debe ser un número mayor que 0.")
        if not isinstance(categoria, str) or len(categoria.strip()) < 3:
            raise self._rechazar("La categoría debe tener al menos 3 caracteres.")
        if not isinstance(disponible, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._nombre = nombre.strip()
        self._tarifa_dia = tarifa_dia
        self._categoria = categoria.strip()
        self._disponible = disponible
        logger.info(f"Equipo creado correctamente: {self._nombre} ({self._categoria})")

    @staticmethod
    def _rechazar(mensaje):
        # Registra la advertencia en el log y devuelve la excepción para lanzarla
        logger.warning(f"Equipo: {mensaje}")
        return ErrorValidacion(mensaje)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_dia(self):
        return self._tarifa_dia

    @property
    def categoria(self):
        return self._categoria

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._disponible = valor

    def validar_parametro(self, dias=1):
        # La duración del alquiler debe ser un número entre DIAS_MIN y DIAS_MAX
        if isinstance(dias, bool) or not isinstance(dias, (int, float)):
            raise self._rechazar("Los días deben ser un número.")
        if not self.DIAS_MIN <= dias <= self.DIAS_MAX:
            raise self._rechazar(f"Los días deben estar entre {self.DIAS_MIN} y {self.DIAS_MAX}.")
        return True

    def calcular_costo(self, dias=1, impuesto=0.0, descuento=0.0):
        # Variantes (sobrecarga con parámetros opcionales):
        #   calcular_costo()               -> 1 día con seguro (así lo usa Reserva.procesar)
        #   calcular_costo(5)              -> 5 días
        #   calcular_costo(5, 0.19)        -> 5 días con 19% de impuesto
        #   calcular_costo(5, 0.19, 0.10)  -> 5 días con impuesto y 10% de descuento
        self.validar_parametro(dias)
        for etiqueta, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not 0 <= valor <= 1:
                raise self._rechazar(f"El {etiqueta} debe ser un número entre 0 y 1.")
        total = self._tarifa_dia * (1 + self.SEGURO) * dias * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise self._rechazar("El costo calculado es inconsistente.")
        return round(total, 2)

    def describir_servicio(self):
        estado = "disponible" if self._disponible else "NO disponible"
        return (f"Equipo '{self._nombre}' | categoría: {self._categoria} | "
                f"${self._tarifa_dia * (1 + self.SEGURO):,.0f} por día (incluye seguro) | {estado}")


class Asesoria_especializada(Servicio):
    """Servicio especializado: asesoría (tarifa por hora, con recargo según el nivel)."""
    HORAS_MIN = 1
    HORAS_MAX = 8
    NIVELES = {"junior": 1.0, "senior": 1.5}   # el nivel senior cuesta 50% más

    def __init__(self, nombre, tarifa_hora, nivel, disponible=True):
        # Validaciones estrictas de los datos de la asesoría
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise self._rechazar("El nombre de la asesoría debe tener al menos 3 caracteres.")
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise self._rechazar("La tarifa por hora debe ser un número mayor que 0.")
        if not isinstance(nivel, str) or nivel.strip().lower() not in self.NIVELES:
            raise self._rechazar("El nivel debe ser 'junior' o 'senior'.")
        if not isinstance(disponible, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._nombre = nombre.strip()
        self._tarifa_hora = tarifa_hora
        self._nivel = nivel.strip().lower()
        self._disponible = disponible
        logger.info(f"Asesoría creada correctamente: {self._nombre} ({self._nivel})")

    @staticmethod
    def _rechazar(mensaje):
        # Registra la advertencia en el log y devuelve la excepción para lanzarla
        logger.warning(f"Asesoría: {mensaje}")
        return ErrorValidacion(mensaje)

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def nivel(self):
        return self._nivel

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):
            raise self._rechazar("La disponibilidad debe ser True o False.")
        self._disponible = valor

    def validar_parametro(self, horas=1):
        # La duración debe ser un número entre HORAS_MIN y HORAS_MAX
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise self._rechazar("Las horas deben ser un número.")
        if not self.HORAS_MIN <= horas <= self.HORAS_MAX:
            raise self._rechazar(f"Las horas deben estar entre {self.HORAS_MIN} y {self.HORAS_MAX}.")
        return True

    def calcular_costo(self, horas=1, impuesto=0.0, descuento=0.0):
        # Variantes (sobrecarga con parámetros opcionales):
        #   calcular_costo()               -> 1 hora con el recargo del nivel (así lo usa Reserva.procesar)
        #   calcular_costo(3)              -> 3 horas
        #   calcular_costo(3, 0.19)        -> 3 horas con 19% de impuesto
        #   calcular_costo(3, 0.19, 0.10)  -> 3 horas con impuesto y 10% de descuento
        self.validar_parametro(horas)
        for etiqueta, valor in (("impuesto", impuesto), ("descuento", descuento)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not 0 <= valor <= 1:
                raise self._rechazar(f"El {etiqueta} debe ser un número entre 0 y 1.")
        total = self._tarifa_hora * self.NIVELES[self._nivel] * horas * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise self._rechazar("El costo calculado es inconsistente.")
        return round(total, 2)

    def describir_servicio(self):
        estado = "disponible" if self._disponible else "NO disponible"
        return (f"Asesoría '{self._nombre}' | nivel {self._nivel} | "
                f"${self._tarifa_hora * self.NIVELES[self._nivel]:,.0f} por hora | {estado}")


if __name__ == "__main__":
    Inicio()