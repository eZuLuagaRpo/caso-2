import time
import pytest
import threading
import sys
from io import StringIO
from modules._00spinner import spinner


#verificar que el hilo no se inicia si no se llama a start
def test_spinner_join_without_start():
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
    
    # No iniciar el hilo, solo llamar a join
    spinner_thread.join(timeout=0.1)
    
    # Verificar que no hay errores (el hilo simplemente no está activo)
    assert not spinner_thread.is_alive()


def test_spinner_stops_on_error():
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(stop_event,))
    spinner_thread.start()
    
    try:
        time.sleep(0.5) 
        raise RuntimeError("Simulated error")
    except RuntimeError:
        time.sleep(0.5) 
        spinner_thread.join(timeout=0.1) 
        assert not spinner_thread.is_alive(), "Spinner did not stop after error"
    
    stop_event.set()
    spinner_thread.join(timeout=1.0)