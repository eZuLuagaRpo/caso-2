import itertools
import time
import sys
def spinner(stop_event):
    spinner_cycle = itertools.cycle(['-', '/', '|', '\\'])
    while not stop_event.is_set():  # El spinner se detendrá cuando el evento esté activado
        sys.stdout.write(next(spinner_cycle))
        sys.stdout.flush()
        sys.stdout.write('\b')  # Borra el símbolo anterior
        time.sleep(0.1)


