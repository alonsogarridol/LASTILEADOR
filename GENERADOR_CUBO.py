import laspy
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os


def generar_cubo_macizo_las(tamano_cubo, resolucion, ruta_salida):
    """
    Genera un archivo LAS con un cubo macizo de puntos.

    :param tamano_cubo: Lado del cubo (en unidades arbitrarias).
    :param resolucion: Distancia entre puntos dentro del cubo.
    :param ruta_salida: Ruta donde se guardará el archivo LAS generado.
    """
    try:
        tamano_cubo = float(tamano_cubo)
        resolucion = float(resolucion)

        # Verificar si la ruta de salida es válida
        directorio_salida = os.path.dirname(ruta_salida)
        if directorio_salida and not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)

        # Generar coordenadas 3D del cubo
        x = np.arange(0, tamano_cubo, resolucion)
        y = np.arange(0, tamano_cubo, resolucion)
        z = np.arange(0, tamano_cubo, resolucion)

        # Crear la malla de puntos dentro del cubo
        xx, yy, zz = np.meshgrid(x, y, z)

        # Aplanar para obtener listas de coordenadas
        puntos_x = xx.flatten()
        puntos_y = yy.flatten()
        puntos_z = zz.flatten()

        # Crear un objeto LAS
        header = laspy.LasHeader(point_format=3, version="1.2")
        header.offsets = [0, 0, 0]
        header.scales = [resolucion, resolucion, resolucion]
        las = laspy.LasData(header)

        # Asignar coordenadas
        las.x = puntos_x
        las.y = puntos_y
        las.z = puntos_z

        # Guardar en el archivo LAS
        las.write(ruta_salida)
        messagebox.showinfo("Éxito", f"Cubo macizo generado y guardado en:\n{ruta_salida}")
    except FileNotFoundError as fnf_error:
        messagebox.showerror("Error", f"Ruta de salida inválida:\n{fnf_error}")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {str(e)}")


def seleccionar_ruta_salida(entry_ruta):
    """
    Permite al usuario seleccionar una ruta para guardar el archivo LAS.
    """
    ruta = filedialog.asksaveasfilename(
        defaultextension=".las",
        filetypes=[("Archivos LAS", "*.las"), ("Todos los archivos", "*.*")]
    )
    if ruta:
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, ruta)


def main():
    """
    Crea la interfaz gráfica con tkinter para ingresar los parámetros del cubo.
    """
    # Crear la ventana principal
    ventana = tk.Tk()
    ventana.title("Generador de Cubo en LAS")
    ventana.geometry("400x300")

    # Etiquetas y campos de entrada
    tk.Label(ventana, text="Tamaño del cubo (metros):").pack(pady=5)
    entry_tamano = tk.Entry(ventana)
    entry_tamano.pack(pady=5)

    tk.Label(ventana, text="Distancia entre puntos (metros)):").pack(pady=5)
    entry_resolucion = tk.Entry(ventana)
    entry_resolucion.pack(pady=5)

    tk.Label(ventana, text="Ruta de salida del archivo LAS:").pack(pady=5)
    frame_ruta = tk.Frame(ventana)
    frame_ruta.pack(pady=5)
    entry_ruta = tk.Entry(frame_ruta, width=30)
    entry_ruta.pack(side=tk.LEFT, padx=5)
    btn_seleccionar = tk.Button(frame_ruta, text="Seleccionar", command=lambda: seleccionar_ruta_salida(entry_ruta))
    btn_seleccionar.pack(side=tk.LEFT)

    # Botón para generar el cubo
    btn_generar = tk.Button(
        ventana,
        text="Generar Cubo",
        command=lambda: generar_cubo_macizo_las(
            entry_tamano.get(), entry_resolucion.get(), entry_ruta.get()
        )
    )
    btn_generar.pack(pady=20)

    # Iniciar el bucle principal de tkinter
    ventana.mainloop()


if __name__ == "__main__":
    main()
