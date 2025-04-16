import pytest
import pandas as pd
from unittest.mock import patch
from modules._03analytics import Analytics
import allure
from allure_commons.types import Severity

# Clase auxiliar para simular geopy.distance.geodesic
class MockDistance:
    def __init__(self, km):
        self.kilometers = km

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "start_station_name": ["Station A", "Station B", "Station A", "Station C", "Station D", "Station E", "Station F", "Station G", "Station H", "Station I", "Station J"],
        "end_station_name": ["Station B", "Station C", "Station C", "Station D", "Station E", "Station F", "Station G", "Station H", "Station I", "Station J", "Station A"],
        "start_station_latitude": [60.39, 60.40, 60.39, 60.42, 60.43, 60.44, 60.45, 60.46, 60.47, 60.48, 60.49],
        "start_station_longitude": [5.32, 5.33, 5.32, 5.34, 5.35, 5.36, 5.37, 5.38, 5.39, 5.40, 5.41],
        "end_station_latitude": [60.40, 60.41, 60.41, 60.42, 60.43, 60.44, 60.45, 60.46, 60.47, 60.48, 60.49],
        "end_station_longitude": [5.33, 5.34, 5.34, 5.35, 5.36, 5.37, 5.38, 5.39, 5.40, 5.41, 5.42],
        "duration": [300, 600, 450, 500, 700, 800, 900, 1000, 1100, 1200, 1300]
    })

# Test para verificar que el analizador de datos funciona correctamente
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with Normal Case")
@allure.description("Verifica que el método AnalizeData procesa correctamente un conjunto de datos válido, generando estadísticas, rutas populares, distancias y duraciones.")
@allure.tag("analytics", "unit", "positive")
@allure.severity(Severity.CRITICAL)
def test_analyze_data_normal_case(sample_data):
    with patch("pandas.read_excel", return_value=sample_data): 
        with patch("modules._03analytics.geodesic", return_value=MockDistance(1.5)):
            analytics = Analytics()
            result = analytics.AnalizeData()

            assert isinstance(result, dict)
            assert set(result.keys()) == {"data", "most_popular_routes", "distance_between_routes", "longest_duration_routes", "stats"}
            assert len(result["data"]) == len(sample_data)  # No hay duplicados en este caso
            assert len(result["most_popular_routes"]) <= 10
            assert "Station A to Station B" in result["most_popular_routes"]["route"].values

            # Verificar distancias
            assert len(result["distance_between_routes"]) <= 10
            assert result["distance_between_routes"]["distance_km"].iloc[0] == 1.5

            # Verificar duraciones
            assert len(result["longest_duration_routes"]) <= 10
            assert result["longest_duration_routes"]["avg_duration"].iloc[0] > 0

            # Verificar estadísticas
            assert len(result["stats"]) == 8
            assert result["stats"]["Statistic"].tolist() == [
                "Mean", "Variance", "Standard Deviation", "Max", "Min",
                "25th Percentile", "50th Percentile", "75th Percentile"
            ]

# Test para verificar que el analizador de datos funciona correctamente con un DataFrame vacío
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with Empty DataFrame")
@allure.description("Verifica que el método AnalizeData maneja un DataFrame vacío, aunque el módulo no lo procesa correctamente y puede fallar. Debería retornar resultados vacíos.")
@allure.tag("analytics", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_analyze_data_empty():
    empty_data = pd.DataFrame(columns=[
        "start_station_name", "end_station_name",
        "start_station_latitude", "start_station_longitude",
        "end_station_latitude", "end_station_longitude",
        "duration"
    ])
    
    with patch("pandas.read_excel", return_value=empty_data):
        with patch("geopy.distance.geodesic", return_value=MockDistance(0)):
            analytics = Analytics()
            result = analytics.AnalizeData()

            # Verificar que no hay datos procesados
            assert len(result["data"]) == 0
            assert len(result["most_popular_routes"]) == 0
            assert len(result["distance_between_routes"]) == 0
            assert len(result["longest_duration_routes"]) == 0
            # Verificar que stats tiene valores NaN o ceros donde corresponde
            assert result["stats"]["Duration"].iloc[0].isna()  # Media es NaN

# Test para verificar que el analizador de datos maneja correctamente un archivo no encontrado
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with File Not Found")
@allure.description("Verifica que el método AnalizeData lanza FileNotFoundError cuando el archivo de datos no existe. El módulo debería mejorar el manejo de este error.")
@allure.tag("analytics", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_analyze_data_file_not_found():
    with patch("pandas.read_excel", side_effect=FileNotFoundError):
        analytics = Analytics()
        with pytest.raises(FileNotFoundError):
            analytics.AnalizeData()

# Test para verificar que el analizador de datos maneja correctamente un DataFrame sin columnas requeridas
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with Missing Columns")
@allure.description("Verifica que el método AnalizeData lanza KeyError cuando el DataFrame no contiene las columnas requeridas para el análisis.")
@allure.tag("analytics", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_analyze_data_missing_columns():
    # DataFrame sin columnas requeridas
    invalid_data = pd.DataFrame({
        "other_column": [1, 2, 3]
    })
    
    with patch("pandas.read_excel", return_value=invalid_data):
        analytics = Analytics()
        with pytest.raises(KeyError):
            analytics.AnalizeData()

# Test para verificar que el analizador de datos maneja correctamente una ruta con estaciones iguales
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with Same Stations")
@allure.description("Verifica que el método AnalizeData elimina correctamente las rutas donde la estación de inicio y fin son iguales, asegurando datos válidos.")
@allure.tag("analytics", "unit", "positive")
@allure.severity(Severity.CRITICAL)
def test_analyze_data_same_stations(sample_data):
    sample_data.loc[3] = [
        "Station A", "Station A", 60.39, 5.32, 60.39, 5.32, 200
    ]
    
    with patch("pandas.read_excel", return_value=sample_data):
        analytics = Analytics()
        result = analytics.AnalizeData()
  
        # Verificar que la ruta con estaciones iguales fue eliminada
        assert len(result["data"]) == 10  # Una fila menos
        assert not (result["data"]["start_station_name"] == result["data"]["end_station_name"]).any()

# Test para verificar que el analizador de datos maneja correctamente coordenadas inválidas
@allure.feature("Data Analytics System")
@allure.title("Test Data Analysis with Invalid Coordinates")
@allure.description("Verifica que el método AnalizeData lanza ValueError para coordenadas inválidas (None). El módulo falla al reemplazar NaN por 0, lo que debería corregirse.")
@allure.tag("analytics", "unit", "edge")
@allure.severity(Severity.MINOR)
def test_analyze_data_invalid_coordinates():
    invalid_data = pd.DataFrame({
        "start_station_name": ["Station A"],
        "end_station_name": ["Station B"],
        "start_station_latitude": [None],
        "start_station_longitude": [5.32],
        "end_station_latitude": [60.40],
        "end_station_longitude": [5.33],
        "duration": [300]
    })
    
    with patch("pandas.read_excel", return_value=invalid_data):
        analytics = Analytics()
        with pytest.raises(ValueError):  # geodesic fallará con None
            analytics.AnalizeData()