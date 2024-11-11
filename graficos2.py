# Importar las librerías necesarias
import csv  # Para leer archivos CSV
from datetime import datetime  # Para manejar fechas

# Crear un diccionario vacío para almacenar los datos del CSV
data_dict = {}

# Abrir y leer el archivo CSV
with open('TP-Estructura-de-Datos/Play_Store_Data.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)  # Crear un lector CSV
    
    # Leer la primera fila que contiene los nombres de las columnas
    headers = next(csv_reader)
    
    # Crear una lista vacía para cada columna en el diccionario
    for header in headers:
        data_dict[header] = []
    
    # Leer cada fila del CSV y guardar los valores en las listas correspondientes
    for row in csv_reader:
        for i, value in enumerate(row):
            data_dict[headers[i]].append(value)


# Importar librerías para visualización
import matplotlib.pyplot as plt  # Para crear gráficos
import numpy as np  # Para operaciones numéricas

# Función para convertir strings de instalaciones a números
def convert_installs(install_str):
    if isinstance(install_str, str):  # Verificar si es string
        install_str = install_str.replace(',', '')  # Remover comas
        install_str = install_str.replace('+', '')  # Remover signo más
        if install_str.isnumeric():  # Verificar si es número
            return int(install_str)  # Convertir a entero
    return 0  # Retornar 0 si no es válido

# Obtener clasificaciones de contenido únicas (excluyendo 'Unrated')
content_ratings = sorted(list(set(data_dict['Content Rating']) - {'Unrated'}))
avg_installs = []  # Lista para almacenar promedios de instalaciones

# Calcular promedio de instalaciones para cada clasificación
for rating in content_ratings:
    # Obtener índices donde aparece esta clasificación
    indices = [i for i, x in enumerate(data_dict['Content Rating']) if x == rating]
    # Obtener número de instalaciones para estos índices
    installs = [data_dict['Installs'][i] for i in indices]
    # Convertir strings a números
    installs_num = [convert_installs(x) for x in installs]
    # Calcular promedio y convertir a millones
    avg = sum(installs_num) / len(installs_num) if installs_num else 0
    avg_installs.append(avg / 1_000_000)

# Crear gráfico de barras
plt.figure(figsize=(10, 6))  # Establecer tamaño de la figura
plt.bar(content_ratings, avg_installs)  # Crear gráfico de barras
plt.xticks(rotation=45)  # Rotar etiquetas del eje x
plt.yticks(np.arange(0, max(avg_installs)+5, 5))  # Establecer ticks del eje y
plt.xlabel('Clasificación de Contenido')  # Etiqueta eje x
plt.ylabel('Promedio de Instalaciones (Millones)')  # Etiqueta eje y
plt.title('Promedio de Instalaciones por Clasificación de Contenido')  # Título

# Formatear números en el eje y con separadores de miles
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

# Ajustar layout para evitar corte de etiquetas
plt.tight_layout()

# Mostrar el gráfico
plt.show()


# Convertir ratings a números y filtrar valores inválidos
ratings = []
for rating in data_dict['Rating']:
    try:
        rating_num = float(rating)  # Convertir a float
        if 0 <= rating_num <= 5:  # Validar rango
            ratings.append(rating_num)
    except (ValueError, TypeError):  # Ignorar valores no numéricos
        continue

# Crear histograma de ratings
plt.figure(figsize=(12, 7))  # Tamaño de la figura
plt.hist(ratings, bins=10, range=(0, 5),  # Crear histograma
         color='skyblue',  # Color de las barras
         edgecolor='black',  # Color del borde
         alpha=0.7,  # Transparencia
         rwidth=0.9)  # Ancho relativo de las barras

# Configurar título y etiquetas
plt.title('Distribución de Calificaciones en Google Play Store', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Calificación', fontsize=12)
plt.ylabel('Cantidad de Apps', fontsize=12)

# Agregar cuadrícula
plt.grid(True, alpha=0.3, linestyle='--')

# Configurar ticks del eje x
plt.xticks(np.arange(0, 5.5, 0.5), fontsize=10)

# Formatear eje y con separadores de miles
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

# Agregar texto con total de apps
total_apps = len(ratings)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes, 
         ha='right', 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# Ajustar márgenes
plt.tight_layout()

# Mostrar el gráfico
plt.show()


# Procesar fechas de actualización
dates = []
for date_str in data_dict['Last Updated']:
    try:
        # Convertir string a objeto datetime
        date = datetime.strptime(date_str, '%B %d, %Y')
        # Incluir solo fechas desde 2013
        if date.year >= 2013:
            dates.append(date)
    except:
        continue

# Crear figura para el histograma de fechas
plt.figure(figsize=(15, 8))

# Crear histograma de fechas
plt.hist(dates, bins=50, color='lightseagreen', 
         edgecolor='black', alpha=0.7)

# Configurar estilo y etiquetas
plt.title('Actualizaciones de Apps a lo Largo del Tiempo', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Fecha de Actualización', fontsize=12)
plt.ylabel('Número de Apps Actualizadas', fontsize=12)

# Rotar etiquetas del eje x
plt.xticks(rotation=45)

# Agregar cuadrícula
plt.grid(True, alpha=0.3, linestyle='--')

# Formatear eje y con separadores de miles
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

# Agregar texto con total de apps
total_apps = len(dates)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes,
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
         ha='right')

# Ajustar layout
plt.tight_layout()

# Mostrar gráfico
plt.show()


# Contar frecuencia de cada categoría
category_counts = {}
for category in data_dict['Category']:
    if category not in category_counts:
        category_counts[category] = 0
    category_counts[category] += 1

# Ordenar categorías por frecuencia y separar top 6
sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
top_6_categories = sorted_categories[:6]  # Top 6 categorías
other_categories = sorted_categories[6:]  # Resto de categorías

# Calcular total de "otras" categorías
others_count = sum(count for category, count in other_categories)

# Preparar datos para el gráfico principal
labels = [category for category, count in top_6_categories] + ['Otros']
sizes = [count for category, count in top_6_categories] + [others_count]

# Crear figura con dos subplots
fig = plt.figure(figsize=(18, 8))

# Configurar grid para los subplots
gs = plt.GridSpec(1, 3, figure=fig)

# Crear gráfico de pie principal (2/3 del espacio)
ax1 = fig.add_subplot(gs[0, :2])
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
        startangle=90, shadow=True)
ax1.set_title('Distribución de las 6 Categorías más Comunes en Play Store', 
              pad=20, fontsize=14, fontweight='bold')

# Preparar datos para el gráfico de "Otros"
total_others = sum(count for _, count in other_categories)
other_percentages = [(category, (count/total_others)*100) for category, count in other_categories]

# Agrupar categorías pequeñas
grouped_others = {'Otros (<4%)': 0}
filtered_others = []

for category, percentage in other_percentages:
    if percentage < 4:  # Agrupar categorías con menos del 4%
        grouped_others['Otros (<4%)'] += percentage
    else:
        filtered_others.append((category, percentage))

# Convertir porcentajes a valores absolutos
filtered_sizes = [count/100 * total_others for _, count in filtered_others]
filtered_labels = [category for category, _ in filtered_others]

# Agregar grupo de "otros" si existe
if grouped_others['Otros (<4%)'] > 0:
    filtered_sizes.append(grouped_others['Otros (<4%)']/100 * total_others)
    filtered_labels.append('Otros (<4%)')

# Crear gráfico de pie secundario (1/3 del espacio)
ax2 = fig.add_subplot(gs[0, 2])
ax2.pie(filtered_sizes, labels=filtered_labels, autopct='%1.1f%%', 
        startangle=90, shadow=True)
ax2.set_title('Desglose de "Otros"', 
              pad=20, fontsize=12, fontweight='bold')

# Asegurar que los gráficos sean circulares
ax1.axis('equal')
ax2.axis('equal')

# Ajustar layout
plt.tight_layout()

# Mostrar gráficos
plt.show()

# Preparar datos para análisis de ratings vs reviews
ratings = []
reviews = []

# Recolectar datos válidos
for i in range(len(data_dict['App'])):
    try:
        rating = float(data_dict['Rating'][i])  # Convertir rating a float
        review_count = int(data_dict['Reviews'][i])  # Convertir reviews a int
        if 0 <= rating <= 5:  # Validar rango de rating
            ratings.append(rating)
            reviews.append(review_count)
    except (ValueError, TypeError):
        continue

# Preparar datos para la línea de tendencia
log_reviews = np.log10(reviews)  # Calcular logaritmo de reviews
ratings_array = np.array(ratings)  # Convertir ratings a array

# Calcular línea de tendencia
coefficients = np.polyfit(log_reviews, ratings_array, 1)  # Ajuste lineal
polynomial = np.poly1d(coefficients)  # Crear función polinomial

# Crear gráfico de dispersión
plt.figure(figsize=(12, 8))
plt.scatter(reviews, ratings, 
           alpha=0.5,  # Transparencia
           color='skyblue',  # Color
           marker='x',  # Tipo de marcador
           s=50)  # Tamaño de marcadores

# Configurar escala logarítmica en eje x
plt.xscale('log')

# Crear puntos para la línea de tendencia
x_line = np.logspace(min(log_reviews), max(log_reviews), 100)
y_line = polynomial(np.log10(x_line))

# Agregar línea de tendencia
plt.plot(x_line, y_line, 'r-', 
         alpha=0.8)

# Configurar título y etiquetas
plt.title('Rating vs. Reviews', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Number of Reviews', fontsize=12)
plt.ylabel('Rating', fontsize=12)

# Configurar límites y cuadrícula
plt.ylim(1, 5.2)
plt.grid(True, alpha=0.3, linestyle='--')

# Agregar texto con total de apps
total_apps = len(ratings)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes, 
         ha='right', 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# Ajustar layout
plt.tight_layout()

# Mostrar gráfico
plt.show()