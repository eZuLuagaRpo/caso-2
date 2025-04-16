import os
import pandas as pd
import pytest
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch
from PIL import Image

# Importación de módulos del sistema
from modules._01authentication import Authentication
from modules._03analytics import Analytics
from modules._04report import report
from modules._02request import getData
import main
import allure
from allure_commons.types import Severity

# Clases y utilidades auxiliares
class StubDatabase:
    """Retorna valores predefinidos para simular base de datos"""
    def connection(self):
        return "Success"
    
    def db(self):
        return {"test_user": "test_password"}

class FakeThread:
    """Implementación falsa de Thread para evitar ejecución de hilos reales"""
    def __init__(self, *args, **kwargs):
        pass
    def start(self):
        pass
    def join(self):
        pass

# Fixtures para datos de prueba
@pytest.fixture
def sample_data():
    """Proporciona un conjunto de datos de muestra para las pruebas"""
    return [{
        "start_station_name": "Station A",
        "end_station_name": "Station B",
        "start_station_latitude": 60.39,
        "start_station_longitude": 5.32,
        "end_station_latitude": 60.38,
        "end_station_longitude": 5.33,
        "duration": 300,
        "distance_km": 1.2,
        "route": "Station A to Station B"
    }]

# Fixtures para configuración de entorno
@pytest.fixture
def auth_stub():
    """Proporciona un objeto Authentication inicializado con un StubDatabase"""
    db = StubDatabase()
    auth = Authentication(db)
    yield auth
    # tearDown
    auth.logout()

@pytest.fixture
def auth_stub_main(monkeypatch):
    """Reemplaza la clase dataBase en main con StubDatabase"""
    monkeypatch.setattr(main, "dataBase", StubDatabase)
    yield

@pytest.fixture
def temp_dirs(tmp_path):
    """Crea una estructura de directorios temporal para las pruebas"""
    input_dir = tmp_path / "data" / "input"
    output_dir = tmp_path / "data" / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "root": tmp_path,
        "input": input_dir,
        "output": output_dir,
        "excel_path": input_dir / "data.xlsx"
    }

@pytest.fixture
def temp_working_dir(temp_dirs, monkeypatch):
    """Cambia el directorio de trabajo actual al directorio temporal"""
    monkeypatch.chdir(temp_dirs["root"])
    return temp_dirs["root"]

@pytest.fixture
def create_fake_logo(temp_working_dir):
    """
    Crea una imagen JPG real en assets/usb.jpg para evitar errores de PIL/ReportLab.
    """
    assets_dir = temp_working_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    fake_logo_path = assets_dir / "usb.jpg"

    # Crear una imagen real (100x100 px, fondo blanco)
    img = Image.new("RGB", (100, 100), color="white")
    img.save(fake_logo_path, "JPEG")

    return str(fake_logo_path)

# Fixtures para mocks y parches
@pytest.fixture
def simulate_inputs(monkeypatch):
    """Simula entradas del usuario para login"""
    monkeypatch.setattr("builtins.input", lambda _: "test_user")
    monkeypatch.setattr(main, "getpass", lambda prompt="": "test_password")

