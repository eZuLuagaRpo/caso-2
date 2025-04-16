import os
import io
import pytest
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")  # ¡Antes de importar pyplot!
import matplotlib.pyplot as plt
from unittest.mock import MagicMock
from io import BytesIO
from reportlab.platypus import Table
from reportlab.lib import colors
from modules._04report import (
    PDFWithHeaderFooter,
    create_bar_chart,
    dataframe_to_table,
    create_map_plot,
    create_distribution_plots,
    create_scatter_plot,
    create_box_plots,
    report
)
from modules._03analytics import Analytics
import contextily as ctx

#fixture para los datos de prueba
@pytest.fixture
def sample_data():
    """Datos de prueba simulados con estructura completa."""
    return pd.DataFrame({
        'start_station_name': ['Station A', 'Station B', 'Station A', 'Station C'],
        'end_station_name': ['Station B', 'Station C', 'Station C', 'Station A'],
        'start_station_latitude': [60.39, 60.38, 60.39, 60.37],
        'start_station_longitude': [5.32, 5.33, 5.32, 5.34],
        'end_station_latitude': [60.38, 60.37, 60.37, 60.39],
        'end_station_longitude': [5.33, 5.34, 5.32, 5.32],
        'duration': [300, 450, 600, 200],
        'distance_km': [1.2, 2.5, 3.0, 1.8],
        'route': ['Station A to Station B', 'Station B to Station C', 'Station A to Station C', 'Station C to Station A']
    })

#fixture para analizar los datos simulados y tener los resultados
@pytest.fixture
def analized_data(sample_data, monkeypatch):
    """Datos analizados simulados con monkeypatch para lectura de Excel."""
    monkeypatch.setattr(pd, 'read_excel', MagicMock(return_value=sample_data))
    analytics = Analytics()
    return analytics.AnalizeData()

#fixture para los datos de prueba invalidos
@pytest.fixture
def invalid_data():
    """Datos inválidos para pruebas de edge cases."""
    return {
        "most_popular_routes": pd.DataFrame(),
        "distance_between_routes": pd.DataFrame(),
        "longest_duration_routes": pd.DataFrame(),
        "data": pd.DataFrame(),
        "stats": pd.DataFrame()
    }

#mock para todas las pruebas 
@pytest.fixture(autouse=True)
def global_mocks(monkeypatch):
    # Evita apertura de PDF
    monkeypatch.setattr(os, "startfile", lambda _: None)
    

    """
    Mock para eliminar la dependencia de un archivo de logo (assets/logo.png)
    Evita errores si el logo no existe durante las pruebas
    """
    monkeypatch.setattr(
        PDFWithHeaderFooter, 
        "_header_footer", 
        lambda self, canvas, doc: None
    )
    
    """
    Mock para evitar la llamada a add_basemap de contextily
    Evita errores si no hay conexión a internet
    """
    monkeypatch.setattr(ctx, "add_basemap", lambda ax, crs: None)

#Test para crear la tabla
def test_dataframe_to_table(sample_data):
    table = dataframe_to_table(sample_data)
    assert isinstance(table, Table)
    assert len(table._cellvalues) == len(sample_data) + 1  # Filas + encabezado

#Test para crear el grafico de barras
def test_create_bar_chart(sample_data):
    buffer = create_bar_chart(sample_data, 'distance_km', 'Test Chart')
    assert isinstance(buffer, BytesIO)
    assert len(buffer.getvalue()) > 0
    buffer.close()

#Test para crear el grafico de mapa
def test_create_map_plot(sample_data):
    buffer = create_map_plot(sample_data)
    assert isinstance(buffer, BytesIO)
    buffer.close()      

#Test para crear el grafico de distribucion
def test_create_distribution_plots(sample_data):
    buffer = create_distribution_plots(sample_data)
    assert buffer.getvalue()[:8] == b'\x89PNG\r\n\x1a\n'
    buffer.close()

#Test para crear el grafico de dispersion           
def test_create_scatter_plot(sample_data):
    buffer = create_scatter_plot(sample_data)
    assert buffer.tell() == 0  # Verifica posición inicial después de seek(0)
    buffer.close()

#Test para crear el grafico de boxplots
def test_create_box_plots(sample_data):
    buffer = create_box_plots(sample_data)
    assert not buffer.closed  # Verifica que el buffer esté abierto
    buffer.close()

#Test para generar el reporte
def test_report_generation(tmp_path, analized_data):
    pdf_path = tmp_path/"report.pdf"
    report(str(pdf_path), analized_data, "test_user")
    
    # Verificaciones básicas del archivo
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1024  # PDF no vacío
    
    # Verificación de contenido mínimo
    with open(pdf_path, 'rb') as f:
        content = f.read()
        assert b'%PDF' in content  # Cabecera de PDF válida

