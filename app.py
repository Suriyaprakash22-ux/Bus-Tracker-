from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random
import json

app = Flask(__name__)

# Bus routes data
BUS_ROUTES = {
    'trichy': {
        'name': 'Trichy',
        'routes': [
            {'id': 'T1', 'name': 'Trichy - Central Station', 'stops': ['Central Bus Stand', 'Railway Station', 'Airport', 'BHEL Township']},
            {'id': 'T2', 'name': 'Trichy - Srirangam', 'stops': ['Central Bus Stand', 'Srirangam Temple', 'Rockfort', 'Main Guard Gate']},
            {'id': 'T3', 'name': 'Trichy - Airport', 'stops': ['Central Bus Stand', 'Airport', 'BHEL Township', 'Thanjavur Road']},
        ]
    },
    'coimbatore': {
        'name': 'Coimbatore',
        'routes': [
            {'id': 'C1', 'name': 'Trichy - Coimbatore', 'stops': ['Trichy Central', 'Karur', 'Erode', 'Coimbatore Central']},
            {'id': 'C2', 'name': 'Coimbatore - Mettupalayam', 'stops': ['Coimbatore Central', 'Gandhipuram', 'Mettupalayam']},
        ]
    },
    'chennai': {
        'name': 'Chennai',
        'routes': [
            {'id': 'CH1', 'name': 'Trichy - Chennai', 'stops': ['Trichy Central', 'Villupuram', 'Chengalpattu', 'Chennai Central']},
            {'id': 'CH2', 'name': 'Chennai - Airport', 'stops': ['Chennai Central', 'T.Nagar', 'Airport']},
        ]
    },
    'trichy_areas': {
        'name': 'Inside Trichy Areas',
        'routes': [
            {'id': 'TA1', 'name': 'Central - Srirangam', 'stops': ['Central Bus Stand', 'Woraiyur', 'Srirangam', 'Tiruvanaikoil']},
            {'id': 'TA2', 'name': 'Central - Rockfort', 'stops': ['Central Bus Stand', 'Main Guard Gate', 'Rockfort', 'Chathiram Bus Stand']},
            {'id': 'TA3', 'name': 'Central - BHEL', 'stops': ['Central Bus Stand', 'BHEL Township', 'Thuvakudi', 'Golden Rock']},
            {'id': 'TA4', 'name': 'Central - Airport', 'stops': ['Central Bus Stand', 'Airport', 'Thanjavur Road', 'Ponmalai']},
        ]
    }
}

# Simulated bus locations (in real app, this would come from GPS)
bus_locations = {}

def initialize_bus_locations():
    """Initialize bus locations for all routes"""
    for city, city_data in BUS_ROUTES.items():
        for route in city_data['routes']:
            for i in range(1, 4):  # 3 buses per route
                bus_id = f"{route['id']}-{i}"
                # Randomly place bus at one of the stops
                current_stop_index = random.randint(0, len(route['stops']) - 1)
                bus_locations[bus_id] = {
                    'route_id': route['id'],
                    'route_name': route['name'],
                    'current_stop': route['stops'][current_stop_index],
                    'current_stop_index': current_stop_index,
                    'next_stop': route['stops'][(current_stop_index + 1) % len(route['stops'])],
                    'stops': route['stops'],
                    'city': city,
                    'eta': random.randint(2, 15),  # ETA in minutes
                    'status': random.choice(['On Time', 'Delayed', 'Early']),
                    'last_updated': datetime.now().isoformat()
                }

# Initialize bus locations on startup
initialize_bus_locations()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', routes=BUS_ROUTES)

@app.route('/route/<city>')
def route_view(city):
    """Route view for a specific city"""
    if city not in BUS_ROUTES:
        return render_template('404.html'), 404
    return render_template('route.html', city=city, city_data=BUS_ROUTES[city])

@app.route('/track/<route_id>')
def track_route(route_id):
    """Track a specific route"""
    # Find the route
    route_info = None
    city_name = None
    for city, city_data in BUS_ROUTES.items():
        for route in city_data['routes']:
            if route['id'] == route_id:
                route_info = route
                city_name = city
                break
        if route_info:
            break
    
    if not route_info:
        return render_template('404.html'), 404
    
    # Get buses for this route
    route_buses = [bus for bus_id, bus in bus_locations.items() if bus['route_id'] == route_id]
    
    return render_template('track.html', route=route_info, buses=route_buses, city=city_name)

@app.route('/api/buses')
def api_buses():
    """API endpoint to get all bus locations"""
    city = request.args.get('city', None)
    route_id = request.args.get('route_id', None)
    
    filtered_buses = bus_locations.copy()
    
    if city:
        filtered_buses = {k: v for k, v in filtered_buses.items() if v['city'] == city}
    
    if route_id:
        filtered_buses = {k: v for k, v in filtered_buses.items() if v['route_id'] == route_id}
    
    return jsonify(filtered_buses)

@app.route('/api/bus/<bus_id>')
def api_bus_detail(bus_id):
    """API endpoint to get specific bus details"""
    if bus_id not in bus_locations:
        return jsonify({'error': 'Bus not found'}), 404
    
    # Simulate movement (in real app, this would be GPS data)
    bus = bus_locations[bus_id]
    # Randomly update position occasionally
    if random.random() < 0.3:  # 30% chance to update
        current_index = bus['current_stop_index']
        if current_index < len(bus['stops']) - 1:
            bus['current_stop_index'] = current_index + 1
        else:
            bus['current_stop_index'] = 0  # Loop back
        bus['current_stop'] = bus['stops'][bus['current_stop_index']]
        bus['next_stop'] = bus['stops'][(bus['current_stop_index'] + 1) % len(bus['stops'])]
        bus['eta'] = random.randint(2, 15)
        bus['last_updated'] = datetime.now().isoformat()
    
    return jsonify(bus)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

