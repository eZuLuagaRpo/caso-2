from modules import Authentication, Analytics, report, getData, spinner
from getpass import getpass
import threading

class dataBase: # Fake
    def __init__(self) -> None:
        pass
    def connection(self): # Stub
        return "Success"
    def db(self):# Stub
        return {"user1":"pass1","user2":"pass2"}

AuthSystem = Authentication(dataBase())

# Crear un hilo paralelo para el spinner de carga
stop_event = threading.Event()
spinner_thread = threading.Thread(target=spinner, args=(stop_event,))

print(f"===========================================================")
print(f"============== Sistema de análisis de datos ===============")
print(f"===========================================================")
print("Por favor inicie sesión.")

session = AuthSystem.getSession()
tries = 0
while tries < 3:
    user = input("Ingrese usuario: ")
    password = getpass("Contraseña: ")
    if AuthSystem.login(user, password):
        session = AuthSystem.getSession()
        break

    tries += 1

if session:
    print(f"===========================================================")
    print(f"==================== Bienvenid@ {user} ====================")
    print(f"===========================================================")
    print("Obteniendo datos de ... https://data.urbansharing.com/bergenbysykkel.no/trips/v1/2024/09.json")

    data_response = getData("https://data.urbansharing.com/bergenbysykkel.no/trips/v1/2024/09.json","data/input") 

    AnalyticsModule = Analytics()
    analized_data = AnalyticsModule.AnalizeData()

    if data_response:
        print("Generando reporte...")
        spinner_thread.start()
        report("data/output/report.pdf", analized_data, user)
        stop_event.set()
    else:
        print("No hay datos para generar reporte.")

spinner_thread.join()
print("=================== Programa finalizado ===================")