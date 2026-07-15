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
import base64
import hashlib

# Initialize Faker for realistic data generation
fake = Faker()

class AGLDeliveryMilestoneGenerator:
    def __init__(self, num_shipments=1000):
        """
        Initialize the delivery and milestone data generator
        
        Args:
            num_shipments (int): Number of shipments to generate milestones for
        """
        self.num_shipments = num_shipments
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define milestone types and their sequences
        self.milestone_sequence = [
            'Booking Confirmed',
            'Cargo Received',
            'Customs Cleared',
            'Departed Origin',
            'Arrived at Border',
            'Border Cleared',
            'Departed Border',
            'Arrived at Destination',
            'Out for Delivery',
            'Delivered'
        ]
        
        # Define exception types
        self.exception_types = [
            'Over', 'Short', 'Damaged', 'Customs Hold', 
            'Weather Delay', 'Traffic Delay', 'Documentation Issue',
            'Vehicle Breakdown', 'Missed Connection', 'Package Lost'
        ]
        
        # Define damage categories
        self.damage_categories = [
            'Minor Scratches', 'Moderate Damage', 'Severe Damage',
            'Water Damage', 'Crushed', 'Tampered Seal', 'Temperature Damage',
            'Broken Pallets', 'Torn Packaging', 'Missing Parts'
        ]
        
        # Define delay reasons
        self.delay_reasons = [
            'Customs Inspection',
            'Incomplete Documentation',
            'Payment Clearance',
            'Weather Conditions',
            'Traffic Congestion',
            'Border Post Processing',
            'Vehicle Mechanical Issues',
            'Weight Discrepancy',
            'Prohibited Items Found',
            'Quarantine Hold',
            'Missing Paperwork',
            'Holiday Closure',
            'System Outage'
        ]
        
        # Define cargo conditions
        self.cargo_conditions = [
            'Excellent', 'Good', 'Satisfactory', 
            'Minor Wear', 'Damaged', 'Unsatisfactory'
        ]
        
        # Define border posts
        self.border_posts = [
            'Rusumo Border Post',
            'Gatuna Border Post',
            'Gisenyi Border Post',
            'Kagitumba Border Post',
            'Ruhwa Border Post'
        ]
        
        # Define origin/destination cities
        self.cities = [
            'Kigali', 'Rusumo', 'Gatuna', 'Gisenyi', 'Musanze',
            'Nyamata', 'Rwamagana', 'Rubavu', 'Kirehe', 'Kayonza'
        ]
        
        # Generate shipment references
        self.shipment_references = [f'AGL-{i+1:08d}' for i in range(num_shipments)]
    
    def _generate_digital_signature(self, name):
        """Generate a simulated digital signature (text-based)"""
        # Create a signature hash based on name and timestamp
        signature_data = f"{name}_{datetime.now().isoformat()}_{random.random()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Create a base64 encoded signature string
        signature_string = f"SIGNED_BY_{name.upper().replace(' ', '_')}_{signature_hash[:16]}"
        return base64.b64encode(signature_string.encode()).decode('utf-8')
    
    def _generate_milestone_timestamps(self, shipment_id, base_date):
        """Generate a sequence of milestone timestamps for a shipment"""
        milestones = []
        current_time = base_date
        
        # Generate random intervals between milestones
        for i, milestone_name in enumerate(self.milestone_sequence):
            # Add some randomness to timing
            if i == 0:
                # Booking confirmed - immediate
                interval = timedelta(hours=random.uniform(0, 2))
            elif i == 1:
                # Cargo received - within 1-24 hours
                interval = timedelta(hours=random.uniform(1, 24))
            elif i == 2:
                # Customs cleared - 2-48 hours
                interval = timedelta(hours=random.uniform(2, 48))
            elif i == 3:
                # Departed origin - 1-12 hours after customs
                interval = timedelta(hours=random.uniform(1, 12))
            elif i == 4:
                # Arrived at border - 4-12 hours
                interval = timedelta(hours=random.uniform(4, 12))
            elif i == 5:
                # Border cleared - 1-8 hours
                interval = timedelta(hours=random.uniform(1, 8))
            elif i == 6:
                # Departed border - 0.5-4 hours
                interval = timedelta(hours=random.uniform(0.5, 4))
            elif i == 7:
                # Arrived at destination - 2-10 hours
                interval = timedelta(hours=random.uniform(2, 10))
            elif i == 8:
                # Out for delivery - 1-6 hours
                interval = timedelta(hours=random.uniform(1, 6))
            else:
                # Delivered - 0.5-4 hours after out for delivery
                interval = timedelta(hours=random.uniform(0.5, 4))
            
            current_time += interval
            
            # Add some randomness to the milestone
            milestone = {
                'shipment_id': shipment_id,
                'milestone_name': milestone_name,
                'milestone_order': i + 1,
                'timestamp': current_time,
                'completed': random.random() > 0.1,  # 90% completion rate
                'location': random.choice(self.cities),
                'notes': fake.text(max_nb_chars=50) if random.random() > 0.7 else None
            }
            
            # Add border post for border-related milestones
            if 'Border' in milestone_name:
                milestone['border_post'] = random.choice(self.border_posts)
            
            milestones.append(milestone)
        
        return milestones
    
    def _generate_proof_of_delivery(self, shipment_id, delivery_milestone):
        """Generate PoD data for a shipment"""
        # Generate random delivery details
        recipient_name = fake.name()
        recipient_signature = self._generate_digital_signature(recipient_name)
        delivery_agent = fake.name()
        delivery_agent_signature = self._generate_digital_signature(delivery_agent)
        
        # Generate cargo condition report
        conditions = []
        num_items = random.randint(1, 5)
        for i in range(num_items):
            conditions.append({
                'item': f'Item_{i+1}',
                'condition': random.choice(self.cargo_conditions),
                'remarks': fake.text(max_nb_chars=30) if random.random() > 0.5 else None
            })
        
        # Generate photo evidence references
        photo_evidence = []
        if random.random() > 0.3:  # 70% chance of photos
            for i in range(random.randint(1, 3)):
                photo_evidence.append({
                    'photo_id': f'PHOTO_{uuid.uuid4().hex[:8].upper()}',
                    'description': f'Cargo photo {i+1}',
                    'timestamp': delivery_milestone['timestamp'] + timedelta(minutes=random.randint(0, 30))
                })
        
        pod = {
            'pod_id': f'POD_{shipment_id}',
            'shipment_id': shipment_id,
            'recipient_name': recipient_name,
            'recipient_contact': fake.phone_number(),
            'recipient_email': fake.email(),
            'recipient_signature': recipient_signature,
            'delivery_agent_name': delivery_agent,
            'delivery_agent_signature': delivery_agent_signature,
            'delivery_timestamp': delivery_milestone['timestamp'],
            'delivery_location': delivery_milestone['location'],
            'cargo_condition_summary': random.choice(self.cargo_conditions),
            'cargo_condition_details': json.dumps(conditions, default=str),
            'photo_evidence': json.dumps(photo_evidence, default=str),
            'temperature_at_delivery_c': round(random.uniform(15, 35), 2),
            'humidity_at_delivery_percent': round(random.uniform(30, 90), 2),
            'delivery_notes': fake.text(max_nb_chars=100) if random.random() > 0.5 else None,
            'received_by': fake.name()
        }
        
        return pod
    
    def _generate_exception_data(self, shipment_id, milestones):
        """Generate exception and discrepancy data for shipments"""
        exceptions = []
        
        # Determine if there are exceptions (30% chance)
        if random.random() < 0.3:
            num_exceptions = random.randint(1, 3)
            
            for i in range(num_exceptions):
                exception_type = random.choice(self.exception_types)
                
                # Find the milestone where exception occurred
                if 'Customs' in exception_type:
                    relevant_milestone = next(
                        (m for m in milestones if 'Customs' in m['milestone_name']), 
                        milestones[0]
                    )
                elif any(word in exception_type for word in ['Weather', 'Traffic', 'Vehicle']):
                    relevant_milestone = next(
                        (m for m in milestones if 'Departed' in m['milestone_name']), 
                        milestones[0]
                    )
                else:
                    relevant_milestone = milestones[-2] if len(milestones) > 1 else milestones[0]
                
                exception = {
                    'exception_id': f'EXC_{uuid.uuid4().hex[:8].upper()}',
                    'shipment_id': shipment_id,
                    'exception_type': exception_type,
                    'occurred_at': relevant_milestone['timestamp'] + timedelta(hours=random.uniform(0, 6)),
                    'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
                    'description': fake.text(max_nb_chars=150),
                    'action_taken': fake.text(max_nb_chars=100) if random.random() > 0.3 else None,
                    'resolution_date': None,
                    'status': random.choice(['Open', 'In Progress', 'Resolved', 'Closed']),
                    'assigned_to': fake.name() if random.random() > 0.5 else None
                }
                
                # Handle specific exception types
                if exception_type == 'Over':
                    exception['over_quantity'] = random.randint(1, 10)
                    exception['measured_weight'] = round(random.uniform(100, 5000), 2)
                    exception['documented_weight'] = round(exception['measured_weight'] * random.uniform(0.8, 0.95), 2)
                elif exception_type == 'Short':
                    exception['short_quantity'] = random.randint(1, 10)
                    exception['expected_quantity'] = random.randint(50, 200)
                    exception['actual_quantity'] = exception['expected_quantity'] - exception['short_quantity']
                elif exception_type == 'Damaged':
                    exception['damage_category'] = random.choice(self.damage_categories)
                    exception['damage_description'] = fake.text(max_nb_chars=80)
                    exception['damage_value'] = round(random.uniform(100, 10000), 2)
                    exception['damaged_items'] = random.randint(1, 20)
                
                # Add delay reason if applicable
                if exception_type in ['Customs Hold', 'Weather Delay', 'Traffic Delay', 'Documentation Issue']:
                    exception['delay_reason'] = random.choice(self.delay_reasons)
                    exception['delay_duration_hours'] = round(random.uniform(1, 72), 2)
                
                exceptions.append(exception)
        
        return exceptions
    
    def _generate_osd_logs(self, shipment_id):
        """Generate Over, Short, and Damaged (OS&D) logs"""
        osd_logs = []
        
        # 20% chance of OS&D log
        if random.random() < 0.2:
            num_items = random.randint(1, 5)
            for i in range(num_items):
                osd_type = random.choice(['Over', 'Short', 'Damaged'])
                osd_log = {
                    'osd_id': f'OSD_{uuid.uuid4().hex[:8].upper()}',
                    'shipment_id': shipment_id,
                    'osd_type': osd_type,
                    'item_description': fake.text(max_nb_chars=30),
                    'quantity': random.randint(1, 50),
                    'unit': random.choice(['kg', 'pcs', 'boxes', 'pallet']),
                    'reported_by': fake.name(),
                    'reported_date': datetime.now() - timedelta(days=random.randint(0, 30)),
                    'verified_by': fake.name() if random.random() > 0.5 else None,
                    'verified_date': None,
                    'discrepancy_value': round(random.uniform(50, 5000), 2),
                    'currency': random.choice(['USD', 'EUR', 'RWF']),
                    'status': random.choice(['Reported', 'Investigating', 'Resolved', 'Claim Filed']),
                    'notes': fake.text(max_nb_chars=100),
                    'claim_filed': random.random() > 0.7,
                    'claim_amount': round(random.uniform(100, 10000), 2) if random.random() > 0.7 else None
                }
                osd_logs.append(osd_log)
        
        return osd_logs
    
    def _generate_delivery_metrics(self, milestones):
        """Calculate delivery metrics from milestones"""
        # Find key milestones
        booking = next((m for m in milestones if m['milestone_name'] == 'Booking Confirmed'), None)
        customs = next((m for m in milestones if m['milestone_name'] == 'Customs Cleared'), None)
        border_arrival = next((m for m in milestones if m['milestone_name'] == 'Arrived at Border'), None)
        border_cleared = next((m for m in milestones if m['milestone_name'] == 'Border Cleared'), None)
        delivered = next((m for m in milestones if m['milestone_name'] == 'Delivered'), None)
        
        metrics = {}
        
        if booking and delivered:
            # Total transit time
            total_time = delivered['timestamp'] - booking['timestamp']
            metrics['total_transit_hours'] = round(total_time.total_seconds() / 3600, 2)
            metrics['total_transit_days'] = round(metrics['total_transit_hours'] / 24, 2)
        
        if customs and delivered:
            # Customs to delivery time
            customs_to_delivery = delivered['timestamp'] - customs['timestamp']
            metrics['customs_to_delivery_hours'] = round(customs_to_delivery.total_seconds() / 3600, 2)
        
        if border_arrival and border_cleared:
            # Border processing time
            border_time = border_cleared['timestamp'] - border_arrival['timestamp']
            metrics['border_processing_hours'] = round(border_time.total_seconds() / 3600, 2)
        
        # Calculate on-time delivery status
        if delivered and booking:
            # Simulate expected delivery time (5-10 days after booking)
            expected_delivery = booking['timestamp'] + timedelta(days=random.randint(5, 10))
            metrics['expected_delivery'] = expected_delivery
            metrics['on_time'] = delivered['timestamp'] <= expected_delivery
            if not metrics['on_time']:
                metrics['delay_hours'] = round((delivered['timestamp'] - expected_delivery).total_seconds() / 3600, 2)
        
        return metrics
    
    def generate_data(self):
        """Generate all delivery and milestone data"""
        all_milestones = []
        all_pods = []
        all_exceptions = []
        all_osd_logs = []
        all_delivery_metrics = []
        
        # Generate data for each shipment
        for shipment_id in self.shipment_references:
            # Generate base date (within last 90 days)
            base_date = datetime.now() - timedelta(days=random.randint(0, 90))
            
            # Generate milestones
            milestones = self._generate_milestone_timestamps(shipment_id, base_date)
            all_milestones.extend(milestones)
            
            # Generate PoD for delivered shipments (those with 'Delivered' milestone)
            delivered_milestone = next(
                (m for m in milestones if m['milestone_name'] == 'Delivered' and m['completed']), 
                None
            )
            if delivered_milestone:
                pod = self._generate_proof_of_delivery(shipment_id, delivered_milestone)
                all_pods.append(pod)
            
            # Generate exceptions
            exceptions = self._generate_exception_data(shipment_id, milestones)
            all_exceptions.extend(exceptions)
            
            # Generate OS&D logs
            osd_logs = self._generate_osd_logs(shipment_id)
            all_osd_logs.extend(osd_logs)
            
            # Calculate delivery metrics
            metrics = self._generate_delivery_metrics(milestones)
            if metrics:
                metrics['shipment_id'] = shipment_id
                all_delivery_metrics.append(metrics)
        
        # Convert to DataFrames
        self.milestones_df = pd.DataFrame(all_milestones)
        self.pods_df = pd.DataFrame(all_pods)
        self.exceptions_df = pd.DataFrame(all_exceptions)
        self.osd_df = pd.DataFrame(all_osd_logs)
        self.metrics_df = pd.DataFrame(all_delivery_metrics)
        
        # Convert datetime columns
        datetime_cols = ['timestamp', 'delivery_timestamp', 'occurred_at', 'resolution_date', 
                        'reported_date', 'verified_date', 'expected_delivery']
        for col in datetime_cols:
            for df in [self.milestones_df, self.pods_df, self.exceptions_df, 
                      self.osd_df, self.metrics_df]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
        
        return {
            'milestones': self.milestones_df,
            'proof_of_delivery': self.pods_df,
            'exceptions': self.exceptions_df,
            'osd_logs': self.osd_df,
            'delivery_metrics': self.metrics_df
        }
    
    def save_csv(self, output_dir='agl_delivery_data_output'):
        """Save all data as CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.milestones_df.to_csv(os.path.join(output_dir, 'milestones.csv'), index=False)
        self.pods_df.to_csv(os.path.join(output_dir, 'proof_of_delivery.csv'), index=False)
        self.exceptions_df.to_csv(os.path.join(output_dir, 'exceptions.csv'), index=False)
        self.osd_df.to_csv(os.path.join(output_dir, 'osd_logs.csv'), index=False)
        self.metrics_df.to_csv(os.path.join(output_dir, 'delivery_metrics.csv'), index=False)
        
        print(f"CSV files saved to {output_dir}")
    
    def save_parquet(self, output_dir='agl_delivery_data_output'):
        """Save all data as Parquet"""
        os.makedirs(output_dir, exist_ok=True)
        
        self.milestones_df.to_parquet(os.path.join(output_dir, 'milestones.parquet'), index=False)
        self.pods_df.to_parquet(os.path.join(output_dir, 'proof_of_delivery.parquet'), index=False)
        self.exceptions_df.to_parquet(os.path.join(output_dir, 'exceptions.parquet'), index=False)
        self.osd_df.to_parquet(os.path.join(output_dir, 'osd_logs.parquet'), index=False)
        self.metrics_df.to_parquet(os.path.join(output_dir, 'delivery_metrics.parquet'), index=False)
        
        print(f"Parquet files saved to {output_dir}")
    
    def save_json(self, output_dir='agl_delivery_data_output'):
        """Save all data as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        
        def convert_datetime(df):
            df_copy = df.copy()
            for col in df_copy.select_dtypes(include=['datetime64']).columns:
                df_copy[col] = df_copy[col].astype(str)
            return df_copy
        
        convert_datetime(self.milestones_df).to_json(
            os.path.join(output_dir, 'milestones.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.pods_df).to_json(
            os.path.join(output_dir, 'proof_of_delivery.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.exceptions_df).to_json(
            os.path.join(output_dir, 'exceptions.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.osd_df).to_json(
            os.path.join(output_dir, 'osd_logs.json'), orient='records', date_format='iso'
        )
        convert_datetime(self.metrics_df).to_json(
            os.path.join(output_dir, 'delivery_metrics.json'), orient='records', date_format='iso'
        )
        
        print(f"JSON files saved to {output_dir}")
    
    def save_xml(self, output_dir='agl_delivery_data_output'):
        """Save all data as XML"""
        os.makedirs(output_dir, exist_ok=True)
        
        def df_to_xml(df, root_name, element_name, filepath):
            root = ET.Element(root_name)
            
            for _, row in df.iterrows():
                elem = ET.SubElement(root, element_name)
                for col in df.columns:
                    child = ET.SubElement(elem, col.replace('_', ''))
                    value = row[col]
                    
                    # Handle different data types
                    if pd.isna(value):
                        child.text = ''
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        child.text = value.isoformat()
                    elif isinstance(value, (dict, list)):
                        # Convert dict/list to JSON string with default=str to handle datetime
                        child.text = json.dumps(value, default=str)
                    else:
                        child.text = str(value)
            
            xml_str = ET.tostring(root, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
        
        df_to_xml(self.milestones_df, 'Milestones', 'Milestone', 
                  os.path.join(output_dir, 'milestones.xml'))
        df_to_xml(self.pods_df, 'ProofOfDelivery', 'POD', 
                  os.path.join(output_dir, 'proof_of_delivery.xml'))
        df_to_xml(self.exceptions_df, 'Exceptions', 'Exception', 
                  os.path.join(output_dir, 'exceptions.xml'))
        df_to_xml(self.osd_df, 'OSDLogs', 'OSDLog', 
                  os.path.join(output_dir, 'osd_logs.xml'))
        df_to_xml(self.metrics_df, 'DeliveryMetrics', 'Metric', 
                  os.path.join(output_dir, 'delivery_metrics.xml'))
        
        print(f"XML files saved to {output_dir}")
    
    def save_all_formats(self, output_dir='agl_delivery_data_output'):
        """Save all data in all formats"""
        print("\n" + "=" * 60)
        print("Saving delivery data in multiple formats...")
        print("=" * 60)
        
        self.save_csv(output_dir)
        self.save_parquet(output_dir)
        self.save_json(output_dir)
        self.save_xml(output_dir)
        
        print("\nAll delivery data files saved successfully!")

def main():
    """Main function to run the delivery data generator"""
    print("=" * 60)
    print("AGL Rwanda - Delivery & Milestone Data Generator")
    print("=" * 60)
    
    # Initialize generator
    print("\nInitializing delivery data generator...")
    generator = AGLDeliveryMilestoneGenerator(num_shipments=1000)
    
    # Generate data
    print("Generating delivery data...")
    data = generator.generate_data()
    
    # Display statistics
    print(f"\nData generated:")
    print(f"  - Milestones: {len(data['milestones'])}")
    print(f"  - Proof of Delivery records: {len(data['proof_of_delivery'])}")
    print(f"  - Exceptions: {len(data['exceptions'])}")
    print(f"  - OS&D Logs: {len(data['osd_logs'])}")
    print(f"  - Delivery Metrics: {len(data['delivery_metrics'])}")
    
    # Display sample data
    print("\nSample Milestone Data:")
    print(data['milestones'].head())
    
    print("\nSample Proof of Delivery Data:")
    if not data['proof_of_delivery'].empty:
        pod_sample = data['proof_of_delivery'].head()
        # Truncate signature columns for display
        if 'recipient_signature' in pod_sample.columns:
            pod_sample['recipient_signature'] = pod_sample['recipient_signature'].str[:50] + '...'
        if 'delivery_agent_signature' in pod_sample.columns:
            pod_sample['delivery_agent_signature'] = pod_sample['delivery_agent_signature'].str[:50] + '...'
        print(pod_sample)
    
    print("\nSample Exceptions Data:")
    print(data['exceptions'].head())
    
    print("\nSample OS&D Logs:")
    print(data['osd_logs'].head())
    
    print("\nSample Delivery Metrics:")
    print(data['delivery_metrics'].head())
    
    # Save in all formats
    generator.save_all_formats()
    
    print("\n" + "=" * 60)
    print("Delivery data generation complete!")
    print("Check the 'agl_delivery_data_output' directory for all files")
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