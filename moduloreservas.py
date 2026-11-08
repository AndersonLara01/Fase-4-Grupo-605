import tkinter as tk

class Ventana:
    def __init__(self):
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("500x500")
        self.ventana_inicio.title("Modulo reservas")

    def iniciar(self):
        self.ventana_inicio.mainloop()
        print("Intento de commit")

if __name__ == "__main__":
    app = Ventana()
    app.iniciar()
