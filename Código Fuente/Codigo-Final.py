import csv
import networkx as nx
import tkinter as tk
from tkinter import OptionMenu
import queue
import matplotlib.pyplot as plt
import re

# Construir Grafo Principal
def build_graph(csv_file):
    G = nx.Graph()
    with open(csv_file, encoding="utf8") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) < 10:
                continue
            restaurant_id = row[0]
            restaurant_name = row[1]
            restaurant_cuisine = row[2]
            restaurant_Latitud = row[3]
            restaurant_Longitud = row[4]
            restaurant_district = row[5]
            restaurant_stars = int(row[6])
            restaurant_min_price = int(row[7])
            restaurant_max_price = int(row[8])
            restaurant_status = row[9]
            # Omitir restaurantes clausurados
            if restaurant_status == "Clausurado":
                continue
            # Agregar el restaurante como nodo
            G.add_node(restaurant_id, name=restaurant_name)
            # Comparar las condiciones para cada nodo existente...
            for node in G.nodes:
                node_data = G.nodes[node]
                node_cuisine = node_data.get('cuisine', None)
                node_district = node_data.get('district', None)
                node_stars = node_data.get('stars', None)
                # Inicializar el peso
                weight = 4
                # Reducir el peso si se cumple la condición de tipo de comida
                if node_cuisine == restaurant_cuisine:
                    weight -= 1
                # Reducir el peso si se cumple la condición de distrito
                if node_district == restaurant_district:
                    weight -= 1
                # Reducir el peso si se cumple la condición de estrellas
                if node_stars is not None and restaurant_stars is not None and node_stars == restaurant_stars:
                    weight -= 1
                # Agregar la arista al grafo con el peso correspondiente
                if weight != 4:
                    G.add_edge(node, restaurant_id, weight=weight)
            # Actualizar los datos del nodo actual con las condiciones
            G.nodes[restaurant_id]['cuisine'] = restaurant_cuisine
            G.nodes[restaurant_id]['district'] = restaurant_district
            G.nodes[restaurant_id]['stars'] = restaurant_stars
            G.nodes[restaurant_id]['min_price'] = restaurant_min_price
    return G

# Algoritmo BFS
def bfs(graph, start_node, district, stars, cuisine):
    visited = set()
    queue = []
    queue.append((start_node, 0))
    visited.add(start_node)
    selected_restaurants = []
    while queue:
        node, min_price = queue.pop(0)
        node_data = graph.nodes[node]
        node_district = node_data.get('district', None)
        node_stars = node_data.get('stars', None)
        node_cuisine = node_data.get('cuisine', None)
        if node_district == district and node_stars == stars and node_cuisine == cuisine:
            selected_restaurants.append((node_data['name'], node_data['min_price']))
        neighbors = graph.neighbors(node)
        for neighbor in neighbors:
            if neighbor not in visited:
                neighbor_data = graph.nodes[neighbor]
                neighbor_min_price = neighbor_data.get('min_price', None)
                neighbor_min_price = min(neighbor_min_price, min_price)
                queue.append((neighbor, neighbor_min_price))
                visited.add(neighbor)
    return selected_restaurants

# Mostrar Distritos
def show_districts():
    districts = set()
    for node, node_data in graph.nodes(data=True):
        district = node_data.get('district', None)
        if district:
            districts.add(district)
    district_var.set('')
    district_menu['menu'].delete(0, 'end')
    for district in sorted(districts):
        district_menu['menu'].add_command(label=district, command=tk._setit(district_var, district))

# Mostrar Tipo de Comida
def show_cuisines():
    cuisines = set()
    for node, node_data in graph.nodes(data=True):
        cuisine = node_data.get('cuisine', None)
        if cuisine:
            cuisines.add(cuisine)
    cuisine_var.set('')
    cuisine_menu['menu'].delete(0, 'end')
    for cuisine in sorted(cuisines):
        cuisine_menu['menu'].add_command(label=cuisine, command=tk._setit(cuisine_var, cuisine))

# Mostrar Número de Entradas
def show_stars():
    stars = set()
    for node, node_data in graph.nodes(data=True):
        star_rating = node_data.get('stars', None)
        if star_rating:
            stars.add(str(star_rating))
    stars_var.set('')
    stars_menu['menu'].delete(0, 'end')
    for star in sorted(stars):
        stars_menu['menu'].add_command(label=star, command=tk._setit(stars_var, star))

# Busca Restaurantes que Cumplan la Condición
def search_restaurants():
    district = district_var.get()
    stars = int(stars_var.get())
    cuisine = cuisine_var.get()
    # Buscar Nodo que Cumpla las Características
    start_node = None
    for node, node_data in graph.nodes(data=True):
        node_district = node_data.get('district', None)
        node_stars = node_data.get('stars', None)
        node_cuisine = node_data.get('cuisine', None)
        if node_district == district and node_stars == stars and node_cuisine == cuisine:
            start_node = node
            break
    if start_node:
        selected_restaurants = bfs(graph, start_node, district, stars, cuisine)
        results = []
        for restaurant, min_price in selected_restaurants:
            result = f"Restaurante: {restaurant} - Min: {min_price}"
            results.append(result)
    else:
        results = []
    #Limpia Salida e Imprime Resultados
    results_text.delete('1.0', 'end')
    if results:
        results_text.insert('end', "\n".join(results))
    else:
        results_text.insert('end', "No se encontraron restaurantes que cumplan con las características.")

