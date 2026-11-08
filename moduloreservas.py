import tkinter as tk

class Inicio:
    def __init__(self):
        self.ventana_inicio = tk.Tk()
        self.ventana_inicio.geometry("1200x700+170+50")
        self.ventana_inicio.title("Modulo reservas")
        self.ventana_inicio.resizable(False, False)

        self.titulo = tk.Label(self.ventana_inicio, text="SOFTWARE FJ", font=("Times new roman", 30))
        self.titulo.pack(side="top", fill="both")

    def iniciar(self):
        self.ventana_inicio.mainloop()

if __name__ == "__main__":
    app = Inicio()
    app.iniciar()
