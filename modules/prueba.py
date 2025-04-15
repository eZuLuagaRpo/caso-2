from geopy.distance import geodesic

start_coords = (60.39, 5.32)
end_coords = (60.40, 5.33)

distance = geodesic(start_coords, end_coords).kilometers
print(distance)