# Quita Fuera del Resultado por Precio
def quitar_fuera_de_presupuesto():
    min_price = int(min_price_entry.get())    
    results = results_text.get("1.0", 'end').strip().split("\n\n")
    filtered_results = []
    pattern = r"Restaurante: (.*?) - Min: (\d+)"
    for result in results:
        lines = result.strip().split("\n")
        for line in lines:
            match = re.search(pattern, line)
            if match:
                restaurant_name = match.group(1)
                price = int(match.group(2))
                if price < min_price:
                    filtered_results.append((restaurant_name, price))
    #Limpia Salida e Imprime Resultados
    results_text.delete("1.0", tk.END)
    if filtered_results:
        formatted_results = [f"Restaurante: {name} - Min: {price}" for name, price in filtered_results]
        results_text.insert(tk.END, "\n".join(formatted_results))
    else:
        results_text.insert(tk.END, "No se encontraron restaurantes dentro del presupuesto.")

# Actualizar Entradas
def update_options(event):
    if district_var.get() != '':
        show_cuisines()
        show_stars()

# Gráficar Grafo
def visualize_graph(graph):
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=8, edge_color='gray')
    plt.show()

# Mostrar Grafo en Ventana
def mostrar_grafo_total():
    visualize_graph(graph)

# Nombre del archivo CSV que contiene los datos
csv_file = 'restaurants.csv'

# Construir el grafo utilizando los datos del archivo CSV
graph = build_graph(csv_file)

# Crear la ventana principal
window = tk.Tk()
window.geometry("700x350")
window.title("Búsqueda de Restaurantes")
window.configure(bg="#2E2E2E")

# Crear el contenedor de los elementos
frame = tk.Frame(window)
frame.pack(pady=10)

# Campo de Entrada de Precio Mínimo
min_price_label = tk.Label(frame, text="Precio Mínimo:")
min_price_label.grid(row=1, column=1, sticky='w')
min_price_label.configure(fg="white",bg="#2E2E2E")
min_price_entry = tk.Entry(frame)
min_price_entry.grid(row=1, column=2, sticky='w')
min_price_entry.configure(fg="white",bg="#E76F51")

# Botón para Quitar Fuera del Presupuesto
quitar_presupuesto_button = tk.Button(window, text="Quitar Fuera de Presupuesto", command=quitar_fuera_de_presupuesto)
quitar_presupuesto_button.pack()
quitar_presupuesto_button.configure(fg="white",bg="#E76F51")

# Campos de Entrada de Distrito
district_label = tk.Label(frame, text="Distrito:")
district_label.grid(row=0, column=0, sticky='w')
district_label.configure(fg="white",bg="#2E2E2E")
district_var = tk.StringVar()
district_menu = OptionMenu(frame, district_var, '')
district_menu.grid(row=0, column=1, sticky='w')
district_menu.configure(fg="white",bg="#E76F51")

# Campos de Entrada de Estrellas
stars_label = tk.Label(frame, text="Estrellas:")
stars_label.grid(row=0, column=2, sticky='w')
stars_label.configure(fg="white",bg="#2E2E2E")
stars_var = tk.StringVar()
stars_menu = OptionMenu(frame, stars_var, '')
stars_menu.grid(row=0, column=3, sticky='w')
stars_menu.configure(fg="white",bg="#E76F51")

# Campos de Entrada de Tipo de Comida
cuisine_label = tk.Label(frame, text="Tipo de Comida:")
cuisine_label.grid(row=0, column=4, sticky='w')
cuisine_label.configure(fg="white",bg="#2E2E2E")
cuisine_var = tk.StringVar()
cuisine_menu = OptionMenu(frame, cuisine_var, '')
cuisine_menu.grid(row=0, column=5, sticky='w')
cuisine_menu.configure(fg="white",bg="#E76F51")

# Mostrar Barra de Opciones
show_districts()
show_cuisines()
show_stars()

# Modificar Barra de Opciones
district_var.trace('w', update_options)

# Botón de Mostrar Grafo Completo
full_graph_button = tk.Button(window, text="Mostrar Grafo Completo", command=mostrar_grafo_total)
full_graph_button.pack()
full_graph_button.configure(fg="white",bg="#E76F51")

# Botón de Búsqueda
search_button = tk.Button(window, text="Buscar Restaurantes", command=search_restaurants)
search_button.pack()
search_button.configure(fg="white",bg="#E76F51")

# Resultados
results_text = tk.Text(window, height=10, width=60)
results_text.pack(pady=10)
results_text.configure(fg="white",bg="#E76F51")

# Centrar la ventana
window.update_idletasks()
width = window.winfo_width()
height = window.winfo_height()
x = (window.winfo_screenwidth() // 2) - (width // 2)
y = (window.winfo_screenheight() // 2) - (height // 2)
window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Ejecutar la interfaz gráfica
window.mainloop()