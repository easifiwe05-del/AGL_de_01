import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pyarrow as pa
import pyarrow.parquet as pq
import os
from faker import Faker
import math

# Initialize Faker for realistic data generation
fake = Faker()

class AGLFleetDataGenerator:
    def __init__(self, num_vehicles=50, num_trips=500, num_gps_points=5000):
        """
        Initialize the fleet data generator
        
        Args:
            num_vehicles (int): Number of vehicles in fleet
            num_trips (int): Number of trip records
            num_gps_points (int): Number of GPS tracking points
        """
        self.num_vehicles = num_vehicles
        self.num_trips = num_trips
        self.num_gps_points = num_gps_points
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define corridors and routes
        self.corridors = {
            'Kigali-Rusumo': {
                'distance_km': 280,
                'avg_travel_time_hours': 6,
                'route_points': [
                    (-1.9441, 30.0619),  # Kigali
                    (-1.9500, 30.0500),
                    (-1.9600, 30.0600),
                    (-1.9700, 30.0700),
                    (-1.9800, 30.0800),
                    (-1.9900, 30.0900),
                    (-2.0000, 30.1000),
                    (-2.0100, 30.1100),
                    (-2.0200, 30.1200),
                    (-2.0300, 30.1300),
                    (-2.0400, 30.1400),
                    (-2.0500, 30.1500),
                    (-2.0600, 30.1600),
                    (-2.0700, 30.1700),
                    (-2.0800, 30.1800),
                    (-2.0900, 30.1900),
                    (-2.1000, 30.2000)   # Rusumo
                ],
                'toll_booths': [
                    {'name': 'Kigali Toll', 'lat': -1.9550, 'lon': 30.0650},
                    {'name': 'Rwamagana Toll', 'lat': -2.0000, 'lon': 30.1000},
                    {'name': 'Rusumo Border', 'lat': -2.0900, 'lon': 30.1900}
                ],
                'border_posts': ['Rusumo Border Post', 'Kigali Export Zone']
            },
            'Kigali-Gatuna': {
                'distance_km': 340,
                'avg_travel_time_hours': 7,
                'route_points': [
                    (-1.9441, 30.0619),  # Kigali
                    (-1.9300, 30.0500),
                    (-1.9200, 30.0400),
                    (-1.9100, 30.0300),
                    (-1.9000, 30.0200),
                    (-1.8900, 30.0100),
                    (-1.8800, 30.0000),
                    (-1.8700, 29.9900),
                    (-1.8600, 29.9800),
                    (-1.8500, 29.9700),
                    (-1.8400, 29.9600),
                    (-1.8300, 29.9500),
                    (-1.8200, 29.9400),
                    (-1.8100, 29.9300),
                    (-1.8000, 29.9200),
                    (-1.7900, 29.9100),
                    (-1.7800, 29.9000),
                    (-1.7700, 29.8900),
                    (-1.7600, 29.8800),
                    (-1.7500, 29.8700)   # Gatuna
                ],
                'toll_booths': [
                    {'name': 'Kigali Toll', 'lat': -1.9550, 'lon': 30.0650},
                    {'name': 'Musanze Toll', 'lat': -1.8300, 'lon': 29.9500},
                    {'name': 'Gatuna Border', 'lat': -1.7500, 'lon': 29.8700}
                ],
                'border_posts': ['Gatuna Border Post', 'Kigali Export Zone']
            },
            'Kigali-Gisenyi': {
                'distance_km': 250,
                'avg_travel_time_hours': 5,
                'route_points': [
                    (-1.9441, 30.0619),  # Kigali
                    (-1.9300, 30.0300),
                    (-1.9200, 30.0000),
                    (-1.9100, 29.9700),
                    (-1.9000, 29.9400),
                    (-1.8900, 29.9100),
                    (-1.8800, 29.8800),
                    (-1.8700, 29.8500),
                    (-1.8600, 29.8200),
                    (-1.8500, 29.7900),
                    (-1.8400, 29.7600),
                    (-1.8300, 29.7300),
                    (-1.8200, 29.7000),
                    (-1.8100, 29.6700),
                    (-1.8000, 29.6400),
                    (-1.7900, 29.6100),
                    (-1.7800, 29.5800),
                    (-1.7700, 29.5500)   # Gisenyi
                ],
                'toll_booths': [
                    {'name': 'Kigali Toll', 'lat': -1.9550, 'lon': 30.0650},
                    {'name': 'Rubavu Toll', 'lat': -1.7800, 'lon': 29.5800}
                ],
                'border_posts': ['Gisenyi Border Post']
            }
        }
        
        # Vehicle models and their specifications
        self.vehicle_models = [
            {'model': 'Scania R-Series', 'fuel_capacity_l': 800, 'avg_consumption_l_per_100km': 28},
            {'model': 'Mercedes Actros', 'fuel_capacity_l': 900, 'avg_consumption_l_per_100km': 30},
            {'model': 'Volvo FH', 'fuel_capacity_l': 750, 'avg_consumption_l_per_100km': 27},
            {'model': 'MAN TGX', 'fuel_capacity_l': 850, 'avg_consumption_l_per_100km': 29},
            {'model': 'DAF XF', 'fuel_capacity_l': 780, 'avg_consumption_l_per_100km': 26},
            {'model': 'Isuzu Giga', 'fuel_capacity_l': 600, 'avg_consumption_l_per_100km': 32},
            {'model': 'Hino 700', 'fuel_capacity_l': 650, 'avg_consumption_l_per_100km': 31},
            {'model': 'DAF CF', 'fuel_capacity_l': 700, 'avg_consumption_l_per_100km': 28}
        ]
        
        # Error codes for diagnostics
        self.error_codes = {
            'P001': 'Engine Coolant Temperature Too High',
            'P002': 'Engine RPM Too High',
            'P003': 'Fuel System Pressure Error',
            'P004': 'Transmission Overheating',
            'P005': 'Brake System Malfunction',
            'P006': 'Tire Pressure Too Low',
            'P007': 'Battery Voltage Too Low',
            'P008': 'Exhaust System Error',
            'P009': 'Turbocharger Error',
            'P010': 'Air Intake System Error'
        }
        
        # Maintenance types
        self.maintenance_types = [
            'Oil Change', 'Tire Replacement', 'Brake Service', 'Engine Tune-up',
            'Transmission Service', 'Cooling System Flush', 'Electrical Check',
            'Exhaust System Repair', 'Suspension Service', 'Fuel System Cleaning'
        ]
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _generate_vehicles(self):
        """Generate vehicle master data"""
        vehicles = []
        for i in range(self.num_vehicles):
            model_info = random.choice(self.vehicle_models)
            vehicle = {
                'vehicle_id': f'VEH_{i+1:06d}',
                'license_plate': fake.license_plate(),
                'model': model_info['model'],
                'year': random.randint(2015, 2025),
                'fuel_capacity_l': model_info['fuel_capacity_l'],
                'avg_consumption_l_per_100km': model_info['avg_consumption_l_per_100km'],
                'current_fuel_level': round(random.uniform(0, model_info['fuel_capacity_l']), 2),
                'odometer_reading_km': round(random.uniform(5000, 500000), 2),
                'truck_type': random.choice(['Heavy', 'Medium', 'Light']),
                'max_load_tonnes': round(random.uniform(10, 40), 2),
                'status': random.choice(['Active', 'Maintenance', 'Idle', 'Out of Service']),
                'assigned_driver': fake.name(),
                'assigned_corridor': random.choice(list(self.corridors.keys())),
                'insurance_expiry': fake.date_time_between(start_date='now', end_date='+2y'),
                'last_inspection_date': fake.date_time_between(start_date='-180d', end_date='now'),
                'next_inspection_date': fake.date_time_between(start_date='now', end_date='+90d')
            }
            vehicles.append(vehicle)
        return vehicles
    
    def _generate_engine_diagnostics(self, vehicle):
        """Generate engine diagnostic data"""
        # Base values with some variation
        rpm = random.randint(800, 2500)
        coolant_temp = random.randint(70, 110)
        fuel_pressure = round(random.uniform(2.5, 5.5), 2)
        
        # Generate random error codes (20% chance of error)
        error_codes = []
        if random.random() < 0.2:
            num_errors = random.randint(1, 3)
            error_codes = random.sample(list(self.error_codes.keys()), num_errors)
        
        return {
            'engine_rpm': rpm,
            'coolant_temp_c': coolant_temp,
            'fuel_pressure_bar': fuel_pressure,
            'battery_voltage': round(random.uniform(11.5, 14.5), 2),
            'error_codes': ','.join(error_codes) if error_codes else 'None',
            'diagnostic_timestamp': datetime.now()
        }
    
    def _generate_gps_data(self, vehicle, corridor_name, trip_start_time):
        """Generate GPS data points along a corridor"""
        corridor = self.corridors[corridor_name]
        route_points = corridor['route_points']
        
        gps_points = []
        num_points = random.randint(20, 50)
        
        # Calculate total distance and speed
        total_distance = corridor['distance_km']
        avg_speed = total_distance / corridor['avg_travel_time_hours']
        
        for i in range(num_points):
            # Calculate position along route
            progress = i / num_points
            idx = int(progress * (len(route_points) - 1))
            next_idx = min(idx + 1, len(route_points) - 1)
            
            # Interpolate between route points
            frac = (progress * (len(route_points) - 1)) - idx
            lat = route_points[idx][0] + (route_points[next_idx][0] - route_points[idx][0]) * frac
            lon = route_points[idx][1] + (route_points[next_idx][1] - route_points[idx][1]) * frac
            
            # Add some random variation for realism
            lat += random.uniform(-0.001, 0.001)
            lon += random.uniform(-0.001, 0.001)
            
            # Calculate time and speed
            time_offset = (progress * corridor['avg_travel_time_hours'] * 3600)  # in seconds
            timestamp = trip_start_time + timedelta(seconds=time_offset)
            
            # Add random speed variation
            speed = avg_speed * random.uniform(0.6, 1.4)
            speed = max(0, min(speed, 90))  # Cap at 90 km/h
            
            # Calculate heading
            heading = random.uniform(0, 360)
            
            # Determine if near toll booth or border
            near_toll = False
            near_border = False
            toll_name = None
            border_name = None
            
            for toll in corridor['toll_booths']:
                distance = self._calculate_distance(lat, lon, toll['lat'], toll['lon'])
                if distance < 0.5:  # Within 0.5 km
                    near_toll = True
                    toll_name = toll['name']
                    break
            
            for border in corridor['border_posts']:
                # Approximate border location
                if 'Rusumo' in border and abs(lat - (-2.0900)) < 0.01:
                    near_border = True
                    border_name = border
                elif 'Gatuna' in border and abs(lat - (-1.7500)) < 0.01:
                    near_border = True
                    border_name = border
                elif 'Gisenyi' in border and abs(lat - (-1.7800)) < 0.01:
                    near_border = True
                    border_name = border
            
            gps_point = {
                'vehicle_id': vehicle['vehicle_id'],
                'trip_id': f'TRIP_{random.randint(1, 9999):06d}',
                'corridor_name': corridor_name,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'altitude_m': round(random.uniform(1200, 1800), 2),
                'speed_kmh': round(speed, 2),
                'heading_deg': round(heading, 2),
                'timestamp': timestamp,
                'near_toll_booth': near_toll,
                'toll_booth_name': toll_name,
                'near_border_post': near_border,
                'border_post_name': border_name,
                'geofence_entry': near_border or near_toll,
                'geofence_exit': False,  # Will be set when leaving geofence
                'distance_traveled_km': round(progress * total_distance, 2)
            }
            gps_points.append(gps_point)
        
        # Set geofence exit for points after toll/border
        for i, point in enumerate(gps_points):
            if point['geofence_entry'] and i < len(gps_points) - 1:
                gps_points[i+1]['geofence_exit'] = True
        
        return gps_points
    
    def _generate_maintenance_logs(self, vehicles):
        """Generate maintenance log data"""
        maintenance_logs = []
        
        for vehicle in vehicles:
            # Each vehicle has 1-5 maintenance records
            num_records = random.randint(1, 5)
            
            for i in range(num_records):
                service_date = fake.date_time_between(start_date='-365d', end_date='now')
                next_service = service_date + timedelta(days=random.randint(30, 180))
                
                log = {
                    'maintenance_id': f'MTN_{uuid.uuid4().hex[:8].upper()}',
                    'vehicle_id': vehicle['vehicle_id'],
                    'maintenance_type': random.choice(self.maintenance_types),
                    'service_date': service_date,
                    'next_maintenance_date': next_service,
                    'cost': round(random.uniform(100, 2000), 2),
                    'duration_hours': round(random.uniform(1, 8), 2),
                    'technician_name': fake.name(),
                    'service_center': fake.company(),
                    'description': fake.text(max_nb_chars=100),
                    'parts_replaced': random.choice([
                        'Oil filter, Air filter', 'Brake pads, Discs', 'Tires',
                        'Engine oil, Filter', 'Transmission fluid', 'Battery',
                        'Spark plugs', 'Alternator', 'Water pump', 'None'
                    ]),
                    'tire_pressure_front_kpa': round(random.uniform(550, 650), 2),
                    'tire_pressure_rear_kpa': round(random.uniform(600, 700), 2),
                    'breakdown_recorded': random.choice([True, False]) if random.random() < 0.3 else False,
                    'breakdown_description': fake.text(max_nb_chars=80) if random.random() < 0.3 else None,
                    'status': random.choice(['Completed', 'In Progress', 'Scheduled', 'Cancelled'])
                }
                maintenance_logs.append(log)
        
        return maintenance_logs
    
    def _generate_trip_data(self, vehicles):
        """Generate trip data for vehicles"""
        trips = []
        
        for i in range(self.num_trips):
            vehicle = random.choice(vehicles)
            corridor_name = random.choice(list(self.corridors.keys()))
            corridor = self.corridors[corridor_name]
            
            # Generate trip dates
            start_date = fake.date_time_between(start_date='-90d', end_date='now')
            end_date = start_date + timedelta(hours=corridor['avg_travel_time_hours'] * random.uniform(0.8, 1.4))
            
            # Generate trip metrics
            planned_distance = corridor['distance_km']
            actual_distance = planned_distance * random.uniform(0.95, 1.15)
            fuel_consumed = (actual_distance / 100) * vehicle['avg_consumption_l_per_100km'] * random.uniform(0.85, 1.15)
            
            trip = {
                'trip_id': f'TRIP_{i+1:08d}',
                'vehicle_id': vehicle['vehicle_id'],
                'corridor_name': corridor_name,
                'start_location': 'Kigali',
                'end_location': corridor_name.split('-')[1] if '-' in corridor_name else 'Unknown',
                'planned_distance_km': round(planned_distance, 2),
                'actual_distance_km': round(actual_distance, 2),
                'planned_duration_hours': corridor['avg_travel_time_hours'],
                'actual_duration_hours': round((end_date - start_date).total_seconds() / 3600, 2),
                'start_time': start_date,
                'end_time': end_date,
                'fuel_consumed_liters': round(fuel_consumed, 2),
                'avg_speed_kmh': round(actual_distance / ((end_date - start_date).total_seconds() / 3600), 2),
                'max_speed_kmh': round(random.uniform(60, 95), 2),
                'idle_time_minutes': round(random.uniform(10, 60), 2),
                'toll_booths_passed': random.randint(1, 5),
                'border_crossings': random.randint(0, 2),
                'delay_minutes': random.randint(0, 120) if random.random() < 0.3 else 0,
                'delay_reason': random.choice(['Traffic', 'Customs', 'Weather', 'Accident', 'Breakdown', 'None']),
                'cargo_weight_tonnes': round(random.uniform(5, vehicle['max_load_tonnes']), 2),
                'cargo_type': random.choice(['General', 'Perishable', 'Hazardous', 'Oversized']),
                'temperature_c': round(random.uniform(15, 35), 2),
                'humidity_percent': round(random.uniform(30, 90), 2),
                'driver_name': vehicle['assigned_driver'],
                'status': random.choice(['Completed', 'In Progress', 'Scheduled', 'Delayed', 'Cancelled'])
            }
            trips.append(trip)
        
        return trips
    
    def _generate_asset_telematics(self, vehicles, trips):
        """Generate real-time telematics data for vehicles"""
        telematics = []
        
        for vehicle in vehicles:
            if vehicle['status'] == 'Active':
                num_readings = random.randint(10, 30)
                
                for i in range(num_readings):
                    timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
                    
                    # Generate realistic fluctuations
                    fuel_level = vehicle['current_fuel_level'] * random.uniform(0.7, 1.0)
                    fuel_level = max(0, min(fuel_level, vehicle['fuel_capacity_l']))
                    
                    diagnostics = self._generate_engine_diagnostics(vehicle)
                    
                    telemetric = {
                        'reading_id': f'TEL_{uuid.uuid4().hex[:8].upper()}',
                        'vehicle_id': vehicle['vehicle_id'],
                        'timestamp': timestamp,
                        'fuel_level_l': round(fuel_level, 2),
                        'fuel_consumption_rate_l_per_100km': round(
                            vehicle['avg_consumption_l_per_100km'] * random.uniform(0.8, 1.2), 2
                        ),
                        'odometer_reading_km': round(
                            vehicle['odometer_reading_km'] + random.uniform(0, 500), 2
                        ),
                        'engine_rpm': diagnostics['engine_rpm'],
                        'coolant_temp_c': diagnostics['coolant_temp_c'],
                        'fuel_pressure_bar': diagnostics['fuel_pressure_bar'],
                        'battery_voltage': diagnostics['battery_voltage'],
                        'error_codes': diagnostics['error_codes'],
                        'engine_load_percent': round(random.uniform(10, 95), 2),
                        'transmission_temp_c': round(random.uniform(60, 120), 2),
                        'brake_pressure_bar': round(random.uniform(5, 15), 2),
                        'tire_pressure_front_kpa': round(random.uniform(550, 650), 2),
                        'tire_pressure_rear_kpa': round(random.uniform(600, 700), 2),
                        'is_engine_running': random.random() > 0.2,
                        'is_moving': random.random() > 0.3,
                        'latitude': round(random.uniform(-2.2, -1.5), 6),
                        'longitude': round(random.uniform(29.5, 30.5), 6),
                        'speed_kmh': round(random.uniform(0, 90), 2)
                    }
                    telematics.append(telemetric)
        
        return telematics
    
    def generate_data(self):
        """Generate all fleet data"""
        # Generate vehicles
        self.vehicles = self._generate_vehicles()
        
        # Generate trips
        self.trips = self._generate_trip_data(self.vehicles)
        
        # Generate GPS data (sample for some trips)
        self.gps_data = []
        for vehicle in self.vehicles[:min(10, len(self.vehicles))]:  # Limit for performance
            if vehicle['status'] == 'Active':
                corridor = random.choice(list(self.corridors.keys()))
                trip_start = datetime.now() - timedelta(hours=random.randint(1, 48))
                gps_points = self._generate_gps_data(vehicle, corridor, trip_start)
                self.gps_data.extend(gps_points)
        
        # Generate maintenance logs
        self.maintenance_logs = self._generate_maintenance_logs(self.vehicles)
        
        # Generate telematics data
        self.telematics = self._generate_asset_telematics(self.vehicles, self.trips)
        
        # Convert to DataFrames
        self.vehicles_df = pd.DataFrame(self.vehicles)
        self.trips_df = pd.DataFrame(self.trips)
        self.gps_df = pd.DataFrame(self.gps_data)
        self.maintenance_df = pd.DataFrame(self.maintenance_logs)
        self.telematics_df = pd.DataFrame(self.telematics)
        
        # Convert datetime columns
        datetime_cols_vehicles = ['insurance_expiry', 'last_inspection_date', 'next_inspection_date']
        for col in datetime_cols_vehicles:
            if col in self.vehicles_df.columns:
                self.vehicles_df[col] = pd.to_datetime(self.vehicles_df[col])
        
        datetime_cols_trips = ['start_time', 'end_time']
        for col in datetime_cols_trips:
            if col in self.trips_df.columns:
                self.trips_df[col] = pd.to_datetime(self.trips_df[col])
        
        datetime_cols_maintenance = ['service_date', 'next_maintenance_date']
        for col in datetime_cols_maintenance:
            if col in self.maintenance_df.columns:
                self.maintenance_df[col] = pd.to_datetime(self.maintenance_df[col])
        
        if 'timestamp' in self.gps_df.columns:
            self.gps_df['timestamp'] = pd.to_datetime(self.gps_df['timestamp'])
        
        if 'timestamp' in self.telematics_df.columns:
            self.telematics_df['timestamp'] = pd.to_datetime(self.telematics_df['timestamp'])
        
        return {
            'vehicles': self.vehicles_df,
            'trips': self.trips_df,
            'gps_data': self.gps_df,
            'maintenance': self.maintenance_df,
            'telematics': self.telematics_df
        }
    
    def save_csv(self, output_dir='agl_fleet_data_output'):
        """Save all data as CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.vehicles_df.to_csv(os.path.join(output_dir, 'vehicles.csv'), index=False)
        self.trips_df.to_csv(os.path.join(output_dir, 'trips.csv'), index=False)
        self.gps_df.to_csv(os.path.join(output_dir, 'gps_tracking.csv'), index=False)
        self.maintenance_df.to_csv(os.path.join(output_dir, 'maintenance_logs.csv'), index=False)
        self.telematics_df.to_csv(os.path.join(output_dir, 'telematics.csv'), index=False)
        
        print(f"CSV files saved to {output_dir}")
    
    def save_parquet(self, output_dir='agl_fleet_data_output'):
        """Save all data as Parquet"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.vehicles_df.to_parquet(os.path.join(output_dir, 'vehicles.parquet'), index=False)
        self.trips_df.to_parquet(os.path.join(output_dir, 'trips.parquet'), index=False)
        self.gps_df.to_parquet(os.path.join(output_dir, 'gps_tracking.parquet'), index=False)
        self.maintenance_df.to_parquet(os.path.join(output_dir, 'maintenance_logs.parquet'), index=False)
        self.telematics_df.to_parquet(os.path.join(output_dir, 'telematics.parquet'), index=False)
        
        print(f"Parquet files saved to {output_dir}")
    
    def save_json(self, output_dir='agl_fleet_data_output'):
        """Save all data as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(df):
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64']).columns:
                df_copy[col] = df_copy[col].astype(str)
            return df_copy
        
        convert_datetime(self.vehicles_df).to_json(
            os.path.join(output_dir, 'vehicles.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.trips_df).to_json(
            os.path.join(output_dir, 'trips.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.gps_df).to_json(
            os.path.join(output_dir, 'gps_tracking.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.maintenance_df).to_json(
            os.path.join(output_dir, 'maintenance_logs.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.telematics_df).to_json(
            os.path.join(output_dir, 'telematics.json'), orient='records', date_format='iso'
        )
        
        print(f"JSON files saved to {output_dir}")
    
    def save_xml(self, output_dir='agl_fleet_data_output'):
        """Save all data as XML"""
        os.makedirs(output_dir, exist_ok=True)
        
        def df_to_xml(df, root_name, element_name, filepath):
            root = ET.Element(root_name)
            
            for _, row in df.iterrows():
                elem = ET.SubElement(root, element_name)
                for col in df.columns:
                    child = ET.SubElement(elem, col.replace('_', ''))
                    value = row[col]
                    if pd.isna(value):
                        child.text = ''
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        child.text = value.isoformat()
                    else:
                        child.text = str(value)
            
            xml_str = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
        
        df_to_xml(self.vehicles_df, 'Vehicles', 'Vehicle', 
                  os.path.join(output_dir, 'vehicles.xml'))
        df_to_xml(self.trips_df, 'Trips', 'Trip', 
                  os.path.join(output_dir, 'trips.xml'))
        df_to_xml(self.gps_df, 'GPSTracking', 'GPSPoint', 
                  os.path.join(output_dir, 'gps_tracking.xml'))
        df_to_xml(self.maintenance_df, 'MaintenanceLogs', 'Maintenance', 
                  os.path.join(output_dir, 'maintenance_logs.xml'))
        df_to_xml(self.telematics_df, 'Telematics', 'Reading', 
                  os.path.join(output_dir, 'telematics.xml'))
        
        print(f"XML files saved to {output_dir}")
    
    def save_all_formats(self, output_dir='agl_fleet_data_output'):
        """Save all data in all formats"""
        print("\n" + "=" * 60)
        print("Saving fleet data in multiple formats...")
        print("=" * 60)
        
        self.save_csv(output_dir)
        self.save_parquet(output_dir)
        self.save_json(output_dir)
        self.save_xml(output_dir)
        
        print("\nAll fleet data files saved successfully!")

def main():
    """Main function to run the fleet data generator"""
    print("=" * 60)
    print("AGL Rwanda - Transportation & Fleet Data Generator")
    print("=" * 60)
    
    # Initialize generator
    print("\nInitializing fleet data generator...")
    generator = AGLFleetDataGenerator(
        num_vehicles=50,
        num_trips=500,
        num_gps_points=5000
    )
    
    # Generate data
    print("Generating fleet data...")
    data = generator.generate_data()
    
    # Display statistics
    print(f"\nData generated:")
    print(f"  - Vehicles: {len(data['vehicles'])}")
    print(f"  - Trips: {len(data['trips'])}")
    print(f"  - GPS tracking points: {len(data['gps_data'])}")
    print(f"  - Maintenance logs: {len(data['maintenance'])}")
    print(f"  - Telematics readings: {len(data['telematics'])}")
    
    # Display sample data
    print("\nSample Vehicle Data:")
    print(data['vehicles'].head())
    
    print("\nSample Trip Data:")
    print(data['trips'].head())
    
    print("\nSample GPS Tracking Data:")
    print(data['gps_data'].head())
    
    print("\nSample Maintenance Log:")
    print(data['maintenance'].head())
    
    print("\nSample Telematics Data:")
    print(data['telematics'].head())
    
    # Save in all formats
    generator.save_all_formats()
    
    print("\n" + "=" * 60)
    print("Fleet data generation complete!")
    print("Check the 'agl_fleet_data_output' directory for all files")
    print("=" * 60)
    
    return generator

if __name__ == "__main__":
    # Install required packages if missing
    required_packages = ['pandas', 'numpy', 'faker', 'pyarrow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {missing_packages}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
    else:
        generator = main()