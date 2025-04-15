import pytest
import pandas as pd
import json
import os
from unittest.mock import patch, MagicMock
from modules._02request import getData

# Datos de prueba
data = [{"id": i, "name": f"Item {i}", "value": i * 100} for i in range(15000)]

# Fixture para crear un directorio temporal
@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path

    
# Test para verificar que getData maneja correctamente una respuesta exitosa
def test_successful_response(temp_dir): 
    mock_response = MagicMock()
    mock_response.status_code = 200 
    mock_response.json.return_value = data 
    
    with patch("modules._02request.requests.get", return_value=mock_response):
        response = getData("https://ejemplo.com/api/data", str(temp_dir))
        assert response == True
        
        excel_file = temp_dir / "data.xlsx"
        assert excel_file.exists()
        
        df = pd.read_excel(excel_file)
        assert len(df) == 10000
        assert list(df.columns) == ["id", "name", "value"]

# Test para verificar que getData maneja correctamente una respuesta con error
def test_error_response(temp_dir):
    mock_response = MagicMock()
    mock_response.status_code = 404
    with patch("modules._02request.requests.get", return_value=mock_response):
        response = getData("https://example.com/api/data", str(temp_dir))

        assert response == False
        excel_file = temp_dir / "data.xlsx"
        assert not excel_file.exists()


# Test para verificar que getData maneja correctamente datos JSON inválidos
def test_invalid_json(temp_dir):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = "estructura de datos inválida"    
    
    with patch("modules._02request.requests.get", return_value=mock_response):
        response = getData("https://example.com/api/data", str(temp_dir))
        assert response == False
        excel_file = temp_dir / "data.xlsx"
        assert not excel_file.exists()

#Test para verificar si el codigo maneja errores de conexion 
def test_connection_error(temp_dir):
    with patch("modules._02request.requests.get", side_effect=Exception("Connection error")):
        response = getData("https://example.com/api/data", str(temp_dir))
        assert response == False
        excel_file = temp_dir / "data.xlsx"
        assert not excel_file.exists()

# Test para verificar que getData maneja correctamente errores de escritura de archivo
def test_file_write_error(temp_dir):
    mock_response = MagicMock()
    # Crear un mock para requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = data
    
    # Crear un directorio de solo lectura
    read_only_dir = temp_dir / "readonly"
    read_only_dir.mkdir()
    os.chmod(read_only_dir, 0o444)  # Establecer permisos de solo lectura
    
    with patch("modules._02request.requests.get", return_value=mock_response):
        # Llamar a getData con un directorio de solo lectura
        result = getData("https://example.com/api/data", str(read_only_dir))
        
        # Verificar que la función retorna False
        assert result == False
        
        # Verificar que no se creó el archivo Excel
        excel_file = read_only_dir / "data.xlsx"
        assert not excel_file.exists()
    
    # Restaurar permisos para evitar problemas con otros tests
    os.chmod(read_only_dir, 0o755)
