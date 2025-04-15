import time
import pytest
import threading
import sys
from io import StringIO
from modules._00spinner import spinner

def test_spinner_starts_and_outputs(monkeypatch):
    # Capturar la salida de la consola
    captured_output = StringIO()
    monkeypatch.setattr(sys, 'stdout', captured_output)
    
    # Crear un evento para detener el spinner
    stop_event = threading.Event()
    
    # Iniciar el spinner en un hilo
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
    spinner_thread.start()
    
    # Esperar un breve tiempo para capturar salida
    time.sleep(0.3)  # Suficiente para ~3 iteraciones
    stop_event.set()
    spinner_thread.join()
    
    # Verificar que los caracteres esperados aparecen
    output = captured_output.getvalue()
    assert '-' in output
    assert '/' in output
    assert '|' in output
    assert '\\' in output

def test_spinner_stops_on_event():
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
    
    # Iniciar el spinner
    spinner_thread.start()
    
    # Detener después de un breve tiempo
    time.sleep(0.1)
    stop_event.set()
    
    # Esperar a que termine
    spinner_thread.join(timeout=0.5)
    
    # Verificar que el hilo terminó
    assert not spinner_thread.is_alive()

# Test para verificar que el hilo no se inicia si no se llama a start
def test_spinner_join_without_start():
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
    
    # No iniciar el hilo, solo llamar a join
    spinner_thread.join(timeout=0.1)
    
    # Verificar que no hay errores (el hilo simplemente no está activo)
    assert not spinner_thread.is_alive()