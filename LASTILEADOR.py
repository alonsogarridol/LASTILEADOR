import tkinter as tk
from tkinter import filedialog, messagebox
import laspy
import os
import numpy as np

def select_input_file():
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo LAS",
        filetypes=[("Archivos LAS", "*.las")]
    )
    if file_path:
        input_file_var.set(file_path)
        output_folder_var.set(os.path.dirname(file_path))

def select_output_folder():
    folder_path = filedialog.askdirectory(title="Selecciona una carpeta de salida")
    if folder_path:
        output_folder_var.set(folder_path)

def get_overlap_with_unit(overlap):
    """
    Convierte el valor de solape (en metros) a la unidad más adecuada sin decimales.
    Retorna una cadena como '21dm', '35cm', '7mm', etc.
    """
    if overlap >= 1:  # Convertir a metros
        return f"{int(overlap * 10)}dm"  # Pasar a decímetros
    elif overlap >= 0.1:  # Convertir a decímetros
        return f"{int(overlap * 100)}cm"  # Pasar a centímetros
    elif overlap >= 0.01:  # Convertir a centímetros
        return f"{int(overlap * 1000)}mm"  # Pasar a milímetros
    else:  # Convertir a micrómetros para valores extremadamente pequeños
        return f"{int(overlap * 10000)}um"

def process_file():
    input_file = input_file_var.get()
    output_folder = output_folder_var.get()
    cube_size = float(cube_size_var.get())
    overlap = float(overlap_var.get())

    if not os.path.isfile(input_file):
        messagebox.showerror("Error", "El archivo de entrada no es válido.")
        return

    if not os.path.isdir(output_folder):
        messagebox.showerror("Error", "La carpeta de salida no es válida.")
        return

    try:
        # Leer archivo LAS
        las = laspy.read(input_file)

        # Redondear los límites del espacio al múltiplo más cercano del tamaño del cubo
        min_x = np.floor(las.x.min() / cube_size) * cube_size
        max_x = np.ceil(las.x.max() / cube_size) * cube_size
        min_y = np.floor(las.y.min() / cube_size) * cube_size
        max_y = np.ceil(las.y.max() / cube_size) * cube_size
        min_z = np.floor(las.z.min() / cube_size) * cube_size
        max_z = np.ceil(las.z.max() / cube_size) * cube_size

        # Crear la cuadrícula tridimensional
        x_centers = np.arange(min_x + cube_size / 2, max_x, cube_size)
        y_centers = np.arange(min_y + cube_size / 2, max_y, cube_size)
        z_centers = np.arange(min_z + cube_size / 2, max_z, cube_size)

        # Ajustar el tamaño efectivo del cubo para incluir el solape
        effective_cube_size = cube_size + 2 * overlap
        overlap_str = get_overlap_with_unit(overlap)  # Obtener solape con unidad

        # Procesar cada cubo en la cuadrícula
        for x_center in x_centers:
            for y_center in y_centers:
                for z_center in z_centers:
                    # Calcular límites del cubo con solape
                    x_min = x_center - effective_cube_size / 2
                    x_max = x_center + effective_cube_size / 2
                    y_min = y_center - effective_cube_size / 2
                    y_max = y_center + effective_cube_size / 2
                    z_min = z_center - effective_cube_size / 2
                    z_max = z_center + effective_cube_size / 2

                    # Filtrar puntos dentro del cubo con solape
                    mask = (
                        (las.x >= x_min) & (las.x < x_max) &
                        (las.y >= y_min) & (las.y < y_max) &
                        (las.z >= z_min) & (las.z < z_max)
                    )
                    cube_points = las.points[mask]

                    if len(cube_points) == 0:
                        continue

                    # Crear un nuevo archivo LAS para este cubo
                    cube_las = laspy.LasData(las.header)
                    cube_las.points = cube_points

                    # Generar el nombre del archivo de salida basado en los límites
                    x_min_int = int(np.floor(x_min))  # X mínimo redondeado
                    y_min_int = int(np.floor(y_min))  # Y mínimo redondeado
                    z_min_int = int(np.floor(z_min))  # Z mínimo redondeado
                    x_max_int = int(np.floor(x_max))  # X máximo redondeado
                    y_max_int = int(np.floor(y_max))  # Y máximo redondeado
                    z_max_int = int(np.floor(z_max))  # Z máximo redondeado

                    output_file_name = (
                        f"{os.path.splitext(os.path.basename(input_file))[0]}"
                        f"_{x_min_int}_{y_min_int}_{z_min_int}"
                        f"_{x_max_int}_{y_max_int}_{z_max_int}"
                        f"_OV{overlap_str}.las"
                    )
                    output_path = os.path.join(output_folder, output_file_name)

                    # Guardar el archivo LAS
                    cube_las.write(output_path)

        messagebox.showinfo("Éxito", "El archivo ha sido procesado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Troceador de Nube de Puntos LAS con Coordenadas Extendidas")

# Variables
input_file_var = tk.StringVar()
output_folder_var = tk.StringVar()
cube_size_var = tk.StringVar(value="1")
overlap_var = tk.StringVar(value="0")

# Widgets
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

tk.Label(frame, text="Archivo de entrada:").grid(row=0, column=0, sticky="e")
input_file_entry = tk.Entry(frame, textvariable=input_file_var, width=50)
input_file_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Seleccionar", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame, text="Carpeta de salida:").grid(row=1, column=0, sticky="e")
output_folder_entry = tk.Entry(frame, textvariable=output_folder_var, width=50)
output_folder_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="Seleccionar", command=select_output_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame, text="Tamaño del cubo (m):").grid(row=2, column=0, sticky="e")
cube_size_entry = tk.Entry(frame, textvariable=cube_size_var, width=10)
cube_size_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame, text="Solape (m):").grid(row=3, column=0, sticky="e")
overlap_entry = tk.Entry(frame, textvariable=overlap_var, width=10)
overlap_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

tk.Button(frame, text="Procesar", command=process_file, bg="green", fg="white").grid(row=4, column=0, columnspan=3, pady=10)

# Iniciar la aplicación
root.mainloop()
