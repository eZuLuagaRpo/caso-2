import os
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import seaborn as sns
import numpy as np

class PDFWithHeaderFooter(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def build(self, flowables, onFirstPage=None, onLaterPages=None, canvasmaker=canvas.Canvas):
        if onFirstPage is None:
            onFirstPage = self._header_footer
        if onLaterPages is None:
            onLaterPages = self._header_footer
        
        super().build(flowables, onFirstPage=onFirstPage, onLaterPages=onLaterPages, canvasmaker=canvasmaker)

    def _header_footer(self, canvas, doc):
        canvas.saveState()

        # Header
        logo_path = 'assets/usb.jpg'
        canvas.drawImage(logo_path, 50, 730, width=50, height=50)  # Image on the left

        header_text = f"Pruebas de Software | Reporte creado el {datetime.now().strftime('%Y-%m-%d')}"
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawRightString(550, 760, header_text)  # Right-aligned header text

        # Footer
        footer_text = "(c) Contenido confidencial, todos los derechos reservados"
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(300, 30, footer_text)  # Center-aligned footer text

        canvas.restoreState()

# Function to generate the bar chart and return a buffer
def create_bar_chart(df, y_column, title):
    plt.figure(figsize=(8, 6))
    df.plot(kind='bar', y=y_column, legend=False)
    plt.title(title)
    plt.ylabel(y_column)
    plt.xticks(rotation=90)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Histogram
def create_histogram(df, column, title, xlabel):
    plt.figure(figsize=(8, 6))
    plt.hist(df[column].dropna(), bins=30, color='skyblue', edgecolor='black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frecuencia")
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Scatter with regression line
def create_scatter_with_regression(df, x_column, y_column, title):
    plt.figure(figsize=(8, 6))
    sns.regplot(x=df[x_column], y=df[y_column], scatter_kws={"color": "blue"}, line_kws={"color": "red"})
    plt.title(title)
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Boxplot
def create_boxplot(df, column, title):
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[column], color="lightgreen")
    plt.title(title)
    plt.xlabel(column)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Convert DataFrame to ReportLab Table
def dataframe_to_table(df):
    table_data = [list(df.columns)] + df.values.tolist()
    return Table(table_data)

# Create map of bike stations
def create_map_plot(data):
    gdf_start = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['start_station_longitude'], data['start_station_latitude']))
    gdf_end = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['end_station_longitude'], data['end_station_latitude']))

    gdf_all_stations = pd.concat([gdf_start[['start_station_name', 'geometry']],
                                  gdf_end[['end_station_name', 'geometry']].rename(columns={'end_station_name': 'start_station_name'})]).drop_duplicates()
    gdf_all_stations = gdf_all_stations.set_crs(epsg=4326)

    fig, ax = plt.subplots(figsize=(10, 8))
    gdf_all_stations.plot(ax=ax, marker='o', color='red', markersize=5)
    try:
        ctx.add_basemap(ax, crs=gdf_all_stations.crs)
    except:
        print("No se pudo obtener el mapa base.")

    plt.title('Ubicación de las estaciones')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    ax.set_aspect('equal', 'box')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def report(filePath, analized_data, username):
    most_popular_routes = analized_data["most_popular_routes"]
    distance_between_routes = analized_data["distance_between_routes"]
    longest_duration_routes = analized_data["longest_duration_routes"]
    stats_table_data = analized_data["stats_table"]
    data = analized_data["data"]

    pdf_buffer = BytesIO()
    doc = PDFWithHeaderFooter(pdf_buffer, pagesize=letter, topMargin=1.5*inch, bottomMargin=1.5*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()

    report_date = datetime.now().strftime('%Y-%m-%d')
    description = f"Este reporte presenta las rutas de bicicleta más populares en el sistema de bicicletas públicas de Noruega, las distancias más largas entre estaciones, y la mayor duración promedio de rutas en base a los datos proporcionados."
    elements.append(Paragraph(description, styles['BodyText']))
    elements.append(Spacer(1, 12))
    created = f"Creado por {username} el {report_date}."
    elements.append(Paragraph(created, styles['BodyText']))
    elements.append(Spacer(1, 12))

    map_buffer = create_map_plot(data)
    elements.append(Image(map_buffer, width=500, height=400))

    elements.append(Paragraph("Most Popular Routes", styles['Heading2']))
    table_most_popular = dataframe_to_table(most_popular_routes)
    table_most_popular.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    elements.append(table_most_popular)
    buffer_most_popular = create_bar_chart(most_popular_routes, 'count', 'Most Popular Routes')
    elements.append(Image(buffer_most_popular, width=400, height=300))

    elements.append(Paragraph("Routes with the Largest Distances", styles['Heading2']))
    table_distances = dataframe_to_table(distance_between_routes)
    table_distances.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    elements.append(table_distances)
    buffer_distances = create_bar_chart(distance_between_routes, 'distance_km', 'Longest Distances Between Stations')
    elements.append(Image(buffer_distances, width=400, height=300))

    elements.append(Paragraph("Routes with the Longest Average Duration", styles['Heading2']))
    table_longest_duration = dataframe_to_table(longest_duration_routes)
    table_longest_duration.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    elements.append(table_longest_duration)
    buffer_longest_duration = create_bar_chart(longest_duration_routes, 'avg_duration', 'Longest Average Durations')
    elements.append(Image(buffer_longest_duration, width=400, height=300))

    elements.append(Paragraph("Statistical Indicators", styles['Heading2']))
    table_stats = dataframe_to_table(stats_table_data)
    table_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    elements.append(table_stats)

    # NUEVAS VISUALIZACIONES
    elements.append(Paragraph("Histogram of Trip Durations (seconds)", styles['Heading2']))
    hist_buffer = create_histogram(data, 'duration', 'Distribución de Duraciones de Viaje', 'Duración (s)')
    elements.append(Image(hist_buffer, width=400, height=300))

    elements.append(Paragraph("Scatter Plot with Regression Line: Distance vs Duration", styles['Heading2']))
    scatter_buffer = create_scatter_with_regression(data, 'distance_km', 'duration', 'Duración vs Distancia')
    elements.append(Image(scatter_buffer, width=400, height=300))

    elements.append(Paragraph("Boxplot of Trip Durations", styles['Heading2']))
    box_buffer = create_boxplot(data, 'duration', 'Boxplot de Duración de Viajes')
    elements.append(Image(box_buffer, width=400, height=300))

    doc.build(elements)

    buffer_most_popular.close()
    buffer_distances.close()
    buffer_longest_duration.close()
    map_buffer.close()
    hist_buffer.close()
    scatter_buffer.close()
    box_buffer.close()

    with open(filePath, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print("Reporte generado con éxito.")
    pdf_buffer.close()
    os.startfile(".\\" + filePath)


    # En otros sistemas operativos (Linux, macOS):
    # os.system(f'xdg-open "{filePath}"')  # Para Linux
    # os.system(f'open "{filePath}"')      # Para macOS
    pass