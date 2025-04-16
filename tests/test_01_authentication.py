import pytest
from unittest.mock import Mock
from modules._01authentication import Authentication
import allure
from allure_commons.types import Severity

class DummyDatabase:
    """Simular la base de datos"""
    def connection(self):
        return "Success"
    
    def db(self):
        return {}

class StubDatabase: 
    """Retorna valores predefinidos"""
    def connection(self):
        return "Success"
    
    def db(self):
        return {"test_user": "test_password"}

# Fixture para login con DummyDatabase
@pytest.fixture
def auth_dummy():
    db = DummyDatabase()
    auth = Authentication(db)
    yield auth
    # tearDown
    auth.logout()

@pytest.fixture
def auth_stub():
    db = StubDatabase()
    auth = Authentication(db)
    yield auth
    # tearDown
    auth.logout()

# Tests para login con tipos inválidos
@allure.feature("Authentication System")
@allure.title("Test Login with Invalid Types")
@allure.description("Verifica que el método login lanza ValueError cuando se proporcionan tipos de datos inválidos (no cadenas) para usuario o contraseña.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_login_invalid_types(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login(123, "password")
    with pytest.raises(ValueError):
        auth_dummy.login("user", 123)

# Test para datos vacíos
@allure.feature("Authentication System")
@allure.title("Test Login with Empty Strings")
@allure.description("Verifica que el método login lanza ValueError cuando se proporcionan cadenas vacías como usuario y contraseña.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_login_empty_strings(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login("", "")

# Test para datos nulos
@allure.feature("Authentication System")
@allure.title("Test Login with None Values")
@allure.description("Verifica que el método login lanza ValueError cuando se proporcionan valores None para usuario y contraseña.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_login_none_values(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login(None, None)

# Test para base de datos vacía
@allure.feature("Authentication System")
@allure.title("Test Login with Empty Database")
@allure.description("Verifica que el método login devuelve False cuando la base de datos está vacía y no hay credenciales válidas.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_empty_database(auth_dummy):
    assert auth_dummy.login("test_user", "test_password") == False
    assert auth_dummy.getSession() == False

# Tests para login exitoso
@allure.feature("Authentication System")
@allure.title("Test Successful Login")
@allure.description("Verifica que el método login devuelve True y establece una sesión activa cuando se proporcionan credenciales válidas.")
@allure.tag("authentication", "unit", "positive")
@allure.severity(Severity.CRITICAL)
def test_valid_login(auth_stub):
    assert auth_stub.login("test_user", "test_password") == True
    assert auth_stub.getSession() == True

# Tests para login fallido
@allure.feature("Authentication System")
@allure.title("Test Failed Login")
@allure.description("Verifica que el método login devuelve False y no establece una sesión cuando se proporcionan credenciales inválidas.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_invalid_login(auth_stub):
    assert auth_stub.login("wrong_user", "wrong_password") == False
    assert auth_stub.getSession() == False

# Tests Logout
@allure.feature("Authentication System")
@allure.title("Test Logout")
@allure.description("Verifica que el método logout cierra la sesión correctamente después de un login exitoso.")
@allure.tag("authentication", "unit", "positive")
@allure.severity(Severity.CRITICAL)
def test_logout(auth_stub):
    auth_stub.login("test_user", "test_password")
    assert auth_stub.getSession() == True
    auth_stub.logout()
    assert auth_stub.getSession() == False

# Test para base de datos nula
@allure.feature("Authentication System")
@allure.title("Test Login with None Database")
@allure.description("Verifica que el método login devuelve False cuando la base de datos devuelve None, simulando un error en la base de datos.")
@allure.tag("authentication", "unit", "negative")
@allure.severity(Severity.NORMAL)
def test_none_database():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    mock_db.db.return_value = None
    auth = Authentication(mock_db)
    assert auth.login("test_user", "test_password") == False
    assert auth.getSession() == False

# Tests para verificar el comportamiento con Mock
@allure.feature("Authentication System")
@allure.title("Test Login with Mock Database")
@allure.description("Verifica que el método login funciona correctamente con una base de datos simulada (mock) y valida las llamadas a los métodos de la base de datos.")
@allure.tag("authentication", "unit", "positive")
@allure.severity(Severity.CRITICAL)
def test_login_With_Mock():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    mock_db.db.return_value = {"test_user": "test_password"}
    
    auth = Authentication(mock_db)
    assert auth.login("test_user", "test_password") == True
    assert auth.getSession() == True
    mock_db.connection.assert_called_once()
    mock_db.db.assert_called_once()

# Test para credenciales muy largas
@allure.feature("Authentication System")
@allure.title("Test Login with Very Long Credentials")
@allure.description("Verifica que el método login maneja correctamente credenciales muy largas, aunque debería fallar por motivos de seguridad (caso de borde).")
@allure.tag("authentication", "unit", "edge")
@allure.severity(Severity.MINOR)
def test_very_long_credentials():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    long_user = "a" * 1000
    long_pass = "b" * 1000
    mock_db.db.return_value = {long_user: long_pass}
    auth = Authentication(mock_db)
    assert auth.login(long_user, long_pass) == True
    assert auth.getSession() == True