import requests
import pandas as pd

def getData(url,path):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        try:
            df = pd.DataFrame(data)
            df = df.iloc[0:10000] 
            print("Guardando datos en data/input/datos.xlsx ...")
            df.to_excel(f"{path}/data.xlsx",index=False)
            print("Datos obtenidos y guardados.")
        except:
            print("Error al convertir y almacenar el archivo.")
            return False
        return True
    else:
        print("Error obteniendo datos del servidor.")
        return False