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
    
    # Save to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

# Function to convert DataFrame to a ReportLab Table
def dataframe_to_table(df):
    table_data = [list(df.columns)] + df.values.tolist()
    return Table(table_data)

# Create the map plot for bike stations
def create_map_plot(data):
    # Create GeoDataFrames for start and end stations
    gdf_start = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['start_station_longitude'], data['start_station_latitude']))
    gdf_end = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['end_station_longitude'], data['end_station_latitude']))

    # Combine start and end stations into one GeoDataFrame, keeping unique stations
    gdf_all_stations = pd.concat([gdf_start[['start_station_name', 'geometry']],
                                  gdf_end[['end_station_name', 'geometry']].rename(columns={'end_station_name': 'start_station_name'})]).drop_duplicates()

    gdf_all_stations = gdf_all_stations.set_crs(epsg=4326)

    # Plotting the stations with a basemap
    fig, ax = plt.subplots(figsize=(10, 8))
    gdf_all_stations.plot(ax=ax, marker='o', color='red', markersize=5)
    try:
        ctx.add_basemap(ax, crs=gdf_all_stations.crs)
    except:
        print("No se pudo obtener la imagen del mapa de fondo. Problemas de conexión con el servidor.")

    # Customize the map
    plt.title('Ubicación de las estaciones')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    ax.set_aspect('equal', 'box')

    # Save the plot to a buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def report(filePath, analized_data, username):

    most_popular_routes = analized_data["most_popular_routes"]
    distance_between_routes = analized_data["distance_between_routes"]
    longest_duration_routes = analized_data["longest_duration_routes"]
    data = analized_data["data"]

    # Create PDF document with header and footer
    pdf_buffer = BytesIO()
    doc = PDFWithHeaderFooter(pdf_buffer, pagesize=letter, topMargin=1.5*inch, bottomMargin=1.5*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)

    elements = []

    styles = getSampleStyleSheet()

    # Add a description paragraph with the current date
    report_date = datetime.now().strftime('%Y-%m-%d')
    description = f"Este reporte presenta las rutas de bicicleta más populares en el sistema de bicicletas públicas de Noruega, las distancias más largas entre estaciones, y la mayor duración promedio de rutas en base a los datos proporcionados."
    elements.append(Paragraph(description, styles['BodyText']))
    elements.append(Spacer(1, 12))

    created = f"Creado por {username} el {report_date}."
    elements.append(Paragraph(created, styles['BodyText']))
    elements.append(Spacer(1, 12))


    # Add the map plot to the PDF
    map_buffer = create_map_plot(data)
    elements.append(Image(map_buffer, width=500, height=400))

    # Add Most Popular Routes Table
    elements.append(Paragraph("Most Popular Routes", styles['Heading2']))
    table_most_popular = dataframe_to_table(most_popular_routes)
    table_most_popular.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                            ('FONTSIZE', (0, 0), (-1, 0), 12),
                                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]))
    elements.append(table_most_popular)

    # Add bar chart for Most Popular Routes
    buffer_most_popular = create_bar_chart(most_popular_routes, 'count', 'Most Popular Routes')
    elements.append(Image(buffer_most_popular, width=400, height=300))

    # Add Distance Between Routes Table
    elements.append(Paragraph("Routes with the Largest Distances", styles['Heading2']))
    table_distances = dataframe_to_table(distance_between_routes)
    table_distances.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]))
    elements.append(table_distances)

    # Add bar chart for Distances
    buffer_distances = create_bar_chart(distance_between_routes, 'distance_km', 'Longest Distances Between Stations')
    elements.append(Image(buffer_distances, width=400, height=300))

    # Add Longest Duration Routes Table
    elements.append(Paragraph("Routes with the Longest Average Duration", styles['Heading2']))
    table_longest_duration = dataframe_to_table(longest_duration_routes)
    table_longest_duration.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                                ('FONTSIZE', (0, 0), (-1, 0), 12),
                                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige)]))
    elements.append(table_longest_duration)

    # Add bar chart for Longest Duration Routes
    buffer_longest_duration = create_bar_chart(longest_duration_routes, 'avg_duration', 'Longest Average Durations')
    elements.append(Image(buffer_longest_duration, width=400, height=300))

    # Build PDF
    doc.build(elements)

    # Close the buffers
    buffer_most_popular.close()
    buffer_distances.close()
    buffer_longest_duration.close()
    map_buffer.close()

    # Save the PDF to a file
    with open(filePath, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print("Reporte generado con éxito.")

    # Close the PDF buffer
    pdf_buffer.close()

    # Abrir el archivo PDF
    os.startfile(".\\"+filePath)  # Solo en Windows

    # En otros sistemas operativos (Linux, macOS):
    # os.system(f'xdg-open "{pdf_path}"')  # Para Linux
    # os.system(f'open "{pdf_path}"')      # Para macOS
    pass
