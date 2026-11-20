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

        #   Listas internas del módulo de reservas de sala (sin base de datos)
        self.salas = [
            Reservar_sala("Sala Ejecutiva", 40000, 10),
            Reservar_sala("Sala de Juntas", 60000, 20),
            Reservar_sala("Sala Creativa", 30000, 6),
        ]
        self.reservas = []  # cada elemento es una tupla (Reserva, Reservar_sala)

        #Columnas para la distribución de los frames principales (No se estan usando)
        # self.ventana_inicio.columnconfigure(0, weight=1)
        # self.ventana_inicio.columnconfigure(1, weight=1)
        # self.ventana_inicio.columnconfigure(2, weight=1)

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

        #Titulo del frame de reservas
        #self.titulo.reserva_sala = tk.Label(self.frame_reservas, text="Reservar sala", font=("Times new roman", 15), bg="#B8AEAE")
        #self.titulo.reserva_sala.pack(side="top", fill="x")

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

            marco = self.frame_interfaz_reserva
            fuente = ("Times new roman", 12)

            # Variables ligadas a los campos de la interfaz
            var_sala = tk.StringVar()
            var_horas = tk.StringVar()
            var_costo = tk.StringVar(value="Costo estimado: -")
            var_detalle = tk.StringVar(value="")

            # Lista donde se muestran las reservas (se empaqueta al final)
            lista = tk.Listbox(marco, width=130, height=8, font=("Courier", 10), exportselection=False)

            def obtener_sala():
                # Busca en la lista interna la sala elegida en el Combobox
                for sala in self.salas:
                    if sala.nombre == var_sala.get():
                        return sala
                logger.warning("Intento de reservar sin seleccionar una sala.")
                raise ErrorValidacion("Debes seleccionar una sala.")

            def obtener_horas():
                # Convierte el texto ingresado en número; si no se puede, lanza ErrorValidacion (con encadenamiento)
                try:
                    horas = float(var_horas.get())
                    return int(horas) if horas.is_integer() else horas   # 3.0 se muestra como 3
                except ValueError as e:
                    logger.warning("Horas ingresadas no numéricas.")
                    raise ErrorValidacion("Las horas deben ser un número.") from e

            def mostrar_detalle(evento=None):
                try:
                    var_detalle.set(obtener_sala().describir_servicio())
                except ErrorValidacion:
                    var_detalle.set("")

            def refrescar_lista():
                lista.delete(0, "end")
                for reserva, sala in self.reservas:
                    total = f" | Total: ${reserva.costo_total:,.0f}" if reserva.costo_total is not None else ""
                    lista.insert("end", f"{reserva.obtener_resumen()} | {sala.nombre}{total}")

            def reserva_seleccionada():
                seleccion = lista.curselection()
                if not seleccion:
                    logger.warning("Intento de operar sin seleccionar una reserva.")
                    raise ErrorValidacion("Selecciona una reserva de la lista.")
                return self.reservas[seleccion[0]][0]

            def calcular_costo_estimado():
                try:
                    sala = obtener_sala()
                    horas = obtener_horas()
                    var_costo.set(f"Costo estimado: ${sala.calcular_costo(horas):,.0f}")
                except ErrorValidacion as e:
                    var_costo.set("Costo estimado: -")
                    messagebox.showerror("Error de validación", str(e))

            def reservar():
                # Crea la reserva y la deja confirmada (try/except/else/finally)
                try:
                    if self.cliente_activo is None:
                        logger.warning("Intento de reservar sala sin sesión iniciada.")
                        raise ErrorValidacion("Debes iniciar sesión antes de reservar.")
                    sala = obtener_sala()
                    horas = obtener_horas()
                    sala.validar_parametro(horas)
                    if not sala.disponible:
                        logger.warning(f"Intento de reservar la sala no disponible: {sala.nombre}")
                        raise ErrorValidacion(f"La sala '{sala.nombre}' no está disponible.")
                    reserva = Reserva(f"RES-{len(self.reservas) + 1:03d}", self.cliente_activo, sala, horas)
                    reserva.confirmar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo reservar", str(e))
                else:
                    self.reservas.append((reserva, sala))
                    refrescar_lista()
                    messagebox.showinfo("Reserva creada", reserva.obtener_resumen())
                finally:
                    logger.info("Operación de reserva de sala finalizada.")

            def procesar_seleccionada():
                try:
                    costo = reserva_seleccionada().procesar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo procesar", str(e))
                else:
                    messagebox.showinfo("Reserva procesada", f"Total a pagar: ${costo:,.0f}")
                finally:
                    refrescar_lista()

            def cancelar_seleccionada():
                try:
                    reserva_seleccionada().cancelar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo cancelar", str(e))
                else:
                    messagebox.showinfo("Reserva cancelada", "La reserva fue cancelada correctamente.")
                finally:
                    refrescar_lista()

            # Widgets del formulario
            texto_cliente = (f"Cliente activo: {self.cliente_activo.nombre}" if self.cliente_activo
                             else "Sin sesión iniciada: vuelve al menú e inicia sesión para reservar")
            tk.Label(marco, text=texto_cliente, font=fuente, bg="#12BCFF").pack(pady=5)

            tk.Label(marco, text="Sala:", font=fuente, bg="#12BCFF").pack()
            combo_sala = ttk.Combobox(marco, textvariable=var_sala, state="readonly", width=40,
                                      values=[sala.nombre for sala in self.salas])
            combo_sala.pack()
            combo_sala.bind("<<ComboboxSelected>>", mostrar_detalle)
            tk.Label(marco, textvariable=var_detalle, font=fuente, bg="#12BCFF").pack(pady=3)

            tk.Label(marco, text="Horas (1 a 12):", font=fuente, bg="#12BCFF").pack()
            tk.Entry(marco, textvariable=var_horas, font=fuente, width=10).pack()
            tk.Label(marco, textvariable=var_costo, font=fuente, bg="#12BCFF").pack(pady=3)

            botones = tk.Frame(marco, bg="#12BCFF")
            botones.pack(pady=8)
            tk.Button(botones, text="Calcular costo", font=fuente, command=calcular_costo_estimado).pack(side="left", padx=5)
            tk.Button(botones, text="Reservar", font=fuente, bg="#2F4371", fg="#FFFFFF", command=reservar).pack(side="left", padx=5)
            tk.Button(botones, text="Procesar seleccionada", font=fuente, command=procesar_seleccionada).pack(side="left", padx=5)
            tk.Button(botones, text="Cancelar seleccionada", font=fuente, command=cancelar_seleccionada).pack(side="left", padx=5)

            tk.Label(marco, text="Mis reservas (selecciona una para procesarla o cancelarla):", font=fuente, bg="#12BCFF").pack()
            lista.pack(padx=10, pady=5)
            refrescar_lista()   # muestra las reservas hechas antes de salir y volver a entrar

        #Boton del menu principal para abrir la interfaz de reserva
        boton_reserva_sala = tk.Button(self.frame_reservas, text="Reservar sala", font=("Times new roman", 20), width=15, height=60, bg="#2F4371", fg="#FFFFFF", command=interfaz_reserva)
        boton_reserva_sala.pack(side="top", pady=200)


        #Frame de alquiler
        self.frame_alquiler = tk.Frame(self.ventana_inicio, bg="#F7F4E9")
        self.frame_alquiler.pack(fill="both", expand=True, side="left")

        #Titulo del frame de alquiler
        #self.titulo.alquiler = tk.Label(self.frame_alquiler, text="Alquilar equipo", font=("Times new roman", 15))
        #self.titulo.alquiler.pack(side="top", fill="x")
        #--- Módulo de alquiler de equipos: lista interna de equipos y de sus reservas ---
        self.equipos = [
            Alquilar_equipo("Portátil", 30000, "Cómputo"),
            Alquilar_equipo("Proyector", 25000, "Audiovisual"),
            Alquilar_equipo("Cámara profesional", 45000, "Audiovisual"),
        ]
        self.reservas_alquiler = []  # cada elemento es una tupla (Reserva, Alquilar_equipo)

        #Logica para regresar al menú principal desde alquiler de equipos
        def volver_inicio_alquiler():
            logger.info("El usuario regresó al menú principal desde alquiler de equipos.")
            self.frame_interfaz_alquiler.destroy()
            self.titulo.pack(side="top", fill="both")
            self.frame_reservas.pack(fill="both", expand=True, side="left")
            self.frame_alquiler.pack(fill="both", expand=True, side="left")
            self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #Interfaz del modulo de alquiler de equipos
        def interfaz_alquiler():
            logger.info("El usuario ingresó al módulo de alquiler de equipos.")
            self.titulo.pack_forget()
            self.frame_reservas.pack_forget()
            self.frame_alquiler.pack_forget()
            self.frame_asesoria.pack_forget()
            color = "#F5D76E"
            fuente = ("Times new roman", 12)
            self.frame_interfaz_alquiler = tk.Frame(self.ventana_inicio, bg=color)
            self.frame_interfaz_alquiler.pack(fill="both", expand=True)
            marco = self.frame_interfaz_alquiler
            tk.Button(marco, text="←", font=("Times new roman", 20), command=volver_inicio_alquiler).pack(side="top", anchor="nw", padx=10, pady=10)
            tk.Label(marco, text="Alquiler de equipos", font=("Times new roman", 30), bg=color).pack(side="top", fill="x")

            # Variables ligadas a los campos de la interfaz
            var_equipo = tk.StringVar()
            var_dias = tk.StringVar()
            var_costo = tk.StringVar(value="Costo estimado: -")
            var_detalle = tk.StringVar(value="")

            # Lista donde se muestran las reservas de alquiler (se empaqueta al final)
            lista = tk.Listbox(marco, width=130, height=8, font=("Courier", 10), exportselection=False)

            def obtener_equipo():
                # Busca en la lista interna el equipo elegido en el Combobox
                for equipo in self.equipos:
                    if equipo.nombre == var_equipo.get():
                        return equipo
                logger.warning("Intento de alquilar sin seleccionar un equipo.")
                raise ErrorValidacion("Debes seleccionar un equipo.")

            def obtener_dias():
                # Convierte el texto ingresado en número; si no se puede, lanza ErrorValidacion (con encadenamiento)
                try:
                    dias = float(var_dias.get())
                    return int(dias) if dias.is_integer() else dias   # 3.0 se muestra como 3
                except ValueError as e:
                    logger.warning("Días de alquiler ingresados no numéricos.")
                    raise ErrorValidacion("Los días deben ser un número.") from e

            def mostrar_detalle(evento=None):
                try:
                    var_detalle.set(obtener_equipo().describir_servicio())
                except ErrorValidacion:
                    var_detalle.set("")

            def refrescar_lista():
                lista.delete(0, "end")
                for reserva, equipo in self.reservas_alquiler:
                    total = f" | Total: ${reserva.costo_total:,.0f}" if reserva.costo_total is not None else ""
                    lista.insert("end", f"{reserva.obtener_resumen()} | {equipo.nombre}{total}")

            def reserva_seleccionada():
                seleccion = lista.curselection()
                if not seleccion:
                    logger.warning("Intento de operar sin seleccionar una reserva de alquiler.")
                    raise ErrorValidacion("Selecciona una reserva de la lista.")
                return self.reservas_alquiler[seleccion[0]][0]

            def calcular_costo_estimado():
                try:
                    equipo = obtener_equipo()
                    dias = obtener_dias()
                    var_costo.set(f"Costo estimado: ${equipo.calcular_costo(dias):,.0f}")
                except ErrorValidacion as e:
                    var_costo.set("Costo estimado: -")
                    messagebox.showerror("Error de validación", str(e))

            def reservar():
                # Crea la reserva y la deja confirmada (try/except/else/finally)
                try:
                    if self.cliente_activo is None:
                        logger.warning("Intento de alquilar un equipo sin sesión iniciada.")
                        raise ErrorValidacion("Debes iniciar sesión antes de reservar.")
                    equipo = obtener_equipo()
                    dias = obtener_dias()
                    equipo.validar_parametro(dias)
                    if not equipo.disponible:
                        logger.warning(f"Intento de alquilar un equipo no disponible: {equipo.nombre}")
                        raise ErrorValidacion(f"El equipo '{equipo.nombre}' no está disponible.")
                    reserva = Reserva(f"ALQ-{len(self.reservas_alquiler) + 1:03d}", self.cliente_activo, equipo, dias)
                    reserva.confirmar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo reservar", str(e))
                else:
                    self.reservas_alquiler.append((reserva, equipo))
                    refrescar_lista()
                    messagebox.showinfo("Reserva creada", reserva.obtener_resumen())
                finally:
                    logger.info("Operación de alquiler de equipo finalizada.")

            def procesar_seleccionada():
                try:
                    costo = reserva_seleccionada().procesar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo procesar", str(e))
                else:
                    messagebox.showinfo("Reserva procesada", f"Total a pagar: ${costo:,.0f}")
                finally:
                    refrescar_lista()

            def cancelar_seleccionada():
                try:
                    reserva_seleccionada().cancelar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo cancelar", str(e))
                else:
                    messagebox.showinfo("Reserva cancelada", "La reserva fue cancelada correctamente.")
                finally:
                    refrescar_lista()

            # Widgets del formulario
            texto_cliente = (f"Cliente activo: {self.cliente_activo.nombre}" if self.cliente_activo
                             else "Sin sesión iniciada: vuelve al menú e inicia sesión para reservar")
            tk.Label(marco, text=texto_cliente, font=fuente, bg=color).pack(pady=5)

            tk.Label(marco, text="Equipo:", font=fuente, bg=color).pack()
            combo = ttk.Combobox(marco, textvariable=var_equipo, state="readonly", width=40,
                                 values=[equipo.nombre for equipo in self.equipos])
            combo.pack()
            combo.bind("<<ComboboxSelected>>", mostrar_detalle)
            tk.Label(marco, textvariable=var_detalle, font=fuente, bg=color).pack(pady=3)

            tk.Label(marco, text="Días (1 a 30):", font=fuente, bg=color).pack()
            tk.Entry(marco, textvariable=var_dias, font=fuente, width=10).pack()
            tk.Label(marco, textvariable=var_costo, font=fuente, bg=color).pack(pady=3)

            botones = tk.Frame(marco, bg=color)
            botones.pack(pady=8)
            tk.Button(botones, text="Calcular costo", font=fuente, command=calcular_costo_estimado).pack(side="left", padx=5)
            tk.Button(botones, text="Alquilar", font=fuente, bg="#2F4371", fg="#FFFFFF", command=reservar).pack(side="left", padx=5)
            tk.Button(botones, text="Procesar seleccionada", font=fuente, command=procesar_seleccionada).pack(side="left", padx=5)
            tk.Button(botones, text="Cancelar seleccionada", font=fuente, command=cancelar_seleccionada).pack(side="left", padx=5)

            tk.Label(marco, text="Mis alquileres (selecciona una para procesarla o cancelarla):", font=fuente, bg=color).pack()
            lista.pack(padx=10, pady=5)
            refrescar_lista()   # muestra las reservas hechas antes de salir y volver a entrar


        boton_alquiler= tk.Button(self.frame_alquiler, text= "Alquilar equipo", font= ("times new roman", 20), width=15, height=60, bg="#FFBB0C", command=interfaz_alquiler) 
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

        #Logica para regresar al menú principal desde la asesoría
        def volver_inicio_asesoria():
            logger.info("El usuario regresó al menú principal desde asesoría.")
            self.frame_interfaz_asesoria.destroy()
            self.titulo.pack(side="top", fill="both")
            self.frame_reservas.pack(fill="both", expand=True, side="left")
            self.frame_alquiler.pack(fill="both", expand=True, side="left")
            self.frame_asesoria.pack(fill="both", expand=True, side="left")

        #Interfaz del modulo de asesoría especializada
        def interfaz_asesoria():
            logger.info("El usuario ingresó al módulo de asesoría especializada.")
            self.titulo.pack_forget()
            self.frame_reservas.pack_forget()
            self.frame_alquiler.pack_forget()
            self.frame_asesoria.pack_forget()
            color = "#8FD694"
            fuente = ("Times new roman", 12)
            self.frame_interfaz_asesoria = tk.Frame(self.ventana_inicio, bg=color)
            self.frame_interfaz_asesoria.pack(fill="both", expand=True)
            marco = self.frame_interfaz_asesoria
            tk.Button(marco, text="←", font=("Times new roman", 20), command=volver_inicio_asesoria).pack(side="top", anchor="nw", padx=10, pady=10)
            tk.Label(marco, text="Asesoría especializada", font=("Times new roman", 30), bg=color).pack(side="top", fill="x")

            # Variables ligadas a los campos de la interfaz
            var_asesoria = tk.StringVar()
            var_horas = tk.StringVar()
            var_costo = tk.StringVar(value="Costo estimado: -")
            var_detalle = tk.StringVar(value="")

            # Lista donde se muestran las reservas de asesoría (se empaqueta al final)
            lista = tk.Listbox(marco, width=130, height=8, font=("Courier", 10), exportselection=False)

            def obtener_asesoria():
                # Busca en la lista interna la asesoría elegida en el Combobox
                for asesoria in self.asesorias:
                    if asesoria.nombre == var_asesoria.get():
                        return asesoria
                logger.warning("Intento de reservar sin seleccionar una asesoría.")
                raise ErrorValidacion("Debes seleccionar una asesoría.")

            def obtener_horas():
                # Convierte el texto ingresado en número; si no se puede, lanza ErrorValidacion (con encadenamiento)
                try:
                    horas = float(var_horas.get())
                    return int(horas) if horas.is_integer() else horas   # 3.0 se muestra como 3
                except ValueError as e:
                    logger.warning("Horas de asesoría ingresadas no numéricas.")
                    raise ErrorValidacion("Las horas deben ser un número.") from e

            def mostrar_detalle(evento=None):
                try:
                    var_detalle.set(obtener_asesoria().describir_servicio())
                except ErrorValidacion:
                    var_detalle.set("")

            def refrescar_lista():
                lista.delete(0, "end")
                for reserva, asesoria in self.reservas_asesoria:
                    total = f" | Total: ${reserva.costo_total:,.0f}" if reserva.costo_total is not None else ""
                    lista.insert("end", f"{reserva.obtener_resumen()} | {asesoria.nombre}{total}")

            def reserva_seleccionada():
                seleccion = lista.curselection()
                if not seleccion:
                    logger.warning("Intento de operar sin seleccionar una reserva de asesoría.")
                    raise ErrorValidacion("Selecciona una reserva de la lista.")
                return self.reservas_asesoria[seleccion[0]][0]

            def calcular_costo_estimado():
                try:
                    asesoria = obtener_asesoria()
                    horas = obtener_horas()
                    var_costo.set(f"Costo estimado: ${asesoria.calcular_costo(horas):,.0f}")
                except ErrorValidacion as e:
                    var_costo.set("Costo estimado: -")
                    messagebox.showerror("Error de validación", str(e))

            def reservar():
                # Crea la reserva y la deja confirmada (try/except/else/finally)
                try:
                    if self.cliente_activo is None:
                        logger.warning("Intento de reservar asesoría sin sesión iniciada.")
                        raise ErrorValidacion("Debes iniciar sesión antes de reservar.")
                    asesoria = obtener_asesoria()
                    horas = obtener_horas()
                    asesoria.validar_parametro(horas)
                    if not asesoria.disponible:
                        logger.warning(f"Intento de reservar una asesoría no disponible: {asesoria.nombre}")
                        raise ErrorValidacion(f"La asesoría '{asesoria.nombre}' no está disponible.")
                    reserva = Reserva(f"ASE-{len(self.reservas_asesoria) + 1:03d}", self.cliente_activo, asesoria, horas)
                    reserva.confirmar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo reservar", str(e))
                else:
                    self.reservas_asesoria.append((reserva, asesoria))
                    refrescar_lista()
                    messagebox.showinfo("Reserva creada", reserva.obtener_resumen())
                finally:
                    logger.info("Operación de reserva de asesoría finalizada.")

            def procesar_seleccionada():
                try:
                    costo = reserva_seleccionada().procesar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo procesar", str(e))
                else:
                    messagebox.showinfo("Reserva procesada", f"Total a pagar: ${costo:,.0f}")
                finally:
                    refrescar_lista()

            def cancelar_seleccionada():
                try:
                    reserva_seleccionada().cancelar()
                except ErrorValidacion as e:
                    messagebox.showerror("No se pudo cancelar", str(e))
                else:
                    messagebox.showinfo("Reserva cancelada", "La reserva fue cancelada correctamente.")
                finally:
                    refrescar_lista()

            # Widgets del formulario
            texto_cliente = (f"Cliente activo: {self.cliente_activo.nombre}" if self.cliente_activo
                             else "Sin sesión iniciada: vuelve al menú e inicia sesión para reservar")
            tk.Label(marco, text=texto_cliente, font=fuente, bg=color).pack(pady=5)

            tk.Label(marco, text="Asesoría:", font=fuente, bg=color).pack()
            combo = ttk.Combobox(marco, textvariable=var_asesoria, state="readonly", width=40,
                                 values=[asesoria.nombre for asesoria in self.asesorias])
            combo.pack()
            combo.bind("<<ComboboxSelected>>", mostrar_detalle)
            tk.Label(marco, textvariable=var_detalle, font=fuente, bg=color).pack(pady=3)

            tk.Label(marco, text="Horas (1 a 8):", font=fuente, bg=color).pack()
            tk.Entry(marco, textvariable=var_horas, font=fuente, width=10).pack()
            tk.Label(marco, textvariable=var_costo, font=fuente, bg=color).pack(pady=3)

            botones = tk.Frame(marco, bg=color)
            botones.pack(pady=8)
            tk.Button(botones, text="Calcular costo", font=fuente, command=calcular_costo_estimado).pack(side="left", padx=5)
            tk.Button(botones, text="Reservar", font=fuente, bg="#2F4371", fg="#FFFFFF", command=reservar).pack(side="left", padx=5)
            tk.Button(botones, text="Procesar seleccionada", font=fuente, command=procesar_seleccionada).pack(side="left", padx=5)
            tk.Button(botones, text="Cancelar seleccionada", font=fuente, command=cancelar_seleccionada).pack(side="left", padx=5)

            tk.Label(marco, text="Mis reservas de asesoría (selecciona una para procesarla o cancelarla):", font=fuente, bg=color).pack()
            lista.pack(padx=10, pady=5)
            refrescar_lista()   # muestra las reservas hechas antes de salir y volver a entrar
        #Titulo del frame de asesoria
        #self.titulo.asesoria = tk.Label(self.frame_asesoria, text="Asesoria especializada", font=("Times new roman", 15))
        #self.titulo.asesoria.pack(side="top", fill="x")

        boton_asesoria= tk.Button(self.frame_asesoria, text= "Asesoria \nespecializada", font= ("times new roman", 20), width=15, height=60, bg="#F4F7E9", command=interfaz_asesoria) 
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