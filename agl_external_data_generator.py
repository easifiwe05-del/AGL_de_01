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

# Initialize Faker for realistic data generation
fake = Faker()

class AGLExternalDataGenerator:
    def __init__(self, num_weather_records=5000, num_traffic_records=2000, 
                 num_market_records=1000):
        """
        Initialize the external and contextual data generator
        
        Args:
            num_weather_records (int): Number of weather records
            num_traffic_records (int): Number of traffic/infrastructure records
            num_market_records (int): Number of market data records
        """
        self.num_weather_records = num_weather_records
        self.num_traffic_records = num_traffic_records
        self.num_market_records = num_market_records
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define corridors and their geographic coordinates
        self.corridors = {
            'Kigali-Rusumo': {
                'start': {'lat': -1.9441, 'lon': 30.0619},
                'end': {'lat': -2.0900, 'lon': 30.1900},
                'waypoints': [
                    (-1.9600, 30.0800),
                    (-1.9800, 30.1000),
                    (-2.0000, 30.1200),
                    (-2.0300, 30.1500),
                    (-2.0600, 30.1700)
                ],
                'border_post': 'Rusumo Border Post',
                'distance_km': 280,
                'major_towns': ['Kigali', 'Rwamagana', 'Kirehe', 'Rusumo']
            },
            'Kigali-Gatuna': {
                'start': {'lat': -1.9441, 'lon': 30.0619},
                'end': {'lat': -1.7500, 'lon': 29.8700},
                'waypoints': [
                    (-1.9200, 30.0300),
                    (-1.8900, 30.0000),
                    (-1.8600, 29.9700),
                    (-1.8300, 29.9400),
                    (-1.8000, 29.9100)
                ],
                'border_post': 'Gatuna Border Post',
                'distance_km': 340,
                'major_towns': ['Kigali', 'Musanze', 'Gatuna']
            },
            'Kigali-Gisenyi': {
                'start': {'lat': -1.9441, 'lon': 30.0619},
                'end': {'lat': -1.7800, 'lon': 29.5500},
                'waypoints': [
                    (-1.9300, 30.0300),
                    (-1.9100, 29.9800),
                    (-1.8800, 29.9300),
                    (-1.8500, 29.8800),
                    (-1.8200, 29.8300)
                ],
                'border_post': 'Gisenyi Border Post',
                'distance_km': 250,
                'major_towns': ['Kigali', 'Rubavu', 'Gisenyi']
            }
        }
        
        # Define East African countries and their currencies
        self.east_african_countries = [
            {'country': 'Rwanda', 'currency': 'RWF', 'fuel_index': 100, 'exchange_rate_to_usd': 1200},
            {'country': 'Kenya', 'currency': 'KES', 'fuel_index': 85, 'exchange_rate_to_usd': 150},
            {'country': 'Uganda', 'currency': 'UGX', 'fuel_index': 90, 'exchange_rate_to_usd': 3700},
            {'country': 'Tanzania', 'currency': 'TZS', 'fuel_index': 80, 'exchange_rate_to_usd': 2500},
            {'country': 'Burundi', 'currency': 'BIF', 'fuel_index': 95, 'exchange_rate_to_usd': 2800},
            {'country': 'South Sudan', 'currency': 'SSP', 'fuel_index': 110, 'exchange_rate_to_usd': 1000},
            {'country': 'DRC', 'currency': 'CDF', 'fuel_index': 105, 'exchange_rate_to_usd': 2000},
            {'country': 'Ethiopia', 'currency': 'ETB', 'fuel_index': 75, 'exchange_rate_to_usd': 55}
        ]
        
        # Define weather conditions
        self.weather_conditions = [
            'Clear', 'Partly Cloudy', 'Overcast', 'Light Rain', 'Heavy Rain',
            'Thunderstorm', 'Fog', 'Mist', 'Haze', 'Drizzle', 'Snow', 'Windy'
        ]
        
        # Define traffic conditions
        self.traffic_conditions = ['Free Flow', 'Moderate', 'Heavy', 'Gridlock', 'Stop and Go']
        self.road_conditions = ['Good', 'Fair', 'Poor', 'Under Construction', 'Flooded']
        
        # Define holiday types
        self.holiday_types = ['Public Holiday', 'National Day', 'Religious Holiday', 
                             'International Holiday', 'Regional Holiday']
        
        # Define border wait times by post
        self.border_wait_times = {
            'Rusumo Border Post': {'min_hours': 0.5, 'max_hours': 8},
            'Gatuna Border Post': {'min_hours': 1, 'max_hours': 6},
            'Gisenyi Border Post': {'min_hours': 0.5, 'max_hours': 4},
            'Kagitumba Border Post': {'min_hours': 1, 'max_hours': 5},
            'Ruhwa Border Post': {'min_hours': 0.5, 'max_hours': 3}
        }
    
    def _generate_weather_data(self):
        """Generate weather data along corridors"""
        weather_records = []
        
        for i in range(self.num_weather_records):
            corridor = random.choice(list(self.corridors.keys()))
            corridor_data = self.corridors[corridor]
            
            # Generate timestamp (within last 30 days and next 7 days forecast)
            if random.random() > 0.7:
                # Forecast data (future)
                timestamp = datetime.now() + timedelta(days=random.randint(1, 7))
                is_forecast = True
            else:
                # Historical data (past)
                timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
                is_forecast = False
            
            # Select a location along the corridor
            location_type = random.choices(
                ['start', 'waypoint', 'end'],
                weights=[0.2, 0.6, 0.2]
            )[0]
            
            if location_type == 'start':
                lat, lon = corridor_data['start']['lat'], corridor_data['start']['lon']
                location_name = corridor_data['major_towns'][0]
            elif location_type == 'end':
                lat, lon = corridor_data['end']['lat'], corridor_data['end']['lon']
                location_name = corridor_data['major_towns'][-1]
            else:
                waypoint = random.choice(corridor_data['waypoints'])
                lat, lon = waypoint[0], waypoint[1]
                location_name = random.choice(corridor_data['major_towns'][1:-1]) if len(corridor_data['major_towns']) > 2 else corridor_data['major_towns'][0]
            
            # Generate weather metrics
            temperature = round(random.uniform(10, 35), 2)
            precipitation_mm = round(random.uniform(0, 20), 2)
            wind_speed_kmh = round(random.uniform(0, 60), 2)
            wind_direction = round(random.uniform(0, 360), 2)
            humidity = round(random.uniform(20, 95), 2)
            pressure_hpa = round(random.uniform(980, 1030), 2)
            visibility_km = round(random.uniform(0.5, 20), 2)
            cloud_cover_percent = round(random.uniform(0, 100), 2)
            
            weather = {
                'weather_id': f'WTH_{uuid.uuid4().hex[:8].upper()}',
                'corridor_name': corridor,
                'location_name': location_name,
                'latitude': round(lat, 6),
                'longitude': round(lon, 6),
                'timestamp': timestamp,
                'is_forecast': is_forecast,
                'weather_condition': random.choice(self.weather_conditions),
                'temperature_c': temperature,
                'precipitation_mm': precipitation_mm,
                'wind_speed_kmh': wind_speed_kmh,
                'wind_direction_deg': wind_direction,
                'humidity_percent': humidity,
                'pressure_hpa': pressure_hpa,
                'visibility_km': visibility_km,
                'cloud_cover_percent': cloud_cover_percent,
                'uv_index': round(random.uniform(0, 11), 1),
                'weather_alert': random.choice([
                    'None', 'Heavy Rain Warning', 'Strong Wind Advisory', 
                    'Fog Warning', 'Flood Alert', 'Heat Advisory'
                ]) if random.random() > 0.85 else 'None'
            }
            weather_records.append(weather)
        
        return weather_records
    
    def _generate_traffic_data(self):
        """Generate traffic and infrastructure data"""
        traffic_records = []
        
        for i in range(self.num_traffic_records):
            corridor = random.choice(list(self.corridors.keys()))
            corridor_data = self.corridors[corridor]
            
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Generate location
            location_type = random.choices(
                ['corridor', 'border_post', 'town'],
                weights=[0.4, 0.35, 0.25]
            )[0]
            
            if location_type == 'corridor':
                location_name = f"{corridor} Corridor"
                # Generate traffic congestion index
                congestion_index = round(random.uniform(0.2, 1.0), 2)
                traffic_condition = random.choices(
                    self.traffic_conditions,
                    weights=[0.3, 0.35, 0.2, 0.1, 0.05]
                )[0]
            elif location_type == 'border_post':
                location_name = corridor_data['border_post']
                # Generate border wait time
                wait_times = self.border_wait_times.get(location_name, {'min_hours': 0.5, 'max_hours': 4})
                border_wait_hours = round(random.uniform(wait_times['min_hours'], wait_times['max_hours']), 2)
                congestion_index = border_wait_hours / 8  # Normalize to 0-1 range
                traffic_condition = 'Heavy' if border_wait_hours > 3 else 'Moderate'
            else:
                location_name = random.choice(corridor_data['major_towns'])
                congestion_index = round(random.uniform(0.2, 0.8), 2)
                traffic_condition = random.choice(self.traffic_conditions)
            
            # Generate road conditions
            road_condition = random.choices(
                self.road_conditions,
                weights=[0.5, 0.25, 0.15, 0.07, 0.03]
            )[0]
            
            # Generate traffic events
            has_event = random.random() > 0.85
            event_type = None
            event_description = None
            event_duration_hours = None
            
            if has_event:
                event_type = random.choice([
                    'Road Closure', 'Accident', 'Construction', 'Maintenance',
                    'Flooding', 'Landslide', 'Protest'
                ])
                event_description = fake.text(max_nb_chars=80)
                event_duration_hours = round(random.uniform(1, 24), 2)
            
            traffic = {
                'traffic_id': f'TRA_{uuid.uuid4().hex[:8].upper()}',
                'corridor_name': corridor,
                'location_name': location_name,
                'latitude': round(random.uniform(-2.2, -1.5), 6),
                'longitude': round(random.uniform(29.5, 30.5), 6),
                'timestamp': timestamp,
                'congestion_index': congestion_index,
                'traffic_condition': traffic_condition,
                'road_condition': road_condition,
                'average_speed_kmh': round(random.uniform(10, 80), 2),
                'travel_time_estimate_minutes': round(random.uniform(10, 240), 2),
                'road_closure': random.random() > 0.9,
                'construction_delay': random.random() > 0.85,
                'construction_delay_days': random.randint(1, 30) if random.random() > 0.85 else 0,
                'has_event': has_event,
                'event_type': event_type,
                'event_description': event_description,
                'event_duration_hours': event_duration_hours,
                'affected_route': f"{corridor} Route" if random.random() > 0.5 else None,
                'alternative_route': f"Alternative via {random.choice(['Kigali', 'Muhanga', 'Rwamagana'])}" if random.random() > 0.7 else None
            }
            
            # Add border-specific fields
            if location_type == 'border_post':
                traffic['border_wait_time_hours'] = border_wait_hours
                traffic['number_of_trucks_waiting'] = random.randint(5, 50)
                traffic['customs_clearance_time_hours'] = round(random.uniform(0.5, 4), 2)
                traffic['documentation_check_time_minutes'] = round(random.uniform(10, 60), 2)
            
            traffic_records.append(traffic)
        
        return traffic_records
    
    def _generate_market_data(self):
        """Generate market and geopolitical data"""
        market_records = []
        
        for i in range(self.num_market_records):
            country_data = random.choice(self.east_african_countries)
            timestamp = datetime.now() - timedelta(days=random.randint(0, 60))
            
            # Generate fuel price (based on index with daily variation)
            base_fuel_price = country_data['fuel_index'] * random.uniform(0.8, 1.2)
            fuel_price = round(base_fuel_price * (1 + random.uniform(-0.05, 0.05)), 2)
            
            # Generate exchange rate (based on base rate with daily variation)
            exchange_rate = round(
                country_data['exchange_rate_to_usd'] * (1 + random.uniform(-0.03, 0.03)),
                2
            )
            
            # Generate additional market metrics
            inflation_rate = round(random.uniform(2, 15), 2)
            interest_rate = round(random.uniform(4, 20), 2)
            
            # Determine if it's a holiday
            is_holiday = random.random() > 0.95  # 5% chance of holiday
            
            market = {
                'market_id': f'MKT_{uuid.uuid4().hex[:8].upper()}',
                'country': country_data['country'],
                'currency': country_data['currency'],
                'timestamp': timestamp,
                'fuel_price_index': fuel_price,
                'fuel_price_usd': round(fuel_price / exchange_rate, 4),
                'exchange_rate_to_usd': exchange_rate,
                'exchange_rate_trend': random.choice(['Appreciating', 'Depreciating', 'Stable']),
                'inflation_rate_percent': inflation_rate,
                'interest_rate_percent': interest_rate,
                'gdp_growth_rate_percent': round(random.uniform(-2, 8), 2),
                'trade_balance': random.choice(['Surplus', 'Deficit', 'Balanced']),
                'import_duty_rate_percent': round(random.uniform(0, 25), 2),
                'export_volume_index': round(random.uniform(80, 120), 2),
                'is_holiday': is_holiday,
                'holiday_name': random.choice([
                    'Independence Day', 'New Year', 'Christmas', 'Eid al-Fitr',
                    'Eid al-Adha', 'Labor Day', 'Liberation Day', 'Heroes Day',
                    'Umuganura', 'Christmas Day', 'Boxing Day'
                ]) if is_holiday else None,
                'holiday_type': random.choice(self.holiday_types) if is_holiday else None,
                'holiday_date': timestamp.strftime('%Y-%m-%d') if is_holiday else None,
                'market_volatility': random.choice(['Low', 'Medium', 'High']),
                'business_confidence_index': round(random.uniform(40, 100), 2),
                'consumer_spending_index': round(random.uniform(40, 100), 2),
                'logistics_performance_index': round(random.uniform(2, 5), 1)
            }
            
            market_records.append(market)
        
        return market_records
    
    def _generate_fuel_price_timeseries(self):
        """Generate time series fuel price data for East Africa"""
        fuel_prices = []
        
        for country_data in self.east_african_countries:
            base_price = country_data['fuel_index']
            
            # Generate 6 months of weekly data
            for week in range(24):
                timestamp = datetime.now() - timedelta(weeks=24-week)
                
                # Add weekly variation with trend
                weekly_variation = random.uniform(-0.03, 0.03) * (week / 24)
                price = base_price * (1 + weekly_variation + random.uniform(-0.02, 0.02))
                price = round(price, 2)
                
                fuel_prices.append({
                    'fuel_price_id': f'FPR_{uuid.uuid4().hex[:8].upper()}',
                    'country': country_data['country'],
                    'timestamp': timestamp,
                    'fuel_price_index': price,
                    'fuel_price_usd': round(price / country_data['exchange_rate_to_usd'], 4),
                    'week_number': week + 1,
                    'price_trend': 'Upward' if price > base_price else 'Downward' if price < base_price else 'Stable',
                    'supply_status': random.choice(['Normal', 'Tight', 'Abundant'])
                })
        
        return fuel_prices
    
    def _generate_exchange_rate_timeseries(self):
        """Generate time series exchange rate data"""
        exchange_rates = []
        
        for country_data in self.east_african_countries:
            base_rate = country_data['exchange_rate_to_usd']
            
            # Generate 6 months of daily data
            for day in range(180):
                timestamp = datetime.now() - timedelta(days=180-day)
                
                # Add daily variation with trend
                daily_variation = random.uniform(-0.01, 0.01) * (day / 180)
                rate = base_rate * (1 + daily_variation + random.uniform(-0.005, 0.005))
                rate = round(rate, 2)
                
                exchange_rates.append({
                    'exchange_rate_id': f'EXR_{uuid.uuid4().hex[:8].upper()}',
                    'country': country_data['country'],
                    'currency': country_data['currency'],
                    'timestamp': timestamp,
                    'exchange_rate_to_usd': rate,
                    'exchange_rate_to_rwf': round(rate / 1200, 4),
                    'day_of_year': day + 1,
                    'rate_change_percent': round(((rate - base_rate) / base_rate) * 100, 2),
                    'market_sentiment': random.choice(['Bullish', 'Bearish', 'Neutral'])
                })
        
        return exchange_rates
    
    def generate_data(self):
        """Generate all external data"""
        print("Generating external and contextual data...")
        
        # Generate main data
        print("  - Generating weather data...")
        self.weather_data = self._generate_weather_data()
        
        print("  - Generating traffic data...")
        self.traffic_data = self._generate_traffic_data()
        
        print("  - Generating market data...")
        self.market_data = self._generate_market_data()
        
        print("  - Generating fuel price time series...")
        self.fuel_prices = self._generate_fuel_price_timeseries()
        
        print("  - Generating exchange rate time series...")
        self.exchange_rates = self._generate_exchange_rate_timeseries()
        
        # Convert to DataFrames
        self.weather_df = pd.DataFrame(self.weather_data)
        self.traffic_df = pd.DataFrame(self.traffic_data)
        self.market_df = pd.DataFrame(self.market_data)
        self.fuel_prices_df = pd.DataFrame(self.fuel_prices)
        self.exchange_rates_df = pd.DataFrame(self.exchange_rates)
        
        # Convert datetime columns
        if 'timestamp' in self.weather_df.columns:
            self.weather_df['timestamp'] = pd.to_datetime(self.weather_df['timestamp'])
        
        if 'timestamp' in self.traffic_df.columns:
            self.traffic_df['timestamp'] = pd.to_datetime(self.traffic_df['timestamp'])
        
        if 'timestamp' in self.market_df.columns:
            self.market_df['timestamp'] = pd.to_datetime(self.market_df['timestamp'])
        
        if 'timestamp' in self.fuel_prices_df.columns:
            self.fuel_prices_df['timestamp'] = pd.to_datetime(self.fuel_prices_df['timestamp'])
        
        if 'timestamp' in self.exchange_rates_df.columns:
            self.exchange_rates_df['timestamp'] = pd.to_datetime(self.exchange_rates_df['timestamp'])
        
        return {
            'weather': self.weather_df,
            'traffic': self.traffic_df,
            'market': self.market_df,
            'fuel_prices': self.fuel_prices_df,
            'exchange_rates': self.exchange_rates_df
        }
    
    def save_csv(self, output_dir='agl_external_data_output'):
        """Save all data as CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.weather_df.to_csv(os.path.join(output_dir, 'weather_data.csv'), index=False)
        self.traffic_df.to_csv(os.path.join(output_dir, 'traffic_data.csv'), index=False)
        self.market_df.to_csv(os.path.join(output_dir, 'market_data.csv'), index=False)
        self.fuel_prices_df.to_csv(os.path.join(output_dir, 'fuel_prices.csv'), index=False)
        self.exchange_rates_df.to_csv(os.path.join(output_dir, 'exchange_rates.csv'), index=False)
        
        print(f"CSV files saved to {output_dir}")
    
    def save_parquet(self, output_dir='agl_external_data_output'):
        """Save all data as Parquet"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.weather_df.to_parquet(os.path.join(output_dir, 'weather_data.parquet'), index=False)
        self.traffic_df.to_parquet(os.path.join(output_dir, 'traffic_data.parquet'), index=False)
        self.market_df.to_parquet(os.path.join(output_dir, 'market_data.parquet'), index=False)
        self.fuel_prices_df.to_parquet(os.path.join(output_dir, 'fuel_prices.parquet'), index=False)
        self.exchange_rates_df.to_parquet(os.path.join(output_dir, 'exchange_rates.parquet'), index=False)
        
        print(f"Parquet files saved to {output_dir}")
    
    def save_json(self, output_dir='agl_external_data_output'):
        """Save all data as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        def convert_datetime(df):
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64']).columns:
                df_copy[col] = df_copy[col].astype(str)
            return df_copy
        
        convert_datetime(self.weather_df).to_json(
            os.path.join(output_dir, 'weather_data.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.traffic_df).to_json(
            os.path.join(output_dir, 'traffic_data.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.market_df).to_json(
            os.path.join(output_dir, 'market_data.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.fuel_prices_df).to_json(
            os.path.join(output_dir, 'fuel_prices.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.exchange_rates_df).to_json(
            os.path.join(output_dir, 'exchange_rates.json'), orient='records', date_format='iso'
        )
        
        print(f"JSON files saved to {output_dir}")
    
    def save_xml(self, output_dir='agl_external_data_output'):
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
        
        df_to_xml(self.weather_df, 'WeatherData', 'WeatherRecord', 
                  os.path.join(output_dir, 'weather_data.xml'))
        df_to_xml(self.traffic_df, 'TrafficData', 'TrafficRecord', 
                  os.path.join(output_dir, 'traffic_data.xml'))
        df_to_xml(self.market_df, 'MarketData', 'MarketRecord', 
                  os.path.join(output_dir, 'market_data.xml'))
        df_to_xml(self.fuel_prices_df, 'FuelPrices', 'FuelPrice', 
                  os.path.join(output_dir, 'fuel_prices.xml'))
        df_to_xml(self.exchange_rates_df, 'ExchangeRates', 'ExchangeRate', 
                  os.path.join(output_dir, 'exchange_rates.xml'))
        
        print(f"XML files saved to {output_dir}")
    
    def save_all_formats(self, output_dir='agl_external_data_output'):
        """Save all data in all formats"""
        print("\n" + "=" * 60)
        print("Saving external data in multiple formats...")
        print("=" * 60)
        
        self.save_csv(output_dir)
        self.save_parquet(output_dir)
        self.save_json(output_dir)
        self.save_xml(output_dir)
        
        print("\nAll external data files saved successfully!")

def main():
    """Main function to run the external data generator"""
    print("=" * 60)
    print("AGL Rwanda - External & Contextual Data Generator")
    print("=" * 60)
    
    # Initialize generator
    print("\nInitializing external data generator...")
    generator = AGLExternalDataGenerator(
        num_weather_records=5000,
        num_traffic_records=2000,
        num_market_records=1000
    )
    
    # Generate data
    data = generator.generate_data()
    
    # Display statistics
    print(f"\nData generated:")
    print(f"  - Weather Records: {len(data['weather'])}")
    print(f"  - Traffic Records: {len(data['traffic'])}")
    print(f"  - Market Records: {len(data['market'])}")
    print(f"  - Fuel Price Records: {len(data['fuel_prices'])}")
    print(f"  - Exchange Rate Records: {len(data['exchange_rates'])}")
    
    # Display sample data
    print("\nSample Weather Data:")
    print(data['weather'].head())
    
    print("\nSample Traffic Data:")
    print(data['traffic'].head())
    
    print("\nSample Market Data:")
    print(data['market'].head())
    
    print("\nSample Fuel Price Data:")
    print(data['fuel_prices'].head())
    
    print("\nSample Exchange Rate Data:")
    print(data['exchange_rates'].head())
    
    # Save in all formats
    generator.save_all_formats()
    
    print("\n" + "=" * 60)
    print("External data generation complete!")
    print("Check the 'agl_external_data_output' directory for all files")
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