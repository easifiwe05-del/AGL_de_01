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

class AGLColdChainDataGenerator:
    def __init__(self, num_containers=100, num_warehouses=10, 
                 num_sensors=500, num_readings=50000):
        """
        Initialize the cold chain environmental data generator
        
        Args:
            num_containers (int): Number of reefer containers
            num_warehouses (int): Number of warehouses/cold storage facilities
            num_sensors (int): Number of IoT sensors
            num_readings (int): Number of sensor readings
        """
        self.num_containers = num_containers
        self.num_warehouses = num_warehouses
        self.num_sensors = num_sensors
        self.num_readings = num_readings
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define product types and their temperature requirements
        self.product_types = {
            'Pharmaceuticals': {
                'temp_min': 2.0,
                'temp_max': 8.0,
                'humidity_min': 30.0,
                'humidity_max': 60.0,
                'sensitivity': 'High'
            },
            'Fresh Produce': {
                'temp_min': 0.0,
                'temp_max': 4.0,
                'humidity_min': 85.0,
                'humidity_max': 95.0,
                'sensitivity': 'Medium'
            },
            'Frozen Foods': {
                'temp_min': -25.0,
                'temp_max': -18.0,
                'humidity_min': 60.0,
                'humidity_max': 80.0,
                'sensitivity': 'High'
            },
            'Dairy Products': {
                'temp_min': 0.0,
                'temp_max': 5.0,
                'humidity_min': 60.0,
                'humidity_max': 75.0,
                'sensitivity': 'Medium'
            },
            'Meat & Seafood': {
                'temp_min': -2.0,
                'temp_max': 4.0,
                'humidity_min': 75.0,
                'humidity_max': 85.0,
                'sensitivity': 'High'
            },
            'Beverages': {
                'temp_min': 2.0,
                'temp_max': 10.0,
                'humidity_min': 40.0,
                'humidity_max': 70.0,
                'sensitivity': 'Low'
            },
            'Flowers': {
                'temp_min': 2.0,
                'temp_max': 8.0,
                'humidity_min': 80.0,
                'humidity_max': 90.0,
                'sensitivity': 'Medium'
            },
            'Chemicals': {
                'temp_min': 15.0,
                'temp_max': 25.0,
                'humidity_min': 30.0,
                'humidity_max': 50.0,
                'sensitivity': 'High'
            }
        }
        
        # Define temperature zones
        self.temperature_zones = [
            'Frozen (-25°C to -18°C)',
            'Cold (0°C to 4°C)',
            'Chilled (2°C to 8°C)',
            'Ambient (15°C to 25°C)',
            'Climate Controlled (20°C to 22°C)'
        ]
        
        # Define IoT sensor types
        self.sensor_types = [
            'Temperature Sensor',
            'Humidity Sensor',
            'Pressure Sensor',
            'Vibration Sensor',
            'Light Sensor',
            'Door Sensor',
            'Gas Sensor',
            'Motion Sensor'
        ]
        
        # Define manufacturers
        self.manufacturers = [
            'Honeywell', 'Siemens', 'Johnson Controls', 'Danfoss', 'Thermo King',
            'Carrier', 'Emerson', 'Schneider Electric', 'Zebra', 'Sensata'
        ]
        
        # Define warehouse names
        self.warehouse_names = [
            'Kigali SEZ Cold Storage 1',
            'Kigali SEZ Cold Storage 2',
            'Kigali SEZ Cold Storage 3',
            'Rusumo Cold Chain Facility',
            'Gatuna Cold Storage Hub',
            'Gisenyi Cold Chain Center',
            'Kigali Pharma Storage',
            'Rwamagana Cold Storage',
            'Musanze Cold Facility',
            'Rubavu Cold Chain Hub'
        ]
    
    def _generate_containers(self):
        """Generate reefer container master data"""
        containers = []
        for i in range(self.num_containers):
            container_type = random.choice(['20ft', '40ft', '40ft HC', '45ft'])
            product_type = random.choice(list(self.product_types.keys()))
            requirements = self.product_types[product_type]
            
            # Calculate capacity based on container type
            capacity_m3 = {
                '20ft': 33.2,
                '40ft': 67.7,
                '40ft HC': 76.3,
                '45ft': 86.0
            }[container_type]
            
            container = {
                'container_id': f'CONT_{i+1:06d}',
                'container_type': container_type,
                'product_type': product_type,
                'setpoint_temp_c': round(random.uniform(
                    requirements['temp_min'], 
                    requirements['temp_max']
                ), 1),
                'temp_min_c': requirements['temp_min'],
                'temp_max_c': requirements['temp_max'],
                'setpoint_humidity_percent': round(random.uniform(
                    requirements['humidity_min'],
                    requirements['humidity_max']
                ), 1),
                'humidity_min_percent': requirements['humidity_min'],
                'humidity_max_percent': requirements['humidity_max'],
                'capacity_m3': capacity_m3,
                'current_fill_percent': round(random.uniform(10, 95), 1),
                'manufacturer': random.choice(self.manufacturers),
                'model': f'R{random.randint(100, 999)}-{random.choice(["A", "B", "C"])}',
                'year_manufactured': random.randint(2015, 2025),
                'last_maintenance_date': datetime.now() - timedelta(days=random.randint(1, 90)),
                'next_maintenance_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                'status': random.choice(['Active', 'In Use', 'Maintenance', 'Idle', 'Out of Service']),
                'assigned_warehouse': random.choice(self.warehouse_names[:self.num_warehouses]) if random.random() > 0.3 else None,
                'gps_latitude': round(random.uniform(-2.2, -1.5), 6),
                'gps_longitude': round(random.uniform(29.5, 30.5), 6)
            }
            containers.append(container)
        return containers
    
    def _generate_warehouses(self):
        """Generate warehouse master data"""
        warehouses = []
        for i in range(self.num_warehouses):
            product_types = random.sample(list(self.product_types.keys()), random.randint(2, 5))
            
            warehouse = {
                'warehouse_id': f'WH_{i+1:03d}',
                'warehouse_name': self.warehouse_names[i],
                'address': fake.address(),
                'total_area_m2': round(random.uniform(500, 5000), 2),
                'cooling_capacity_kw': round(random.uniform(100, 5000), 2),
                'number_of_bays': random.randint(5, 30),
                'product_types': ','.join(product_types),
                'temperature_zone': random.choice(self.temperature_zones),
                'power_backup_hours': round(random.uniform(2, 24), 2),
                'generator_capacity_kva': round(random.uniform(100, 1000), 2),
                'manager_name': fake.name(),
                'contact_phone': fake.phone_number(),
                'contact_email': fake.email(),
                'operating_hours': random.choice(['24/7', '06:00-22:00', '08:00-20:00']),
                'certification': random.choice([
                    'ISO 22000', 'GMP', 'HACCP', 'FDA', 'WHO GDP',
                    'ISO 9001', 'ISO 14001', 'OHSAS 18001'
                ]),
                'status': random.choice(['Operational', 'Maintenance', 'Expansion', 'Temporary Closure'])
            }
            warehouses.append(warehouse)
        return warehouses
    
    def _generate_sensors(self, containers, warehouses):
        """Generate IoT sensor master data"""
        sensors = []
        sensor_id_counter = 1
        
        # Generate sensors for containers
        for container in containers:
            if container['status'] in ['Active', 'In Use']:
                # Each active container has 3-8 sensors
                num_sensors_per_container = random.randint(3, 8)
                for i in range(num_sensors_per_container):
                    sensor_type = random.choice(self.sensor_types)
                    sensor = {
                        'sensor_id': f'SEN_{sensor_id_counter:06d}',
                        'sensor_type': sensor_type,
                        'manufacturer': random.choice(self.manufacturers),
                        'model': f'M{random.randint(100, 999)}-{sensor_type[:2].upper()}',
                        'container_id': container['container_id'],
                        'warehouse_id': container['assigned_warehouse'] if container['assigned_warehouse'] else None,
                        'location': random.choice(['Inside', 'Outside', 'Door', 'Top', 'Bottom']),
                        'battery_level_percent': round(random.uniform(10, 100), 1),
                        'signal_strength_dbm': round(random.uniform(-80, -30), 2),
                        'calibration_date': datetime.now() - timedelta(days=random.randint(0, 180)),
                        'next_calibration_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                        'calibration_interval_days': random.choice([30, 60, 90, 180]),
                        'status': random.choice(['Active', 'Inactive', 'Maintenance', 'Faulty']),
                        'firmware_version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
                        'last_reading': None,
                        'last_reading_timestamp': None
                    }
                    sensors.append(sensor)
                    sensor_id_counter += 1
        
        # Generate sensors for warehouses
        for warehouse in warehouses:
            if warehouse['status'] == 'Operational':
                # Each warehouse has 10-30 sensors
                num_sensors_per_warehouse = random.randint(10, 30)
                for i in range(num_sensors_per_warehouse):
                    sensor_type = random.choice(self.sensor_types)
                    sensor = {
                        'sensor_id': f'SEN_{sensor_id_counter:06d}',
                        'sensor_type': sensor_type,
                        'manufacturer': random.choice(self.manufacturers),
                        'model': f'M{random.randint(100, 999)}-{sensor_type[:2].upper()}',
                        'container_id': None,
                        'warehouse_id': warehouse['warehouse_id'],
                        'location': random.choice(['Zone A', 'Zone B', 'Zone C', 'Freezer Section', 
                                                  'Chiller Section', 'Receiving Area', 'Dispatch Area']),
                        'battery_level_percent': round(random.uniform(10, 100), 1),
                        'signal_strength_dbm': round(random.uniform(-80, -30), 2),
                        'calibration_date': datetime.now() - timedelta(days=random.randint(0, 180)),
                        'next_calibration_date': datetime.now() + timedelta(days=random.randint(1, 90)),
                        'calibration_interval_days': random.choice([30, 60, 90, 180]),
                        'status': random.choice(['Active', 'Inactive', 'Maintenance', 'Faulty']),
                        'firmware_version': f'v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
                        'last_reading': None,
                        'last_reading_timestamp': None
                    }
                    sensors.append(sensor)
                    sensor_id_counter += 1
        
        return sensors
    
    def _generate_sensor_readings(self, sensors, containers, warehouses):
        """Generate high-frequency sensor readings"""
        readings = []
        
        # Generate readings for each sensor
        for sensor in sensors:
            if sensor['status'] == 'Active':
                # Number of readings per sensor
                num_readings_per_sensor = random.randint(50, 200)
                
                # Determine the time range
                start_time = datetime.now() - timedelta(days=random.randint(1, 30))
                
                # Find the associated container or warehouse for temperature requirements
                temp_min = -25.0
                temp_max = 25.0
                humidity_min = 20.0
                humidity_max = 80.0
                
                if sensor['container_id']:
                    container = next((c for c in containers if c['container_id'] == sensor['container_id']), None)
                    if container:
                        product_type = container['product_type']
                        requirements = self.product_types[product_type]
                        temp_min = requirements['temp_min'] - 5  # Allow some variation
                        temp_max = requirements['temp_max'] + 5
                        humidity_min = max(10, requirements['humidity_min'] - 20)
                        humidity_max = min(100, requirements['humidity_max'] + 20)
                
                for i in range(num_readings_per_sensor):
                    # Generate timestamp with random interval (1-5 minutes)
                    interval_minutes = random.uniform(1, 5)
                    reading_time = start_time + timedelta(minutes=i * interval_minutes)
                    
                    # Generate temperature with random fluctuations
                    temperature = round(random.uniform(temp_min, temp_max), 2)
                    
                    # Generate humidity
                    humidity = round(random.uniform(humidity_min, humidity_max), 2)
                    
                    # Generate pressure (in hPa)
                    pressure = round(random.uniform(980, 1030), 2)
                    
                    # Generate additional sensor-specific readings
                    reading = {
                        'reading_id': f'READ_{uuid.uuid4().hex[:8].upper()}',
                        'sensor_id': sensor['sensor_id'],
                        'container_id': sensor['container_id'],
                        'warehouse_id': sensor['warehouse_id'],
                        'timestamp': reading_time,
                        'temperature_c': temperature,
                        'humidity_percent': humidity,
                        'pressure_hpa': pressure,
                        'battery_level_percent': round(random.uniform(
                            max(5, sensor['battery_level_percent'] - 20),
                            min(100, sensor['battery_level_percent'] + 5)
                        ), 1),
                        'signal_strength_dbm': round(random.uniform(
                            max(-100, sensor['signal_strength_dbm'] - 10),
                            min(-20, sensor['signal_strength_dbm'] + 10)
                        ), 2),
                        'is_anomaly': False
                    }
                    
                    # Add sensor-type specific readings
                    if sensor['sensor_type'] == 'Temperature Sensor':
                        reading['sensor_value'] = temperature
                    elif sensor['sensor_type'] == 'Humidity Sensor':
                        reading['sensor_value'] = humidity
                    elif sensor['sensor_type'] == 'Pressure Sensor':
                        reading['sensor_value'] = pressure
                    else:
                        reading['sensor_value'] = round(random.uniform(0, 100), 2)
                    
                    # Check for anomalies (temperature or humidity out of range)
                    if sensor['container_id']:
                        container = next((c for c in containers if c['container_id'] == sensor['container_id']), None)
                        if container:
                            if (temperature < container['temp_min_c'] - 2 or 
                                temperature > container['temp_max_c'] + 2 or
                                humidity < container['humidity_min_percent'] - 10 or
                                humidity > container['humidity_max_percent'] + 10):
                                reading['is_anomaly'] = True
                    
                    readings.append(reading)
        
        # Trim to desired number of readings
        if len(readings) > self.num_readings:
            readings = random.sample(readings, self.num_readings)
        
        return readings
    
    def _generate_reefer_status(self, containers):
        """Generate reefer status data"""
        reefer_statuses = []
        
        for container in containers:
            if container['status'] in ['Active', 'In Use']:
                # Generate status readings every 15-60 minutes for the last 24 hours
                start_time = datetime.now() - timedelta(hours=24)
                num_readings = random.randint(24, 96)  # 24-96 readings in 24 hours
                
                for i in range(num_readings):
                    reading_time = start_time + timedelta(minutes=i * (1440 / num_readings))
                    
                    # Generate power status
                    power_on = random.random() > 0.05  # 95% on time
                    if not power_on and random.random() < 0.1:
                        # Occasionally power off for maintenance
                        power_on = False
                    
                    # Generate compressor cycles
                    compressor_cycles = random.randint(0, 10) if power_on else 0
                    
                    # Generate defrost cycles
                    defrost_cycles = random.randint(0, 2) if power_on and random.random() > 0.6 else 0
                    
                    # Generate fuel/battery levels
                    if container['container_type'] in ['20ft', '40ft']:
                        fuel_level = round(random.uniform(10, 100), 2)
                        battery_level = round(random.uniform(10, 100), 2)
                    else:
                        fuel_level = round(random.uniform(20, 100), 2)
                        battery_level = round(random.uniform(30, 100), 2)
                    
                    reefer_status = {
                        'status_id': f'RS_{uuid.uuid4().hex[:8].upper()}',
                        'container_id': container['container_id'],
                        'timestamp': reading_time,
                        'power_status': 'On' if power_on else 'Off',
                        'compressor_cycles_per_hour': compressor_cycles,
                        'defrost_cycle_count': defrost_cycles,
                        'fuel_level_percent': fuel_level,
                        'battery_level_percent': battery_level,
                        'cooling_unit_temp_c': round(random.uniform(
                            container['setpoint_temp_c'] - 2,
                            container['setpoint_temp_c'] + 2
                        ), 2),
                        'condenser_pressure_bar': round(random.uniform(10, 30), 2),
                        'evaporator_pressure_bar': round(random.uniform(2, 8), 2),
                        'fan_speed_rpm': random.randint(500, 2000),
                        'runtime_hours': round(container.get('runtime_hours', random.uniform(100, 10000)), 2)
                    }
                    reefer_statuses.append(reefer_status)
        
        return reefer_statuses
    
    def _generate_sensor_health(self, sensors):
        """Generate sensor health data"""
        sensor_health = []
        
        for sensor in sensors:
            # Generate health check for each sensor
            health_check = {
                'health_id': f'HLTH_{uuid.uuid4().hex[:8].upper()}',
                'sensor_id': sensor['sensor_id'],
                'container_id': sensor['container_id'],
                'warehouse_id': sensor['warehouse_id'],
                'check_timestamp': datetime.now() - timedelta(days=random.randint(0, 7)),
                'battery_level_percent': sensor['battery_level_percent'],
                'signal_strength_dbm': sensor['signal_strength_dbm'],
                'calibration_status': 'Valid' if datetime.now() < sensor['next_calibration_date'] else 'Expired',
                'firmware_version': sensor['firmware_version'],
                'data_transmission_rate': round(random.uniform(90, 100), 2),
                'packet_loss_percent': round(random.uniform(0, 5), 2),
                'response_time_ms': round(random.uniform(50, 500), 2),
                'error_code': random.choice(['None', 'ERR001', 'ERR002', 'ERR003', 'ERR004']) if random.random() < 0.15 else 'None',
                'maintenance_recommended': random.random() < 0.1,
                'health_score': random.randint(70, 100)
            }
            sensor_health.append(health_check)
        
        return sensor_health
    
    def generate_data(self):
        """Generate all cold chain data"""
        print("Generating cold chain data...")
        
        # Generate master data
        print("  - Generating containers...")
        self.containers = self._generate_containers()
        
        print("  - Generating warehouses...")
        self.warehouses = self._generate_warehouses()
        
        print("  - Generating sensors...")
        self.sensors = self._generate_sensors(self.containers, self.warehouses)
        
        print("  - Generating sensor readings...")
        self.readings = self._generate_sensor_readings(
            self.sensors, self.containers, self.warehouses
        )
        
        print("  - Generating reefer status data...")
        self.reefer_status = self._generate_reefer_status(self.containers)
        
        print("  - Generating sensor health data...")
        self.sensor_health = self._generate_sensor_health(self.sensors)
        
        # Convert to DataFrames
        self.containers_df = pd.DataFrame(self.containers)
        self.warehouses_df = pd.DataFrame(self.warehouses)
        self.sensors_df = pd.DataFrame(self.sensors)
        self.readings_df = pd.DataFrame(self.readings)
        self.reefer_status_df = pd.DataFrame(self.reefer_status)
        self.sensor_health_df = pd.DataFrame(self.sensor_health)
        
        # Convert datetime columns
        datetime_cols_containers = ['last_maintenance_date', 'next_maintenance_date']
        for col in datetime_cols_containers:
            if col in self.containers_df.columns:
                self.containers_df[col] = pd.to_datetime(self.containers_df[col])
        
        datetime_cols_sensors = ['calibration_date', 'next_calibration_date']
        for col in datetime_cols_sensors:
            if col in self.sensors_df.columns:
                self.sensors_df[col] = pd.to_datetime(self.sensors_df[col])
        
        if 'timestamp' in self.readings_df.columns:
            self.readings_df['timestamp'] = pd.to_datetime(self.readings_df['timestamp'])
        
        if 'timestamp' in self.reefer_status_df.columns:
            self.reefer_status_df['timestamp'] = pd.to_datetime(self.reefer_status_df['timestamp'])
        
        if 'check_timestamp' in self.sensor_health_df.columns:
            self.sensor_health_df['check_timestamp'] = pd.to_datetime(self.sensor_health_df['check_timestamp'])
        
        return {
            'containers': self.containers_df,
            'warehouses': self.warehouses_df,
            'sensors': self.sensors_df,
            'readings': self.readings_df,
            'reefer_status': self.reefer_status_df,
            'sensor_health': self.sensor_health_df
        }
    
    def save_csv(self, output_dir='agl_coldchain_data_output'):
        """Save all data as CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.containers_df.to_csv(os.path.join(output_dir, 'containers.csv'), index=False)
        self.warehouses_df.to_csv(os.path.join(output_dir, 'warehouses.csv'), index=False)
        self.sensors_df.to_csv(os.path.join(output_dir, 'sensors.csv'), index=False)
        self.readings_df.to_csv(os.path.join(output_dir, 'sensor_readings.csv'), index=False)
        self.reefer_status_df.to_csv(os.path.join(output_dir, 'reefer_status.csv'), index=False)
        self.sensor_health_df.to_csv(os.path.join(output_dir, 'sensor_health.csv'), index=False)
        
        print(f"CSV files saved to {output_dir}")
    
    def save_parquet(self, output_dir='agl_coldchain_data_output'):
        """Save all data as Parquet"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.containers_df.to_parquet(os.path.join(output_dir, 'containers.parquet'), index=False)
        self.warehouses_df.to_parquet(os.path.join(output_dir, 'warehouses.parquet'), index=False)
        self.sensors_df.to_parquet(os.path.join(output_dir, 'sensors.parquet'), index=False)
        self.readings_df.to_parquet(os.path.join(output_dir, 'sensor_readings.parquet'), index=False)
        self.reefer_status_df.to_parquet(os.path.join(output_dir, 'reefer_status.parquet'), index=False)
        self.sensor_health_df.to_parquet(os.path.join(output_dir, 'sensor_health.parquet'), index=False)
        
        print(f"Parquet files saved to {output_dir}")
    
    def save_json(self, output_dir='agl_coldchain_data_output'):
        """Save all data as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        def convert_datetime(df):
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64']).columns:
                df_copy[col] = df_copy[col].astype(str)
            return df_copy
        
        convert_datetime(self.containers_df).to_json(
            os.path.join(output_dir, 'containers.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.warehouses_df).to_json(
            os.path.join(output_dir, 'warehouses.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.sensors_df).to_json(
            os.path.join(output_dir, 'sensors.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.readings_df).to_json(
            os.path.join(output_dir, 'sensor_readings.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.reefer_status_df).to_json(
            os.path.join(output_dir, 'reefer_status.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.sensor_health_df).to_json(
            os.path.join(output_dir, 'sensor_health.json'), orient='records', date_format='iso'
        )
        
        print(f"JSON files saved to {output_dir}")
    
    def save_xml(self, output_dir='agl_coldchain_data_output'):
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
        
        df_to_xml(self.containers_df, 'Containers', 'Container', 
                  os.path.join(output_dir, 'containers.xml'))
        df_to_xml(self.warehouses_df, 'Warehouses', 'Warehouse', 
                  os.path.join(output_dir, 'warehouses.xml'))
        df_to_xml(self.sensors_df, 'Sensors', 'Sensor', 
                  os.path.join(output_dir, 'sensors.xml'))
        df_to_xml(self.readings_df, 'SensorReadings', 'Reading', 
                  os.path.join(output_dir, 'sensor_readings.xml'))
        df_to_xml(self.reefer_status_df, 'ReeferStatus', 'Status', 
                  os.path.join(output_dir, 'reefer_status.xml'))
        df_to_xml(self.sensor_health_df, 'SensorHealth', 'Health', 
                  os.path.join(output_dir, 'sensor_health.xml'))
        
        print(f"XML files saved to {output_dir}")
    
    def save_all_formats(self, output_dir='agl_coldchain_data_output'):
        """Save all data in all formats"""
        print("\n" + "=" * 60)
        print("Saving cold chain data in multiple formats...")
        print("=" * 60)
        
        self.save_csv(output_dir)
        self.save_parquet(output_dir)
        self.save_json(output_dir)
        self.save_xml(output_dir)
        
        print("\nAll cold chain data files saved successfully!")

def main():
    """Main function to run the cold chain data generator"""
    print("=" * 60)
    print("AGL Rwanda - Cold Chain Environmental Data Generator")
    print("=" * 60)
    
    # Initialize generator
    print("\nInitializing cold chain data generator...")
    generator = AGLColdChainDataGenerator(
        num_containers=100,
        num_warehouses=10,
        num_sensors=500,
        num_readings=50000
    )
    
    # Generate data
    data = generator.generate_data()
    
    # Display statistics
    print(f"\nData generated:")
    print(f"  - Reefer Containers: {len(data['containers'])}")
    print(f"  - Warehouses: {len(data['warehouses'])}")
    print(f"  - IoT Sensors: {len(data['sensors'])}")
    print(f"  - Sensor Readings: {len(data['readings'])}")
    print(f"  - Reefer Status Records: {len(data['reefer_status'])}")
    print(f"  - Sensor Health Records: {len(data['sensor_health'])}")
    
    # Display sample data
    print("\nSample Container Data:")
    print(data['containers'].head())
    
    print("\nSample Warehouse Data:")
    print(data['warehouses'].head())
    
    print("\nSample Sensor Data:")
    print(data['sensors'].head())
    
    print("\nSample Sensor Readings:")
    print(data['readings'].head())
    
    print("\nSample Reefer Status:")
    print(data['reefer_status'].head())
    
    print("\nSample Sensor Health:")
    print(data['sensor_health'].head())
    
    # Save in all formats
    generator.save_all_formats()
    
    print("\n" + "=" * 60)
    print("Cold chain data generation complete!")
    print("Check the 'agl_coldchain_data_output' directory for all files")
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