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
    avg_installs.append(avg / 1_000_000)

# Gráfico de instalaciones por clasificación
plt.figure(figsize=(10, 6))
plt.bar(content_ratings, avg_installs)
plt.xticks(rotation=45)
plt.yticks(np.arange(0, max(avg_installs)+5, 5))
plt.xlabel('Clasificación de Contenido')
plt.ylabel('Promedio de Instalaciones (Millones)')
plt.title('Promedio de Instalaciones por Clasificación de Contenido')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.tight_layout()
plt.show()

# Procesamiento de ratings - filtrar valores inválidos
ratings = []
for rating in data_dict['Rating']:
    try:
        rating_num = float(rating)
        if 0 <= rating_num <= 5:
            ratings.append(rating_num)
    except (ValueError, TypeError):
        continue

# Histograma de ratings
plt.figure(figsize=(12, 7))
plt.hist(ratings, bins=10, range=(0, 5),
         color='skyblue',
         edgecolor='black',
         alpha=0.7,
         rwidth=0.9)

plt.title('Distribución de Calificaciones en Google Play Store', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Calificación', fontsize=12)
plt.ylabel('Cantidad de Apps', fontsize=12)
plt.grid(True, alpha=0.3, linestyle='--')
plt.xticks(np.arange(0, 5.5, 0.5), fontsize=10)
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

# Info adicional en el gráfico
total_apps = len(ratings)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes, 
         ha='right', 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout()
plt.show()

# TODO: Revisar si podemos optimizar el procesamiento de fechas
dates = []
for date_str in data_dict['Last Updated']:
    try:
        date = datetime.strptime(date_str, '%B %d, %Y')
        if date.year >= 2013:  # Solo datos desde 2013 son relevantes
            dates.append(date)
    except:
        continue

# Análisis temporal de actualizaciones
plt.figure(figsize=(15, 8))
plt.hist(dates, bins=50, color='lightseagreen', 
         edgecolor='black', alpha=0.7)

plt.title('Actualizaciones de Apps a lo Largo del Tiempo', 
          pad=20, fontsize=14, fontweight='bold')
plt.xlabel('Fecha de Actualización', fontsize=12)
plt.ylabel('Número de Apps Actualizadas', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3, linestyle='--')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

total_apps = len(dates)
plt.text(0.95, 0.95, f'Total de Apps: {total_apps:,}', 
         transform=plt.gca().transAxes,
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
         ha='right')

plt.tight_layout()
plt.show()

# Análisis de categorías
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
        startangle=90, shadow=True)
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
        startangle=90, shadow=True)
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
