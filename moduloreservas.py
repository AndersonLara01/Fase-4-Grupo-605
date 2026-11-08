import tkinter as tk
from abc import ABC, abstractmethod

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

