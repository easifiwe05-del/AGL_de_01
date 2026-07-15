import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from faker import Faker
import hashlib
import base64

# Initialize Faker for realistic data generation
fake = Faker()

class AGLDriverMonitoringGenerator:
    def __init__(self, num_drivers=200, num_trips=500, num_events=10000):
        """
        Initialize the driver monitoring data generator
        
        Args:
            num_drivers (int): Number of drivers in the system
            num_trips (int): Number of trip records
            num_events (int): Number of behavioral events
        """
        self.num_drivers = num_drivers
        self.num_trips = num_trips
        self.num_events = num_events
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define driver statuses
        self.driver_statuses = ['Active', 'Inactive', 'On Leave', 'Suspended', 'Training']
        self.duty_statuses = ['On Duty', 'Driving', 'Off Duty', 'Sleeper Berth', 'Loading/Unloading']
        
        # Define event types
        self.event_types = [
            'Harsh Braking',
            'Rapid Acceleration',
            'Sharp Cornering',
            'Excessive Idling',
            'Seatbelt Violation',
            'Speeding',
            'Lane Departure',
            'Following Distance'
        ]
        
        # Define severity levels
        self.severity_levels = ['Low', 'Medium', 'High', 'Critical']
        
        # Define fatigue indicators
        self.fatigue_indicators = [
            'Yawning',
            'Eye Closure',
            'Head Nodding',
            'Drowsiness',
            'Distraction',
            'Mobile Phone Usage',
            'Reaction Delay'
        ]
        
        # Define vehicle types
        self.vehicle_types = ['Truck', 'Trailer', 'Van', 'Bus', 'Heavy Equipment']
        
        # Define app interaction states
        self.app_states = ['Active', 'Background', 'Idle', 'Offline', 'Syncing']
        
        # Define inspection checklist items
        self.inspection_items = [
            'Engine Oil Level',
            'Coolant Level',
            'Brake Fluid',
            'Tire Pressure',
            'Lights',
            'Signals',
            'Windshield',
            'Mirrors',
            'Horn',
            'Seatbelt',
            'Emergency Brake',
            'Steering Wheel',
            'Transmission',
            'Battery',
            'Fuel Level'
        ]
    
    def _generate_drivers(self):
        """Generate driver master data"""
        drivers = []
        for i in range(self.num_drivers):
            driver = {
                'driver_id': f'DRV_{i+1:06d}',
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'license_number': f'DL{fake.random_number(digits=8)}',
                'license_class': random.choice(['A', 'B', 'C', 'D', 'E', 'F']),
                'license_expiry': datetime.now() + timedelta(days=random.randint(30, 730)),
                'date_of_birth': datetime.now() - timedelta(days=random.randint(7300, 20000)),
                'hire_date': datetime.now() - timedelta(days=random.randint(30, 3650)),
                'status': random.choice(self.driver_statuses),
                'vehicle_type': random.choice(self.vehicle_types),
                'home_terminal': fake.city(),
                'emergency_contact': fake.name(),
                'emergency_phone': fake.phone_number(),
                'total_experience_years': round(random.uniform(1, 30), 1),
                'last_medical_exam': datetime.now() - timedelta(days=random.randint(1, 365)),
                'next_medical_exam': datetime.now() + timedelta(days=random.randint(1, 365)),
                'preferred_language': random.choice(['English', 'Kinyarwanda', 'French', 'Swahili']),
                'rating': round(random.uniform(3.5, 5.0), 2),
                'total_missions': random.randint(10, 500),
                'total_km_driven': round(random.uniform(10000, 500000), 2)
            }
            drivers.append(driver)
        return drivers
    
    def _generate_behavioral_events(self, drivers):
        """Generate behavioral telematics events"""
        events = []
        
        for i in range(self.num_events):
            driver = random.choice(drivers)
            
            # Generate event timestamp (within last 30 days)
            event_time = datetime.now() - timedelta(days=random.randint(0, 30))
            event_time += timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # Generate event type with realistic probabilities
            event_type = random.choices(
                self.event_types,
                weights=[0.25, 0.15, 0.15, 0.20, 0.10, 0.08, 0.05, 0.02],
                k=1
            )[0]
            
            # Generate event details
            event = {
                'event_id': f'EVT_{uuid.uuid4().hex[:8].upper()}',
                'driver_id': driver['driver_id'],
                'event_type': event_type,
                'timestamp': event_time,
                'severity': random.choice(self.severity_levels),
                'latitude': round(random.uniform(-2.2, -1.5), 6),
                'longitude': round(random.uniform(29.5, 30.5), 6),
                'speed_kmh': round(random.uniform(0, 90), 2),
                'acceleration_g': round(random.uniform(-1.5, 1.5), 3),
                'brake_pressure_percent': round(random.uniform(0, 100), 2),
                'steering_angle_deg': round(random.uniform(-45, 45), 2),
                'engine_rpm': random.randint(800, 2500),
                'gear_position': random.randint(0, 12),
                'vehicle_id': f'VEH_{random.randint(1, 50):04d}',
                'weather_condition': random.choice(['Clear', 'Rain', 'Fog', 'Snow', 'Windy']),
                'road_condition': random.choice(['Good', 'Fair', 'Poor', 'Construction']),
                'traffic_density': random.choice(['Light', 'Moderate', 'Heavy', 'Gridlock'])
            }
            
            # Add event-specific fields
            if event_type == 'Harsh Braking':
                event['deceleration_rate'] = round(random.uniform(0.5, 1.5), 2)
                event['distance_to_obstacle_m'] = round(random.uniform(5, 30), 2)
            elif event_type == 'Rapid Acceleration':
                event['acceleration_rate'] = round(random.uniform(0.5, 2.0), 2)
                event['engine_load_percent'] = round(random.uniform(60, 100), 2)
            elif event_type == 'Sharp Cornering':
                event['lateral_acceleration'] = round(random.uniform(0.3, 0.8), 3)
                event['curve_radius_m'] = round(random.uniform(20, 100), 2)
            elif event_type == 'Excessive Idling':
                event['idle_duration_minutes'] = round(random.uniform(5, 60), 2)
                event['fuel_consumed_l'] = round(random.uniform(0.5, 5.0), 2)
            elif event_type == 'Seatbelt Violation':
                event['duration_unbuckled_seconds'] = random.randint(10, 300)
                event['warning_count'] = random.randint(1, 5)
            elif event_type == 'Speeding':
                event['speed_limit_kmh'] = random.choice([40, 60, 80, 100, 120])
                event['excess_speed_kmh'] = round(random.uniform(5, 30), 2)
            
            events.append(event)
        
        return events
    
    def _generate_app_telematics(self, drivers):
        """Generate mobile app telematics data"""
        app_data = []
        
        for driver in drivers:
            if driver['status'] == 'Active':
                # Generate app sessions for the last 30 days
                num_sessions = random.randint(5, 30)
                
                for i in range(num_sessions):
                    session_start = datetime.now() - timedelta(days=random.randint(0, 30))
                    session_start += timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    
                    # Session duration: 15 minutes to 12 hours
                    session_duration_seconds = random.randint(900, 43200)
                    session_end = session_start + timedelta(seconds=session_duration_seconds)
                    
                    # Generate app interactions
                    app_data.append({
                        'session_id': f'APP_{uuid.uuid4().hex[:8].upper()}',
                        'driver_id': driver['driver_id'],
                        'login_time': session_start,
                        'logout_time': session_end,
                        'app_active_time_seconds': random.randint(300, session_duration_seconds),
                        'app_state': random.choice(self.app_states),
                        'device_id': f'DEV_{uuid.uuid4().hex[:6]}',
                        'device_type': random.choice(['iOS', 'Android', 'Web']),
                        'app_version': f'{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
                        'screen_interactions': random.randint(10, 200),
                        'screen_state': random.choice(['Foreground', 'Background', 'Locked']),
                        'data_sync_status': random.choice(['Synced', 'Pending', 'Failed', 'Partial']),
                        'offline_data_size_mb': round(random.uniform(0.5, 50), 2),
                        'sync_delay_seconds': random.randint(0, 300),
                        'battery_level_at_login': round(random.uniform(20, 100), 2),
                        'network_type': random.choice(['4G', '5G', 'WiFi', 'Offline']),
                        'signal_strength': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
                        'last_known_location': {
                            'lat': round(random.uniform(-2.2, -1.5), 6),
                            'lon': round(random.uniform(29.5, 30.5), 6)
                        }
                    })
        
        return app_data
    
    def _generate_driver_logs(self, drivers):
        """Generate Hours of Service (HoS) and duty logs"""
        logs = []
        
        for driver in drivers:
            # Generate logs for the last 30 days
            num_days = random.randint(5, 30)
            
            for day in range(num_days):
                log_date = datetime.now() - timedelta(days=day)
                
                # Generate multiple status changes throughout the day
                num_status_changes = random.randint(3, 10)
                current_time = log_date.replace(hour=6, minute=0, second=0)  # Start at 6 AM
                
                for i in range(num_status_changes):
                    status = random.choice(self.duty_statuses)
                    duration_minutes = random.randint(15, 480)
                    
                    log = {
                        'log_id': f'LOG_{uuid.uuid4().hex[:8].upper()}',
                        'driver_id': driver['driver_id'],
                        'duty_status': status,
                        'start_time': current_time,
                        'end_time': current_time + timedelta(minutes=duration_minutes),
                        'duration_minutes': duration_minutes,
                        'vehicle_id': f'VEH_{random.randint(1, 50):04d}',
                        'location': fake.city(),
                        'latitude': round(random.uniform(-2.2, -1.5), 6),
                        'longitude': round(random.uniform(29.5, 30.5), 6),
                        'remarks': fake.text(max_nb_chars=50) if random.random() > 0.7 else None,
                        'is_break': status in ['Off Duty', 'Sleeper Berth'],
                        'is_overtime': random.random() > 0.85,
                        'overtime_hours': round(random.uniform(0.5, 4), 1) if random.random() > 0.85 else 0
                    }
                    
                    # Add mandatory break check
                    if status in ['Driving'] and duration_minutes > 180:
                        log['break_required'] = True
                        log['break_taken'] = random.random() > 0.2
                        if not log['break_taken']:
                            log['violation_noted'] = True
                    else:
                        log['break_required'] = False
                        log['break_taken'] = None
                        log['violation_noted'] = False
                    
                    logs.append(log)
                    current_time = current_time + timedelta(minutes=duration_minutes)
                    
                    # Limit to 24 hours
                    if current_time >= log_date + timedelta(days=1):
                        break
        
        return logs
    
    def _generate_pre_trip_inspections(self, drivers):
        """Generate digital pre-trip inspection checklists"""
        inspections = []
        
        for driver in drivers:
            if driver['status'] == 'Active':
                # Generate inspections for the last 30 days
                num_inspections = random.randint(5, 20)
                
                for i in range(num_inspections):
                    inspection_time = datetime.now() - timedelta(days=random.randint(0, 30))
                    inspection_time += timedelta(hours=random.randint(4, 10), minutes=random.randint(0, 59))
                    
                    # Select random inspection items
                    num_items = random.randint(5, len(self.inspection_items))
                    selected_items = random.sample(self.inspection_items, num_items)
                    
                    inspection = {
                        'inspection_id': f'INS_{uuid.uuid4().hex[:8].upper()}',
                        'driver_id': driver['driver_id'],
                        'vehicle_id': f'VEH_{random.randint(1, 50):04d}',
                        'inspection_date': inspection_time,
                        'inspection_type': random.choice(['Pre-Trip', 'Post-Trip', 'Mid-Trip']),
                        'inspection_items': json.dumps([
                            {
                                'item': item,
                                'status': random.choice(['Pass', 'Fail', 'Needs Attention']),
                                'notes': fake.text(max_nb_chars=30) if random.random() > 0.7 else None
                            }
                            for item in selected_items
                        ]),
                        'pass_count': random.randint(num_items - 3, num_items),
                        'fail_count': random.randint(0, 3),
                        'defect_description': fake.text(max_nb_chars=80) if random.random() > 0.8 else None,
                        'action_taken': fake.text(max_nb_chars=60) if random.random() > 0.8 else None,
                        'status': random.choice(['Completed', 'Pending Review', 'Action Required']),
                        'location': fake.city(),
                        'latitude': round(random.uniform(-2.2, -1.5), 6),
                        'longitude': round(random.uniform(29.5, 30.5), 6),
                        'weather_condition': random.choice(['Clear', 'Rain', 'Fog', 'Snow']),
                        'temperature_c': round(random.uniform(10, 35), 2)
                    }
                    inspections.append(inspection)
        
        return inspections
    
    def _generate_fatigue_data(self, drivers):
        """Generate biometric and fatigue monitoring data"""
        fatigue_data = []
        
        for driver in drivers:
            if driver['status'] == 'Active':
                # Generate fatigue events for the last 30 days
                num_events = random.randint(5, 30)
                
                for i in range(num_events):
                    event_time = datetime.now() - timedelta(days=random.randint(0, 30))
                    event_time += timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    
                    fatigue_type = random.choice(self.fatigue_indicators)
                    
                    fatigue_event = {
                        'fatigue_id': f'FAT_{uuid.uuid4().hex[:8].upper()}',
                        'driver_id': driver['driver_id'],
                        'fatigue_type': fatigue_type,
                        'timestamp': event_time,
                        'severity': random.choice(self.severity_levels),
                        'duration_seconds': random.randint(1, 60),
                        'latitude': round(random.uniform(-2.2, -1.5), 6),
                        'longitude': round(random.uniform(29.5, 30.5), 6),
                        'alert_triggered': random.random() > 0.7,
                        'response_time_seconds': random.randint(1, 10) if random.random() > 0.7 else None,
                        'driver_acknowledged': random.random() > 0.5 if random.random() > 0.7 else None
                    }
                    
                    # Add fatigue-specific fields
                    if fatigue_type == 'Mobile Phone Usage':
                        fatigue_event['phone_type'] = random.choice(['Handheld', 'Bluetooth', 'Smartphone'])
                        fatigue_event['duration_seconds'] = random.randint(5, 120)
                    elif fatigue_type in ['Yawning', 'Eye Closure']:
                        fatigue_event['frequency_per_minute'] = round(random.uniform(1, 10), 2)
                        fatigue_event['eye_closure_percent'] = round(random.uniform(20, 80), 2)
                    elif fatigue_type == 'Distraction':
                        fatigue_event['distraction_source'] = random.choice([
                            'Internal', 'External', 'Device', 'Passenger', 'Navigation'
                        ])
                    
                    # Add biometric data
                    fatigue_event['heart_rate_bpm'] = random.randint(60, 120)
                    fatigue_event['skin_temperature_c'] = round(random.uniform(35, 37), 2)
                    fatigue_event['galvanic_skin_response'] = round(random.uniform(1, 10), 2)
                    fatigue_event['head_position'] = random.choice(['Normal', 'Tilted', 'Nodding'])
                    fatigue_event['eye_speed'] = round(random.uniform(100, 500), 2)
                    
                    fatigue_data.append(fatigue_event)
        
        return fatigue_data
    
    def generate_data(self):
        """Generate all driver monitoring data"""
        print("Generating driver monitoring data...")
        
        # Generate master data
        print("  - Generating drivers...")
        self.drivers = self._generate_drivers()
        
        print("  - Generating behavioral events...")
        self.events = self._generate_behavioral_events(self.drivers)
        
        print("  - Generating app telematics...")
        self.app_data = self._generate_app_telematics(self.drivers)
        
        print("  - Generating driver logs...")
        self.driver_logs = self._generate_driver_logs(self.drivers)
        
        print("  - Generating pre-trip inspections...")
        self.inspections = self._generate_pre_trip_inspections(self.drivers)
        
        print("  - Generating fatigue data...")
        self.fatigue_data = self._generate_fatigue_data(self.drivers)
        
        # Convert to DataFrames
        self.drivers_df = pd.DataFrame(self.drivers)
        self.events_df = pd.DataFrame(self.events)
        self.app_data_df = pd.DataFrame(self.app_data)
        self.driver_logs_df = pd.DataFrame(self.driver_logs)
        self.inspections_df = pd.DataFrame(self.inspections)
        self.fatigue_data_df = pd.DataFrame(self.fatigue_data)
        
        # Convert datetime columns
        datetime_cols_drivers = ['license_expiry', 'date_of_birth', 'hire_date', 
                                 'last_medical_exam', 'next_medical_exam']
        for col in datetime_cols_drivers:
            if col in self.drivers_df.columns:
                self.drivers_df[col] = pd.to_datetime(self.drivers_df[col])
        
        if 'timestamp' in self.events_df.columns:
            self.events_df['timestamp'] = pd.to_datetime(self.events_df['timestamp'])
        
        datetime_cols_app = ['login_time', 'logout_time']
        for col in datetime_cols_app:
            if col in self.app_data_df.columns:
                self.app_data_df[col] = pd.to_datetime(self.app_data_df[col])
        
        datetime_cols_logs = ['start_time', 'end_time']
        for col in datetime_cols_logs:
            if col in self.driver_logs_df.columns:
                self.driver_logs_df[col] = pd.to_datetime(self.driver_logs_df[col])
        
        if 'inspection_date' in self.inspections_df.columns:
            self.inspections_df['inspection_date'] = pd.to_datetime(self.inspections_df['inspection_date'])
        
        if 'timestamp' in self.fatigue_data_df.columns:
            self.fatigue_data_df['timestamp'] = pd.to_datetime(self.fatigue_data_df['timestamp'])
        
        return {
            'drivers': self.drivers_df,
            'behavioral_events': self.events_df,
            'app_telematics': self.app_data_df,
            'driver_logs': self.driver_logs_df,
            'inspections': self.inspections_df,
            'fatigue_data': self.fatigue_data_df
        }
    
    def save_csv(self, output_dir='agl_driver_data_output'):
        """Save all data as CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.drivers_df.to_csv(os.path.join(output_dir, 'drivers.csv'), index=False)
        self.events_df.to_csv(os.path.join(output_dir, 'behavioral_events.csv'), index=False)
        self.app_data_df.to_csv(os.path.join(output_dir, 'app_telematics.csv'), index=False)
        self.driver_logs_df.to_csv(os.path.join(output_dir, 'driver_logs.csv'), index=False)
        self.inspections_df.to_csv(os.path.join(output_dir, 'pre_trip_inspections.csv'), index=False)
        self.fatigue_data_df.to_csv(os.path.join(output_dir, 'fatigue_data.csv'), index=False)
        
        print(f"CSV files saved to {output_dir}")
    
    def save_parquet(self, output_dir='agl_driver_data_output'):
        """Save all data as Parquet"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.drivers_df.to_parquet(os.path.join(output_dir, 'drivers.parquet'), index=False)
        self.events_df.to_parquet(os.path.join(output_dir, 'behavioral_events.parquet'), index=False)
        self.app_data_df.to_parquet(os.path.join(output_dir, 'app_telematics.parquet'), index=False)
        self.driver_logs_df.to_parquet(os.path.join(output_dir, 'driver_logs.parquet'), index=False)
        self.inspections_df.to_parquet(os.path.join(output_dir, 'pre_trip_inspections.parquet'), index=False)
        self.fatigue_data_df.to_parquet(os.path.join(output_dir, 'fatigue_data.parquet'), index=False)
        
        print(f"Parquet files saved to {output_dir}")
    
    def save_json(self, output_dir='agl_driver_data_output'):
        """Save all data as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        def convert_datetime(df):
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64']).columns:
                df_copy[col] = df_copy[col].astype(str)
            return df_copy
        
        convert_datetime(self.drivers_df).to_json(
            os.path.join(output_dir, 'drivers.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.events_df).to_json(
            os.path.join(output_dir, 'behavioral_events.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.app_data_df).to_json(
            os.path.join(output_dir, 'app_telematics.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.driver_logs_df).to_json(
            os.path.join(output_dir, 'driver_logs.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.inspections_df).to_json(
            os.path.join(output_dir, 'pre_trip_inspections.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.fatigue_data_df).to_json(
            os.path.join(output_dir, 'fatigue_data.json'), orient='records', date_format='iso'
        )
        
        print(f"JSON files saved to {output_dir}")
    
    def save_xml(self, output_dir='agl_driver_data_output'):
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
                    elif isinstance(value, (dict, list)):
                        child.text = json.dumps(value, default=str)
                    else:
                        child.text = str(value)
            
            xml_str = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
        
        df_to_xml(self.drivers_df, 'Drivers', 'Driver', 
                  os.path.join(output_dir, 'drivers.xml'))
        df_to_xml(self.events_df, 'BehavioralEvents', 'Event', 
                  os.path.join(output_dir, 'behavioral_events.xml'))
        df_to_xml(self.app_data_df, 'AppTelematics', 'Session', 
                  os.path.join(output_dir, 'app_telematics.xml'))
        df_to_xml(self.driver_logs_df, 'DriverLogs', 'Log', 
                  os.path.join(output_dir, 'driver_logs.xml'))
        df_to_xml(self.inspections_df, 'Inspections', 'Inspection', 
                  os.path.join(output_dir, 'pre_trip_inspections.xml'))
        df_to_xml(self.fatigue_data_df, 'FatigueData', 'FatigueEvent', 
                  os.path.join(output_dir, 'fatigue_data.xml'))
        
        print(f"XML files saved to {output_dir}")
    
    def save_all_formats(self, output_dir='agl_driver_data_output'):
        """Save all data in all formats"""
        print("\n" + "=" * 60)
        print("Saving driver monitoring data in multiple formats...")
        print("=" * 60)
        
        self.save_csv(output_dir)
        self.save_parquet(output_dir)
        self.save_json(output_dir)
        self.save_xml(output_dir)
        
        print("\nAll driver monitoring data files saved successfully!")

def main():
    """Main function to run the driver monitoring data generator"""
    print("=" * 60)
    print("AGL Rwanda - Driver Monitoring & App Data Generator")
    print("=" * 60)
    
    # Initialize generator
    print("\nInitializing driver monitoring data generator...")
    generator = AGLDriverMonitoringGenerator(
        num_drivers=200,
        num_trips=500,
        num_events=10000
    )
    
    # Generate data
    data = generator.generate_data()
    
    # Display statistics
    print(f"\nData generated:")
    print(f"  - Drivers: {len(data['drivers'])}")
    print(f"  - Behavioral Events: {len(data['behavioral_events'])}")
    print(f"  - App Telematics Sessions: {len(data['app_telematics'])}")
    print(f"  - Driver Logs: {len(data['driver_logs'])}")
    print(f"  - Pre-Trip Inspections: {len(data['inspections'])}")
    print(f"  - Fatigue Events: {len(data['fatigue_data'])}")
    
    # Display sample data
    print("\nSample Driver Data:")
    print(data['drivers'].head())
    
    print("\nSample Behavioral Events:")
    print(data['behavioral_events'].head())
    
    print("\nSample App Telematics:")
    print(data['app_telematics'].head())
    
    print("\nSample Driver Logs:")
    print(data['driver_logs'].head())
    
    print("\nSample Pre-Trip Inspections:")
    print(data['inspections'].head())
    
    print("\nSample Fatigue Data:")
    print(data['fatigue_data'].head())
    
    # Save in all formats
    generator.save_all_formats()
    
    print("\n" + "=" * 60)
    print("Driver monitoring data generation complete!")
    print("Check the 'agl_driver_data_output' directory for all files")
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