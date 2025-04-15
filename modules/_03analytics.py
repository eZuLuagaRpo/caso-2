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

        longest_duration_routes = average_route_durations.sort_values(by='avg_duration', ascending=False).reset_index().drop(columns="index").head(10)

        # New analysis for duration and distance statistics
        data['duration']
        duration_stats = {
            'mean': data['duration'].mean(),
            'variance': data['duration'].var(),
            'std_dev': data['duration'].std(),
            'max': data['duration'].max(),
            'min': data['duration'].min(),
            '25th_percentile': data['duration'].quantile(0.25),
            '50th_percentile': data['duration'].quantile(0.50),
            '75th_percentile': data['duration'].quantile(0.75)
        }

        distance_stats = {
            'mean': data['distance_km'].mean(),
            'variance': data['distance_km'].var(),
            'std_dev': data['distance_km'].std(),
            'max': data['distance_km'].max(),
            'min': data['distance_km'].min(),
            '25th_percentile': data['distance_km'].quantile(0.25),
            '50th_percentile': data['distance_km'].quantile(0.50),
            '75th_percentile': data['distance_km'].quantile(0.75)
        }

        # Combine stats into a single DataFrame for reporting
        stats_df = pd.DataFrame({
            'Statistic': ['Mean', 'Variance', 'Standard Deviation', 'Max', 'Min', '25th Percentile', '50th Percentile', '75th Percentile'],
            'Duration': [duration_stats['mean'], duration_stats['variance'], duration_stats['std_dev'], duration_stats['max'], duration_stats['min'], duration_stats['25th_percentile'], duration_stats['50th_percentile'], duration_stats['75th_percentile']],
            'Distance (km)': [distance_stats['mean'], distance_stats['variance'], distance_stats['std_dev'], distance_stats['max'], distance_stats['min'], distance_stats['25th_percentile'], distance_stats['50th_percentile'], distance_stats['75th_percentile']]
        })

        self.analizedData = {
            "data": data,
            "most_popular_routes": most_popular_routes,
            "distance_between_routes": distance_between_routes,
            "longest_duration_routes": longest_duration_routes,
            "stats": stats_df  # Add the new stats DataFrame
        }
        return self.analizedData
    
        
        
    
    
