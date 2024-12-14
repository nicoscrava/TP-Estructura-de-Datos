# Librerías base
import csv
from datetime import datetime

# Dict para datos del CSV
data_dict = {}

# Lectura del CSV
with open('Play_Store_Data.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)
    
    # Inicializar listas vacías para cada columna
    for header in headers:
        data_dict[header] = []
    
    # Poblar el diccionario
    for row in csv_reader:
        for i, value in enumerate(row):
            data_dict[headers[i]].append(value)

# Librerías para gráficos
import matplotlib.pyplot as plt
import numpy as np

# Función helper para limpiar datos de instalaciones
def convert_installs(install_str):
    if isinstance(install_str, str):
        install_str = install_str.replace(',', '').replace('+', '')
        return int(install_str) if install_str.isnumeric() else 0
    return 0

# Análisis por clasificación de contenido
content_ratings = sorted(list(set(data_dict['Content Rating']) - {'Unrated'}))
avg_installs = []

for rating in content_ratings:
    indices = [i for i, x in enumerate(data_dict['Content Rating']) if x == rating]
    installs = [data_dict['Installs'][i] for i in indices]
    installs_num = [convert_installs(x) for x in installs]
    avg = sum(installs_num) / len(installs_num) if installs_num else 0
    avg_installs.append((rating, avg / 1_000_000))  # Guardar también la clasificación

# Obtener las dos clasificaciones con mayor promedio de instalaciones
top_2_content_ratings = sorted(avg_installs, key=lambda x: x[1], reverse=True)[:2]
top_2_ratings = [x[0] for x in top_2_content_ratings]

# Gráfico de instalaciones por clasificación
plt.figure(figsize=(10, 6))
plt.bar(content_ratings, [x[1] for x in avg_installs])  # Usar solo los promedios
plt.xticks(rotation=45)
plt.yticks(np.arange(0, max(avg_installs, key=lambda x: x[1])[1]+5, 5))
plt.xlabel('Clasificación de Contenido')
plt.ylabel('Promedio de Instalaciones (Millones)')
plt.title('Promedio de Instalaciones por Clasificación de Contenido')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.tight_layout()
plt.show()

# Filtrar ratings para las dos clasificaciones principales
ratings_filtered = {top_2_ratings[0]: [], top_2_ratings[1]: []}  # Usar un diccionario para almacenar ratings por categoría
for i in range(len(data_dict['Content Rating'])):
    if data_dict['Content Rating'][i] in top_2_ratings:
        try:
            rating_num = float(data_dict['Rating'][i])
            if 0 <= rating_num <= 5:
                ratings_filtered[data_dict['Content Rating'][i]].append(rating_num)
        except (ValueError, TypeError):
            continue

# Histograma de ratings filtrados
plt.figure(figsize=(12, 7))

# Graficar cada categoría por separado usando histtype='barstacked'
plt.hist([ratings_filtered[top_2_ratings[0]], ratings_filtered[top_2_ratings[1]]], 
         bins=10, range=(0, 5),
         alpha=0.7, label=top_2_ratings, 
         edgecolor='black', rwidth=0.9, histtype='barstacked')

plt.title('Distribución de Calificaciones en las 2 Clasificaciones Principales', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Calificación', fontsize=12)
plt.ylabel('Cantidad de Apps', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(np.arange(0, 5.5, 0.5), fontsize=10)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

# Info adicional en el gráfico
total_apps_filtered = sum(len(ratings) for ratings in ratings_filtered.values())
apps_per_category = {cat: len(ratings) for cat, ratings in ratings_filtered.items()}

info_text = (f'Total de Apps: {total_apps_filtered:,}\n'
            f'{top_2_ratings[0]}: {apps_per_category[top_2_ratings[0]]:,}\n'
            f'{top_2_ratings[1]}: {apps_per_category[top_2_ratings[1]]:,}')

plt.text(0.95, 0.95, info_text,
         transform=plt.gca().transAxes,
         ha='right',
         va='top',
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.legend(title='Clasificación de Contenido')
plt.tight_layout()
plt.show()

# Funciones de utilidad para procesamiento de datos
def parse_date(date_str):
    """Convierte string de fecha a objeto datetime"""
    try:
        return datetime.strptime(date_str, '%B %d, %Y')
    except:
        return None

def parse_rating(rating_str):
    """Convierte string de rating a float"""
    try:
        rating = float(rating_str)
        return rating if 0 <= rating <= 5 else None
    except (ValueError, TypeError):
        return None

def get_valid_update_rating_pairs(data_dict):
    """Obtiene pares válidos de fecha de actualización y rating"""
    pairs = []
    for i in range(len(data_dict['Last Updated'])):
        date = parse_date(data_dict['Last Updated'][i])
        rating = parse_rating(data_dict['Rating'][i])
        
        if date and rating and date.year >= 2013:
            pairs.append((date, rating))
    return pairs

def plot_updates_vs_ratings(update_rating_pairs):
    """Genera gráfico de actualizaciones vs ratings"""
    dates, ratings = zip(*update_rating_pairs)
    
    plt.figure(figsize=(15, 8))
    
    # Scatter plot con transparencia
    plt.scatter(dates, ratings, 
               alpha=0.5,
               color='skyblue',
               marker='o',
               s=50)
    
    # Calcular y agregar línea de tendencia
    dates_num = [d.timestamp() for d in dates]
    z = np.polyfit(dates_num, ratings, 1)
    p = np.poly1d(z)
    plt.plot(dates, p(dates_num), "r--", alpha=0.8)
    
    # Configuración del gráfico
    _configure_update_rating_plot(len(update_rating_pairs))
    
    plt.show()

def _configure_update_rating_plot(total_apps):
    """Configura detalles del gráfico de actualizaciones vs ratings"""
    plt.title('Relación entre Fecha de Actualización y Rating', 
              pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Fecha de Última Actualización', fontsize=12)
    plt.ylabel('Rating', fontsize=12)
    plt.ylim(1, 5.2)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45)
    
    # Agregar información sobre total de apps
    plt.text(0.95, 0.95, 
             f'Total de Apps: {total_apps:,}', 
             transform=plt.gca().transAxes,
             ha='right',
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.tight_layout()

# Ejecución principal
def main():
    # Obtener datos válidos
    update_rating_pairs = get_valid_update_rating_pairs(data_dict)
    
    # Generar gráfico
    plot_updates_vs_ratings(update_rating_pairs)

if __name__ == "__main__":
    main()

# An��lisis de categorías
category_counts = {}
for category in data_dict['Category']:
    if category not in category_counts:
        category_counts[category] = 0
    category_counts[category] += 1

# Top 6 vs resto
sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
top_6_categories = sorted_categories[:6]
other_categories = sorted_categories[6:]
others_count = sum(count for category, count in other_categories)

# Datos para gráfico principal
labels = [category for category, count in top_6_categories] + ['Otros']
sizes = [count for category, count in top_6_categories] + [others_count]

# FIXME: Mejorar la distribución del espacio entre los gráficos
fig = plt.figure(figsize=(18, 8))
gs = plt.GridSpec(1, 3, figure=fig)

# Gráfico principal - Top 6
ax1 = fig.add_subplot(gs[0, :2])
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', 
        startangle=90)
ax1.set_title('Distribución de las 6 Categorías más Comunes en Play Store', 
              pad=20, fontsize=14, fontweight='bold')

# Desglose de "Otros"
total_others = sum(count for _, count in other_categories)
other_percentages = [(category, (count/total_others)*100) for category, count in other_categories]

# Agrupar categorías menores
grouped_others = {'Otros (<4%)': 0}
filtered_others = []

for category, percentage in other_percentages:
    if percentage < 4:
        grouped_others['Otros (<4%)'] += percentage
    else:
        filtered_others.append((category, percentage))

filtered_sizes = [count/100 * total_others for _, count in filtered_others]
filtered_labels = [category for category, _ in filtered_others]

if grouped_others['Otros (<4%)'] > 0:
    filtered_sizes.append(grouped_others['Otros (<4%)']/100 * total_others)
    filtered_labels.append('Otros (<4%)')

# Gráfico secundario - Desglose
ax2 = fig.add_subplot(gs[0, 2])
ax2.pie(filtered_sizes, labels=filtered_labels, autopct='%1.1f%%', 
        startangle=90)
ax2.set_title('Desglose de "Otros"', 
              pad=20, fontsize=12, fontweight='bold')

ax1.axis('equal')
ax2.axis('equal')
plt.tight_layout()
plt.show()

# Análisis de correlación ratings vs reviews
ratings = []
reviews = []

for i in range(len(data_dict['App'])):
    try:
        rating = float(data_dict['Rating'][i])
        review_count = int(data_dict['Reviews'][i])
        if 0 <= rating <= 5:
            ratings.append(rating)
            reviews.append(review_count)
    except (ValueError, TypeError):
        continue

# Cálculo de tendencia
log_reviews = np.log10(reviews)
ratings_array = np.array(ratings)
coefficients = np.polyfit(log_reviews, ratings_array, 1)
polynomial = np.poly1d(coefficients)

plt.figure(figsize=(12, 8))
plt.scatter(reviews, ratings, 
           alpha=0.5,
           color='skyblue',
           marker='x',
           s=50)

plt.xscale('log')

x_line = np.logspace(min(log_reviews), max(log_reviews), 100)
y_line = polynomial(np.log10(x_line))
plt.plot(x_line, y_line, 'r-', alpha=0.8)

plt.title('Rating vs. Reviews', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Number of Reviews', fontsize=12)
plt.ylabel('Rating', fontsize=12)
plt.ylim(1, 5.2)
plt.grid(True, alpha=0.3, linestyle='--')

total_apps = len(ratings)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes, 
         ha='right', 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.show()

# Filtrar aplicaciones con precio mayor a 0 y segmentar por aplicaciones gratuitas y de pago
prices = []
ratings = []
colors = []

for i in range(len(data_dict['App'])):
    try:
        price_str = data_dict['Price'][i]
        if price_str.startswith('$'):
            price = float(price_str.replace('$', ''))
            if price > 0:
                rating = float(data_dict['Rating'][i])
                if 0 <= rating <= 5:
                    prices.append(price)
                    ratings.append(rating)
                    if price == 0:
                        colors.append('blue')  # Aplicaciones gratuitas
                    else:
                        colors.append('red')  # Aplicaciones de pago
    except (ValueError, TypeError):
        continue

# Gráfico de precios vs calificaciones, segmentado por aplicaciones gratuitas y de pago
plt.figure(figsize=(12, 8))
plt.scatter(prices, ratings, alpha=0.5, color=colors, marker='o', s=50)
plt.title('Relación entre Precio y Calificación', pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Precio ($)', fontsize=12)
plt.ylabel('Calificación', fontsize=12)
plt.ylim(1, 5.2)

# Configuración del eje X
plt.xlim(0, 22)  # Ajustar el límite del eje X
xticks = list(range(0, 21, 2)) 
plt.xticks(xticks)

plt.grid(True, alpha=0.3, linestyle='--')

total_apps = len(prices)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes, 
         ha='right', 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.show()

from collections import defaultdict


# Leer el archivo CSV y procesar los datos
file_path = 'Play_Store_Data.csv'  # Asegúrate de que el archivo esté en la misma carpeta
data = defaultdict(lambda: defaultdict(int))  # Estructura para almacenar las actualizaciones

with open(file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            # Convertir la fecha de "Last Updated" al año
            last_updated = datetime.strptime(row['Last Updated'], '%B %d, %Y')
            year = last_updated.year
            
            # Obtener la categoría
            category = row['Category']
            
            # Contar actualizaciones por año y categoría
            data[year][category] += 1
        except Exception:
            continue  # Ignorar filas con errores en las fechas

# Calcular las categorías más relevantes (top 8 por total de actualizaciones)
total_updates = defaultdict(int)
for year, categories in data.items():
    for category, count in categories.items():
        total_updates[category] += count

top_categories = sorted(total_updates, key=total_updates.get, reverse=True)[:8]

# Preparar datos para graficar
years = sorted(data.keys())
category_updates = {category: [data[year].get(category, 0) for year in years] for category in top_categories}

# Graficar los datos
plt.figure(figsize=(12, 6))

for category, updates in category_updates.items():
    plt.plot(years, updates, marker='o', label=category)

# Configurar etiquetas, título y leyenda
plt.title('Tendencias de Actualización por Categoría (Top Categorías)')
plt.xlabel('Fecha')
plt.ylabel('Número de Actualizaciones')
plt.legend(title='Categoría', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()

# Mostrar el gráfico
plt.show()


# -------------- #


# Leer el archivo CSV y procesar los datos
file_path = 'Play_Store_Data.csv'  # Asegúrate de que el archivo esté en la misma carpeta
install_ranges = ['<1K', '1K-10K', '10K-100K', '100K-1M', '>1M']
data = defaultdict(lambda: {r: 0 for r in install_ranges})  # Diccionario anidado para las categorías

# Función para clasificar los rangos de instalaciones
def classify_install_range(installs):
    installs = installs.replace(',', '').replace('+', '')
    try:
        installs = int(installs)
        if installs < 1000:
            return '<1K'
        elif installs < 10000:
            return '1K-10K'
        elif installs < 100000:
            return '10K-100K'
        elif installs < 1000000:
            return '100K-1M'
        else:
            return '>1M'
    except ValueError:
        return None

# Leer el archivo CSV
with open(file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row['Category']
        installs = row['Installs']
        install_range = classify_install_range(installs)
        if install_range:
            data[category][install_range] += 1

# Filtrar las categorías más relevantes (Top 8 por total de instalaciones)
total_installs_by_category = {category: sum(ranges.values()) for category, ranges in data.items()}
top_categories = sorted(total_installs_by_category, key=total_installs_by_category.get, reverse=True)[:8]

# Preparar datos para el gráfico
categories = top_categories
ranges_data = {r: [data[category][r] for category in categories] for r in install_ranges}

# Graficar las barras apiladas
bar_width = 0.6
x = range(len(categories))

plt.figure(figsize=(10, 6))
bottom = [0] * len(categories)

for install_range in install_ranges:
    plt.bar(x, ranges_data[install_range], bar_width, label=install_range, bottom=bottom)
    bottom = [bottom[i] + ranges_data[install_range][i] for i in range(len(categories))]

# Configurar etiquetas y título
plt.xticks(x, categories, rotation=45, ha='right')
plt.title('Distribución de Instalaciones por Categoría')
plt.xlabel('Categoría')
plt.ylabel('Número de Aplicaciones')
plt.legend(title='Rango de Instalaciones', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# Mostrar el gráfico
plt.show()

# -------- #

import math

# Archivo CSV
file_path = 'Play_Store_Data.csv'

# Estructuras de datos
data = defaultdict(list)  # Almacenar filas por categoría
categories = set()        # Mantener un conjunto único de categorías

# Leer y procesar el archivo CSV
with open(file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Type'] == 'Paid':  # Solo considerar apps pagas
            try:
                # Extraer datos necesarios
                category = row['Category']
                rating = float(row['Rating']) if row['Rating'] else 0
                reviews = int(row['Reviews']) if row['Reviews'] else 0
                installs = int(row['Installs'].replace(',', '').replace('+', '')) if row['Installs'] else 0
                price = float(row['Price'].replace('$', '')) if row['Price'].startswith('$') else 0
                revenue = installs * price
                data[category].append({'Rating': rating, 'Reviews': reviews, 'Installs': installs, 'Revenue': revenue})
            except ValueError:
                continue

# Calcular rankings por métrica
ranking = defaultdict(lambda: {'Rating_Rank': 0, 'Review_Rank': 0, 'Install_Rank': 0, 'Revenue_Rank': 0, 'Total_Score': 0})

for category, entries in data.items():
    # Calcular promedios y sumas por categoría
    avg_rating = sum(entry['Rating'] for entry in entries) / len(entries)
    total_reviews = sum(entry['Reviews'] for entry in entries)
    total_installs = sum(entry['Installs'] for entry in entries)
    total_revenue = sum(entry['Revenue'] for entry in entries)
    
    # Guardar valores calculados
    ranking[category]['Rating'] = avg_rating
    ranking[category]['Reviews'] = total_reviews
    ranking[category]['Installs'] = total_installs
    ranking[category]['Revenue'] = total_revenue

# Calcular rankings globales (percentil)
categories = list(ranking.keys())
ratings = [ranking[cat]['Rating'] for cat in categories]
reviews = [ranking[cat]['Reviews'] for cat in categories]
installs = [ranking[cat]['Installs'] for cat in categories]
revenues = [ranking[cat]['Revenue'] for cat in categories]

for category in categories:
    # Percentiles por métrica
    ranking[category]['Rating_Rank'] = sorted(ratings).index(ranking[category]['Rating']) / len(ratings)
    ranking[category]['Review_Rank'] = sorted(reviews).index(ranking[category]['Reviews']) / len(reviews)
    ranking[category]['Install_Rank'] = sorted(installs).index(ranking[category]['Installs']) / len(installs)
    ranking[category]['Revenue_Rank'] = sorted(revenues).index(ranking[category]['Revenue']) / len(revenues)
    
    # Score total ponderado
    ranking[category]['Total_Score'] = (
        ranking[category]['Rating_Rank'] * 0.2 +
        ranking[category]['Review_Rank'] * 0.3 +
        ranking[category]['Install_Rank'] * 0.3 +
        ranking[category]['Revenue_Rank'] * 0.2
    ) * 100  # Normalizar a un rango de 0-100

# Seleccionar las 8 categorías con mayor score
top_categories = sorted(ranking.items(), key=lambda x: x[1]['Total_Score'], reverse=True)[:8]

# Preparar datos para graficar
# Separar categorías y sus puntajes
categories = [item[0] for item in top_categories]  # Extraer nombres de categorías
scores = [item[1]['Total_Score'] for item in top_categories]  # Extraer scores de las categorías


# Graficar
plt.figure(figsize=(12, 6))
bars = plt.bar(categories, scores, color=plt.cm.viridis(range(len(categories))))

# Etiquetas en las barras
for bar, score in zip(bars, scores):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{score:.1f}', 
             ha='center', va='bottom', fontsize=10, color='black', weight='bold')

# Configuración del gráfico
plt.title('Top 8 Categorías por Score Total\n(20% Rating, 30% Reviews, 30% Instalaciones, 20% Ingresos)', fontsize=14, weight='bold')
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.ylabel('Score Total (0-100)', fontsize=12)
plt.yticks(fontsize=10)
plt.ylim(0, max(scores) + 10)  # Ajustar el eje Y para mayor claridad
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Mostrar gráfico
plt.show()

# ---- #

price_thresholds = defaultdict(int)  # Diccionario para acumulación
thresholds = [0, 1, 2, 3, 4, 5, 6, 10]  # Definir umbrales de precios

# Leer y procesar el archivo CSV
with open(file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Type'] == 'Paid':  # Solo considerar apps pagas
            try:
                price = float(row['Price'].replace('$', '')) if row['Price'].startswith('$') else 0
                installs = int(row['Installs'].replace(',', '').replace('+', '')) if row['Installs'] else 0
            except ValueError:
                continue

            # Determinar el umbral de precio correspondiente
            for i in range(len(thresholds) - 1):
                if thresholds[i] <= price < thresholds[i + 1]:
                    price_thresholds[f"${thresholds[i]}-${thresholds[i + 1]}"] += installs
                    break
            else:
                if price >= thresholds[-1]:  # Mayor que el último umbral
                    price_thresholds[f"${thresholds[-1]}+"] += installs

# Ordenar los resultados por umbrales de precio
sorted_thresholds = sorted(price_thresholds.items(), key=lambda x: float(x[0].split('-')[0][1:].replace('+', '')))

# Separar etiquetas y valores para el gráfico
labels = [item[0] for item in sorted_thresholds]
cumulative_installs = [item[1] for item in sorted_thresholds]

# Calcular instalaciones acumulativas
cumulative_installs = [sum(cumulative_installs[:i+1]) for i in range(len(cumulative_installs))]

# Graficar
plt.figure(figsize=(10, 6))
plt.bar(labels, cumulative_installs, color='skyblue', edgecolor='black')

# Etiquetas y título
plt.title('Instalaciones Cumulativas por Umbral de Precio', fontsize=14, weight='bold')
plt.xlabel('Umbrales de Precio', fontsize=12)
plt.ylabel('Instalaciones Cumulativas', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Mostrar el gráfico
plt.tight_layout()
plt.show()

# ------ #

android_versions = defaultdict(int)

# Leer y procesar el archivo CSV
with open(file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        version = row['Android Ver'] if row['Android Ver'] else 'Unknown'
        android_versions[version] += 1

# Ordenar por cantidad de apps
sorted_versions = sorted(android_versions.items(), key=lambda x: x[1], reverse=True)

# Separar etiquetas y valores
labels = [item[0] for item in sorted_versions]
sizes = [item[1] for item in sorted_versions]

# Combinar versiones menos frecuentes en "Other"
top_n = 5  # Mostrar las 5 principales versiones
labels_combined = labels[:top_n]
sizes_combined = sizes[:top_n]
other_size = sum(sizes[top_n:])

if other_size > 0:
    labels_combined.append('Other')
    sizes_combined.append(other_size)

# Crear el gráfico de torta con diseño mejorado
plt.figure(figsize=(10, 8))
colors = plt.cm.tab20c(range(len(labels_combined)))  # Usar una paleta de colores atractiva
explode = [0.1 if label == '4.1 and up' else 0 for label in labels_combined]  # Resaltar "Other"

plt.pie(
    sizes_combined,
    labels=labels_combined,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    explode=explode,
    shadow=False,
    textprops={'fontsize': 10, 'weight': 'bold'}
)

# Configuración del título
plt.title('Distribución de Versiones Requeridas de Android', fontsize=14, weight='bold')
plt.tight_layout()

# Mostrar el gráfico
plt.show()