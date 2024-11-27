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

def process_file():
    input_file = input_file_var.get()
    output_folder = output_folder_var.get()
    cube_size = float(cube_size_var.get())

    if not os.path.isfile(input_file):
        messagebox.showerror("Error", "El archivo de entrada no es válido.")
        return

    if not os.path.isdir(output_folder):
        messagebox.showerror("Error", "La carpeta de salida no es válida.")
        return

    try:
        # Leer archivo LAS
        las = laspy.read(input_file)

        # Obtener límites del archivo LAS
        min_x, max_x = las.header.mins[0], las.header.maxs[0]
        min_y, max_y = las.header.mins[1], las.header.maxs[1]
        min_z, max_z = las.header.mins[2], las.header.maxs[2]

        # Crear una cuadrícula cúbica
        x_edges = np.arange(min_x, max_x + cube_size, cube_size)
        y_edges = np.arange(min_y, max_y + cube_size, cube_size)
        z_edges = np.arange(min_z, max_z + cube_size, cube_size)

        # Asignar puntos a cubos
        x_indices = np.digitize(las.x, x_edges) - 1
        y_indices = np.digitize(las.y, y_edges) - 1
        z_indices = np.digitize(las.z, z_edges) - 1

        unique_indices = set(zip(x_indices, y_indices, z_indices))

        for idx in unique_indices:
            cube_x, cube_y, cube_z = idx

            # Filtrar puntos para este cubo
            mask = (
                (x_indices == cube_x) &
                (y_indices == cube_y) &
                (z_indices == cube_z)
            )

            cube_points = las.points[mask]

            if len(cube_points) == 0:
                continue

            # Crear un nuevo objeto LasData para este cubo
            cube_las = laspy.LasData(las.header)
            cube_las.points = cube_points

            output_file_name = f"{os.path.splitext(os.path.basename(input_file))[0]}_{cube_x}_{cube_y}_{cube_z}.las"
            output_path = os.path.join(output_folder, output_file_name)

            cube_las.write(output_path)

        messagebox.showinfo("Éxito", "El archivo ha sido procesado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {e}")

# Configuración de la ventana principal
root = tk.Tk()
root.title("Troceador de Nube de Puntos LAS")

# Variables
input_file_var = tk.StringVar()
output_folder_var = tk.StringVar()
cube_size_var = tk.StringVar(value="1")

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

tk.Button(frame, text="Procesar", command=process_file, bg="green", fg="white").grid(row=3, column=0, columnspan=3, pady=10)

# Iniciar la aplicación
root.mainloop()
