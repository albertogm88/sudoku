import tkinter as tk
from tkinter import messagebox
import numpy as np

def generar_sudoku():
    def crear_base():
        base = np.arange(1, 10)
        np.random.shuffle(base)
        return base

    def generar_filas(base):
        filas = [np.roll(base, shift=(i * 3 + i // 3) % 9) for i in range(9)]
        return np.array(filas)

    base = crear_base()
    matriz = generar_filas(base)

    for i in range(0, 9, 3):
        np.random.shuffle(matriz[i:i+3])

    matriz = matriz.T
    for i in range(0, 9, 3):
        np.random.shuffle(matriz[i:i+3])

    matriz = matriz.T
    return matriz

def ocultar_posiciones(sudoku, num_ocultos):
    sudoku_oculto = sudoku.astype(object)
    posiciones = [(i, j) for i in range(9) for j in range(9)]
    ocultar = np.random.choice(len(posiciones), num_ocultos, replace=False)
    for idx in ocultar:
        fila, columna = posiciones[idx]
        sudoku_oculto[fila, columna] = None
    return sudoku_oculto

# Función para validación del número introducido
def is_valid(sudoku_original, fila, columna, num):
    return sudoku_original[fila, columna] == num

def repaint(canvas, sudoku):
    canvas.delete("all")
    for fila in range(9):
        for columna in range(9):
            x1 = columna * 50
            y1 = fila * 50
            x2 = x1 + 50
            y2 = y1 + 50
            canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
            if sudoku[fila, columna] is not None:
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(sudoku[fila, columna]), font=("Arial", 20))
    for i in range(1, 3):
        canvas.create_line(i * 150, 0, i * 150, 450, width=3, fill="black")
        canvas.create_line(0, i * 150, 450, i * 150, width=3, fill="black")

def pedir_numero(canvas, sudoku, sudoku_original, fila, columna):
    def validar_numero():
        try:
            num = int(entry.get())
            if num < 1 or num > 9:
                error_label.config(text="¡Error! El número debe estar entre 1 y 9.")
                return
            if not is_valid(sudoku_original, fila, columna, num):
                error_label.config(text="¡Error! El número no es válido en esta celda.")
                return
            sudoku[fila, columna] = num
            repaint(canvas, sudoku)
            eliminar_resaltado()
            if sudoku_completo(sudoku):
                messagebox.showinfo("¡Felicidades!", "¡Has completado el Sudoku!")
                volver_seleccion_nivel()
        except ValueError:
            error_label.config(text="¡Error! Debes ingresar un número válido.")

    def eliminar_resaltado():
        top.destroy()
        if hasattr(top, 'resalte_id'):
            canvas.delete(top.resalte_id)

    top = tk.Toplevel()
    top.title(f"Ingrese un número para la celda ({fila+1}, {columna+1})")
    top.protocol("WM_DELETE_WINDOW", lambda: eliminar_resaltado())  # Para controlar el cierre

    entry_label = tk.Label(top, text="Ingrese un número (1-9):")
    entry_label.pack(pady=5)
    entry = tk.Entry(top)
    entry.pack(pady=5)
    submit_button = tk.Button(top, text="Confirmar", command=validar_numero)
    submit_button.pack(pady=5)
    error_label = tk.Label(top, text="", fg="red")
    error_label.pack(pady=5)
    entry.focus()

    top.resalte_id = marcar_temporalmente(canvas, fila, columna)

    # Deshabilitar la entrada si la celda ya tiene un valor
    if sudoku[fila, columna] is not None:
        entry.config(state=tk.DISABLED)
        submit_button.config(state=tk.DISABLED)

    top.mainloop()


def click_en_celda(event, sudoku, sudoku_original, canvas):
    columna = event.x // 50
    fila = event.y // 50
    if sudoku[fila, columna] is not None:
        messagebox.showinfo("Celda no vacía", "Esta celda ya tiene un número.")
        return  # No permitir hacer clic en celdas ocupadas
    pedir_numero(canvas, sudoku, sudoku_original, fila, columna)


def sudoku_completo(sudoku):
    if np.any(sudoku == None):
        return False
    for i in range(9):
        if len(set(sudoku[i])) != 9:
            return False
        if len(set(sudoku[:, i])) != 9:
            return False
        subcuadrícula_fila = (i // 3) * 3
        subcuadrícula_columna = (i % 3) * 3
        subcuadrícula = sudoku[subcuadrícula_fila:subcuadrícula_fila+3, subcuadrícula_columna:subcuadrícula_columna+3]
        if len(set(subcuadrícula.flatten())) != 9:
            return False
    return True

def marcar_temporalmente(canvas, fila, columna):
    x1 = columna * 50
    y1 = fila * 50
    x2 = x1 + 50
    y2 = y1 + 50
    resalte_id = canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3)
    return resalte_id

def volver_seleccion_nivel():
    global root
    root.destroy()
    crear_interfaz()

def crear_interfaz():
    # Función para devolver el número de celdas vacías según nivel, por cada nivel se ocultan 15 celdas
    def seleccionar_nivel():
        return nivel_var.get() * 15

    def iniciar_juego():
        global root
        root.destroy()
        root = tk.Tk()
        root.title("Sudoku Interactivo")
        num_ocultos = seleccionar_nivel()
        sudoku_original = generar_sudoku()
        print(sudoku_original)
        sudoku = ocultar_posiciones(sudoku_original, num_ocultos)
        canvas = tk.Canvas(root, width=450, height=450)
        canvas.pack()
        repaint(canvas, sudoku)
        canvas.bind("<Button-1>", lambda event: click_en_celda(event, sudoku, sudoku_original, canvas))
        button_volver = tk.Button(root, text="Volver a seleccionar nivel", command=volver_seleccion_nivel)
        button_volver.pack()
        root.mainloop()

    global root
    root = tk.Tk()
    root.title("Selección de Nivel Sudoku")
    nivel_var = tk.IntVar(value=2)
    nivel_widgets = [
        tk.Radiobutton(root, text="Muy Fácil", variable=nivel_var, value=1),
        tk.Radiobutton(root, text="Fácil", variable=nivel_var, value=2),
        tk.Radiobutton(root, text="Medio", variable=nivel_var, value=3),
        tk.Radiobutton(root, text="Difícil", variable=nivel_var, value=4),
        tk.Radiobutton(root, text="Experto", variable=nivel_var, value=5)
    ]
    for widget in nivel_widgets:
        widget.pack(side=tk.TOP, pady=5)
    button_iniciar = tk.Button(root, text="Iniciar Juego", command=iniciar_juego)
    button_iniciar.pack()
    root.mainloop()

crear_interfaz()
