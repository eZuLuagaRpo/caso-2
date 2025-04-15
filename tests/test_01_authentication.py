import pytest
from unittest.mock import Mock
from modules._01authentication import Authentication

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
def test_login_invalid_types(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login(123, "password")
    with pytest.raises(ValueError):
        auth_dummy.login("user", 123)

#Test para datos vacios
def test_login_empty_strings(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login("", "")

#Test para datos nulos
def test_login_none_values(auth_dummy):
    with pytest.raises(ValueError):
        auth_dummy.login(None, None)

#Test para base de datos vacia
def test_empty_database(auth_dummy):
    assert auth_dummy.login("test_user", "test_password") == False
    assert auth_dummy.getSession() == False

# Tests para login exitoso
def test_valid_login(auth_stub):
    assert auth_stub.login("test_user", "test_password") == True
    assert auth_stub.getSession() == True

# Tests para login fallido
def test_invalid_login(auth_stub):
    assert auth_stub.login("wrong_user", "wrong_password") == False
    assert auth_stub.getSession() == False

# Tests Logout
def test_logout(auth_stub):
    auth_stub.login("test_user", "test_password")
    assert auth_stub.getSession() == True
    auth_stub.logout()
    assert auth_stub.getSession() == False

#Test para base de datos nula
def test_none_database():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    mock_db.db.return_value = None
    auth = Authentication(mock_db)
    assert auth.login("test_user", "test_password") == False
    assert auth.getSession() == False

# Tests para verificar el comportamiento con Mock
def test_login_With_Mock():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    mock_db.db.return_value = {"test_user": "test_password"}
    
    auth = Authentication(mock_db)
    assert auth.login("test_user", "test_password") == True
    assert auth.getSession() == True
    mock_db.connection.assert_called_once()
    mock_db.db.assert_called_once()
    
# Tests para verificar el comportamiento con Mock y fallo de conexión
def test_login_With_Mock_Fail_Connection():
    mock_db = Mock()
    mock_db.connection.return_value = "Error"
    
    auth = Authentication(mock_db)
    assert auth.login("test_user", "test_password") == False
    assert auth.getSession() == False
    
    mock_db.connection.assert_called_once()
    mock_db.db.assert_not_called() 

#Test para credenciales muy largas
def test_very_long_credentials():
    mock_db = Mock()
    mock_db.connection.return_value = "Success"
    long_user = "a" * 1000
    long_pass = "b" * 1000
    mock_db.db.return_value = {long_user: long_pass}
    auth = Authentication(mock_db)
    assert auth.login(long_user, long_pass) == True
    assert auth.getSession() == True #error porque no se maneja el error de credenciales muy largas y sirve para seguridad

