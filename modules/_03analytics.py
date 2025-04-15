from ._01authentication import Authentication
from ._02request import getData
from ._04report import report
import pandas as pd
from geopy.distance import geodesic

class Analytics:
    def __init__(self):
        pass

    def AnalizeData(self):
        print("Leyendo datos...")
        data = pd.read_excel("data/input/data.xlsx")

        print("Analizando datos...")

        # Borrar duplicados
        data = data[data["start_station_name"] != data["end_station_name"]]

        # Rutas más populares
        data["route"] = data["start_station_name"] + " to " + data["end_station_name"]
        most_popular_routes = data["route"].value_counts().reset_index().head(10)

        # Distancias más grandes entre estaciones
        def CalculateDistance(row):
            start_coords = (row["start_station_latitude"], row["start_station_longitude"])
            end_coords = (row["end_station_latitude"], row["end_station_longitude"])
            return geodesic(start_coords, end_coords).kilometers

        data["distance_km"] = data.apply(CalculateDistance, axis=1)
        distance_between_routes = data[["route","distance_km"]].sort_values(by="distance_km", ascending=False).drop_duplicates().reset_index().drop(columns="index").head(10)

        # Mayor duración promedio
        average_route_durations = data.groupby('route').agg(
            avg_duration=('duration', 'mean'),
            trip_count=('route', 'count')
        ).reset_index()
        
        def CalculateStats(series):
                return {
                    "Promedio": series.mean(),
                    "Varianza": series.var(),
                    "Desviación Estándar": series.std(),
                    "Máximo": series.max(),
                    "Mínimo": series.min(),
                    "Percentil 25%": series.quantile(0.25),
                    "Mediana (50%)": series.quantile(0.50),
                    "Percentil 75%": series.quantile(0.75)
                } 
        # Calcular estadísticas para la duración
        duration_stats = CalculateStats(data["duration"])
        duration_stats_df = pd.DataFrame(duration_stats, index=["Duración de Viajes"])
        
        # Calcular estadísticas para la distancia
        distance_stats = CalculateStats(data["distance_km"])
        distance_stats_df = pd.DataFrame(distance_stats, index=["Distancia (km)"])

        stats_table = pd.concat([duration_stats_df, distance_stats_df])

        
        longest_duration_routes = average_route_durations.sort_values(by='avg_duration', ascending=False).reset_index().drop(columns="index").head(10)

        self.analizedData = {"data":data, "most_popular_routes": most_popular_routes, "distance_between_routes":distance_between_routes, "longest_duration_routes":longest_duration_routes, "stats_table": stats_table}
        return self.analizedData