@pytest.fixture
def mock_http_response(sample_data):
    """Crea una respuesta HTTP simulada con datos de prueba"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_data
    return mock_response

@pytest.fixture
def patch_requests_get(monkeypatch, sample_data):
    """Parchea el método requests.get para simular una respuesta HTTP exitosa"""
    def fake_get(url):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_data
        return mock_response

    monkeypatch.setattr("modules._02request.requests.get", fake_get)
    yield

@pytest.fixture(autouse=True)
def patch_external(monkeypatch):
    """Parchea funciones externas para evitar efectos secundarios durante las pruebas"""
    # Evitar que se abra el PDF al final
    monkeypatch.setattr("main.os.startfile", lambda path: None)
    # Parchear spinner para que no haga nada
    monkeypatch.setattr(main, "spinner", lambda stop_event: None)
    # Parchear threading.Thread para evitar errores con el hilo del spinner
    monkeypatch.setattr(threading, "Thread", lambda *args, **kwargs: FakeThread())

# Prueba de integración que simula el flujo completo
@allure.feature("System Integration")
@allure.title("Test Full System Integration")
@allure.description(
    "Verifica la integración completa del sistema, incluyendo: "
    "1. Autenticación con credenciales válidas usando StubDatabase, "
    "2. Obtención de datos simulados mediante una respuesta HTTP mock, "
    "3. Análisis de datos con el módulo Analytics, "
    "4. Generación de un reporte PDF y verificación de su existencia."
)
@allure.tag("integration", "positive")
@allure.severity(Severity.CRITICAL)
def test_full_system_integration(auth_stub, temp_dirs, mock_http_response):
    # 1. Autenticación
    assert auth_stub.login("test_user", "test_password") is True, "El login debe ser exitoso con credenciales válidas"
    
    # 2. Simular obtención de datos
    with patch("modules._02request.requests.get", return_value=mock_http_response):
        url = "http://fake.url"
        result = getData(url, str(temp_dirs["input"]))
        assert result is True, "getData debe devolver True con respuesta exitosa"
        assert temp_dirs["excel_path"].exists(), "El archivo Excel debe haberse creado"

    # 3. Ejecutar Analytics
    analytics = Analytics()
    analized_data = analytics.AnalizeData()
    
    # Validar estructura del resultado
    expected_keys = ["data", "most_popular_routes", "distance_between_routes", "longest_duration_routes", "stats"]
    for key in expected_keys:
        assert key in analized_data, f"La clave '{key}' debe estar presente en analized_data"

    # 4. Generar reporte PDF
    pdf_path = temp_dirs["output"] / "report.pdf"
    report(str(pdf_path), analized_data, "test_user")
    
    # Verificar PDF
    assert pdf_path.exists(), "El reporte PDF debe haberse creado"
    assert os.path.getsize(str(pdf_path)) > 0, "El reporte PDF no debe estar vacío"

# Prueba la integración del proceso de autenticación desde main.py
@allure.feature("System Integration")
@allure.title("Test Main Authentication Integration")
@allure.description(
    "Verifica la integración del proceso de autenticación desde main.py, incluyendo: "
    "1. Simulación de entradas de usuario para login con StubDatabase, "
    "2. Ejecución de main.py hasta la autenticación, "
    "3. Verificación del mensaje de bienvenida con el nombre de usuario."
)
@allure.tag("integration", "positive")
@allure.severity(Severity.NORMAL)
def test_main_auth_integration(auth_stub_main, simulate_inputs, monkeypatch, capsys):
    # Detener ejecución después de autenticación para evitar el flujo completo
    monkeypatch.setattr(main, "getData", lambda url, path: False)
    
    # Ejecutar main
    main.main()
    
    # Verificar salida
    captured = capsys.readouterr().out
    assert "Bienvenid@ test_user" in captured, "El login debe mostrar el mensaje de bienvenida correctamente"

# Prueba de integración completa que inicia desde main.py
@allure.feature("System Integration")
@allure.title("Test Full System Integration from Main")
@allure.description(
    "Verifica la integración completa del sistema desde main.py, incluyendo: "
    "1. Autenticación simulada con entradas de usuario, "
    "2. Obtención de datos mediante una respuesta HTTP mock, "
    "3. Análisis de datos con Analytics, "
    "4. Generación de un reporte PDF con un logo simulado, "
    "5. Verificación de mensajes en consola y existencia del reporte."
)
@allure.tag("integration", "positive")
@allure.severity(Severity.CRITICAL)
def test_full_system_integration_main_request_analytics(
    auth_stub_main,
    simulate_inputs,
    patch_requests_get,
    temp_working_dir,
    create_fake_logo,
    capsys
):
    # Parchear la ruta del logo en el header/footer para que apunte al archivo temporal
    with patch("modules._04report.PDFWithHeaderFooter._header_footer") as mocked_header:
        def custom_header(canvas_obj, doc):
            canvas_obj.drawImage(create_fake_logo, 50, 730, width=50, height=50)

        mocked_header.side_effect = custom_header

        # Ejecutar el flujo principal completo
        main.main()

    # Verificaciones de mensajes en consola
    captured = capsys.readouterr().out
    assert "Leyendo datos..." in captured, "Debe mostrarse el mensaje de lectura de datos"
    assert "Analizando datos..." in captured, "Debe mostrarse el mensaje de análisis de datos"
    
    # Verificar generación del reporte PDF
    report_path = temp_working_dir / "data" / "output" / "report.pdf"
    assert report_path.exists(), "El reporte PDF debe existir"
    assert report_path.stat().st_size > 0, "El reporte PDF no debe estar vacío"