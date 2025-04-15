from geopy.distance import geodesic

def test_geodesic_with_nulls():
    # Casos de prueba
    test_cases = [
        # Caso 1: Coordenadas válidas
        {
            "start_coords": (60.39, 5.32),
            "end_coords": (60.40, 5.33),
            "desc": "Coordenadas válidas"
        },
        # Caso 2: start_latitude es None
        {
            "start_coords": (None, 5.32),
            "end_coords": (60.40, 5.33),
            "desc": "start_latitude es None"
        },
        # Caso 3: start_longitude es None
        {
            "start_coords": (60.39, None),
            "end_coords": (60.40, 5.33),
            "desc": "start_longitude es None"
        },
        # Caso 4: end_latitude es None
        {
            "start_coords": (60.39, 5.32),
            "end_coords": (None, 5.33),
            "desc": "end_latitude es None"
        },
        # Caso 5: Todas None
        {
            "start_coords": (None, None),
            "end_coords": (None, None),
            "desc": "Todas None"
        }
    ]

    for case in test_cases:
        print(f"\nProbando: {case['desc']}")
        try:
            distance = geodesic(case["start_coords"], case["end_coords"]).kilometers
            print(f"Resultado: {distance} km")
        except Exception as e:
            print(f"Error: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    test_geodesic_with_nulls()