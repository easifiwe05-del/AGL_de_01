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

# Initialize Faker for realistic data generation
fake = Faker()

class AGLDataGenerator:
    def __init__(self, num_records=1000):
        """
        Initialize the data generator with number of records to generate
        
        Args:
            num_records (int): Number of shipment records to generate
        """
        self.num_records = num_records
        self.seed = 42
        np.random.seed(self.seed)
        random.seed(self.seed)
        
        # Define predefined values for realistic data
        self.cargo_classifications = ['General', 'Hazardous', 'Perishable', 'Fragile', 'Oversized']
        self.invoice_statuses = ['Draft', 'Pending', 'Sent', 'Paid', 'Overdue', 'Cancelled']
        self.currencies = ['USD', 'EUR', 'GBP', 'RWF', 'KES', 'ZAR']
        self.hs_codes = ['8471.30', '8517.12', '8703.23', '3004.90', '0808.10', 
                        '2204.21', '9401.61', '8528.72', '8429.52', '4011.20']
        
        # Generate master data
        self.customers = self._generate_customers(200)
        self.shippers = self._generate_shippers(100)
        self.consignees = self._generate_consignees(150)
        
    def _generate_customers(self, n):
        """Generate customer master data"""
        customers = []
        for i in range(n):
            customers.append({
                'customer_id': f'CUST_{i:06d}',
                'customer_name': fake.company(),
                'customer_type': random.choice(['Exporter', 'Importer', 'Freight Forwarder']),
                'credit_limit': round(random.uniform(10000, 500000), 2),
                'payment_terms': random.choice(['Net 30', 'Net 60', 'Net 90', 'Cash', 'Letter of Credit']),
                'address': fake.address(),
                'contact_email': fake.email(),
                'contact_phone': fake.phone_number()
            })
        return customers
    
    def _generate_shippers(self, n):
        """Generate shipper master data"""
        shippers = []
        for i in range(n):
            shippers.append({
                'shipper_id': f'SHIP_{i:06d}',
                'shipper_name': fake.company(),
                'address': fake.address(),
                'contact_person': fake.name(),
                'contact_email': fake.email(),
                'contact_phone': fake.phone_number()
            })
        return shippers
    
    def _generate_consignees(self, n):
        """Generate consignee master data"""
        consignees = []
        for i in range(n):
            consignees.append({
                'consignee_id': f'CONS_{i:06d}',
                'consignee_name': fake.company(),
                'address': fake.address(),
                'contact_person': fake.name(),
                'contact_email': fake.email(),
                'contact_phone': fake.phone_number()
            })
        return consignees
    
    def _generate_shipment(self, shipment_id):
        """Generate a single shipment record"""
        customer = random.choice(self.customers)
        shipper = random.choice(self.shippers)
        consignee = random.choice(self.consignees)
        
        # Generate dates
        order_date = fake.date_time_between(start_date='-180d', end_date='now')
        dispatch_date = order_date + timedelta(days=random.randint(1, 10))
        delivery_deadline = dispatch_date + timedelta(days=random.randint(10, 45))
        
        # Generate cargo details
        weight = round(random.uniform(50, 50000), 2)
        volume = round(random.uniform(10, 200), 2)
        piece_count = random.randint(1, 500)
        
        # Generate financial metrics
        freight_charges = round(random.uniform(500, 50000), 2)
        customs_duties = round(freight_charges * random.uniform(0.05, 0.30), 2)
        tax_amount = round((freight_charges + customs_duties) * random.uniform(0.05, 0.20), 2)
        total_cost = freight_charges + customs_duties + tax_amount
        
        # Generate SLA information
        guaranteed_days = random.randint(3, 45)
        penalty_rate = round(random.uniform(0.01, 0.05), 3)
        
        return {
            'shipment_id': shipment_id,
            'customer_id': customer['customer_id'],
            'customer_name': customer['customer_name'],
            'shipper_id': shipper['shipper_id'],
            'shipper_name': shipper['shipper_name'],
            'consignee_id': consignee['consignee_id'],
            'consignee_name': consignee['consignee_name'],
            'billing_account': fake.iban(),
            
            # Cargo Manifest
            'weight_kg': weight,
            'volume_m3': volume,
            'piece_count': piece_count,
            'hs_code': random.choice(self.hs_codes),
            'cargo_classification': random.choice(self.cargo_classifications),
            'cargo_description': fake.text(max_nb_chars=50),
            'container_type': random.choice(['20FT', '40FT', '40HC', 'LCL', 'Air Cargo']),
            
            # Financial Metrics
            'freight_charges': freight_charges,
            'customs_duties': customs_duties,
            'tax_amount': tax_amount,
            'total_cost': total_cost,
            'currency': random.choice(self.currencies),
            'invoice_status': random.choice(self.invoice_statuses),
            'invoice_number': f'INV_{shipment_id}',
            'invoice_date': order_date + timedelta(days=random.randint(0, 5)),
            
            # SLA Information
            'order_date': order_date,
            'dispatch_date': dispatch_date,
            'delivery_deadline': delivery_deadline,
            'actual_delivery_date': delivery_deadline + timedelta(days=random.randint(-5, 10)) if random.random() > 0.2 else None,
            'guaranteed_transit_days': guaranteed_days,
            'penalty_threshold_days': random.randint(1, 5),
            'penalty_rate': penalty_rate,
            'sla_compliance': random.choice(['Compliant', 'Non-Compliant', 'Pending']),
            'delay_reason': random.choice(['Weather', 'Customs', 'Traffic', 'None', 'Documentation']),
            
            # Additional metadata
            'status': random.choice(['Planned', 'In Transit', 'Delivered', 'Delayed', 'Cancelled']),
            'priority': random.choice(['High', 'Medium', 'Low']),
            'created_at': order_date,
            'updated_at': fake.date_time_between(start_date=order_date, end_date='now'),
            'notes': fake.text(max_nb_chars=100)
        }
    
    def generate_data(self):
        """Generate all shipment records"""
        shipments = []
        for i in range(self.num_records):
            shipment_id = f'SHIP_{i+1:08d}'
            shipments.append(self._generate_shipment(shipment_id))
        
        self.df = pd.DataFrame(shipments)
        
        # Convert datetime columns for proper formatting
        datetime_cols = ['order_date', 'dispatch_date', 'delivery_deadline', 
                        'actual_delivery_date', 'created_at', 'updated_at', 'invoice_date']
        for col in datetime_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col])
        
        return self.df
    
    def save_csv(self, filepath='agl_shipment_data.csv'):
        """Save data as CSV"""
        self.df.to_csv(filepath, index=False)
        print(f"CSV saved to {filepath}")
        return filepath
    
    def save_parquet(self, filepath='agl_shipment_data.parquet'):
        """Save data as Parquet"""
        self.df.to_parquet(filepath, index=False)
        print(f"Parquet saved to {filepath}")
        return filepath
    
    def save_json(self, filepath='agl_shipment_data.json'):
        """Save data as JSON"""
        # Handle datetime objects for JSON serialization
        df_copy = self.df.copy()
        for col in df_copy.select_dtypes(include=['datetime64']).columns:
            df_copy[col] = df_copy[col].astype(str)
        
        df_copy.to_json(filepath, orient='records', date_format='iso')
        print(f"JSON saved to {filepath}")
        return filepath
    
    def save_xml(self, filepath='agl_shipment_data.xml'):
        """Save data as XML"""
        root = ET.Element('Shipments')
        
        for _, row in self.df.iterrows():
            shipment_elem = ET.SubElement(root, 'Shipment')
            
            for col in self.df.columns:
                child = ET.SubElement(shipment_elem, col)
                value = row[col]
                
                # Handle different data types
                if pd.isna(value):
                    child.text = ''
                elif isinstance(value, (pd.Timestamp, datetime)):
                    child.text = value.isoformat()
                else:
                    child.text = str(value)
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        print(f"XML saved to {filepath}")
        return filepath
    
    def save_all_formats(self, output_dir='data_output'):
        """Save data in all formats"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate data if not already generated
        if not hasattr(self, 'df'):
            self.generate_data()
        
        # Save in all formats
        self.save_csv(os.path.join(output_dir, 'agl_shipment_data.csv'))
        self.save_parquet(os.path.join(output_dir, 'agl_shipment_data.parquet'))
        self.save_json(os.path.join(output_dir, 'agl_shipment_data.json'))
        self.save_xml(os.path.join(output_dir, 'agl_shipment_data.xml'))
        
        # Also save master data separately
        self._save_master_data(output_dir)
        
        print("\nAll data files saved successfully!")
    
    def _save_master_data(self, output_dir):
        """Save master data files"""
        # Customers master
        pd.DataFrame(self.customers).to_csv(os.path.join(output_dir, 'customers_master.csv'), index=False)
        pd.DataFrame(self.customers).to_json(os.path.join(output_dir, 'customers_master.json'), orient='records')
        
        # Shippers master
        pd.DataFrame(self.shippers).to_csv(os.path.join(output_dir, 'shippers_master.csv'), index=False)
        pd.DataFrame(self.shippers).to_json(os.path.join(output_dir, 'shippers_master.json'), orient='records')
        
        # Consignees master
        pd.DataFrame(self.consignees).to_csv(os.path.join(output_dir, 'consignees_master.csv'), index=False)
        pd.DataFrame(self.consignees).to_json(os.path.join(output_dir, 'consignees_master.json'), orient='records')
        
        print(f"Master data saved to {output_dir}")

def main():
    """Main function to run the data generator"""
    print("=" * 60)
    print("AGL Rwanda - Shipment & Order Data Generator")
    print("=" * 60)
    
    # Initialize generator with 1000 records
    print("\nInitializing data generator...")
    generator = AGLDataGenerator(num_records=1000)
    
    # Generate data
    print("Generating data...")
    df = generator.generate_data()
    
    # Display sample and statistics
    print(f"\nGenerated {len(df)} shipment records")
    print(f"\nData columns: {len(df.columns)}")
    print(f"Column names: {list(df.columns)}")
    
    # Show sample data
    print("\nSample data (first 5 rows):")
    print(df.head())
    
    print("\nData types:")
    print(df.dtypes)
    
    print("\nStatistical summary:")
    print(df.describe())
    
    # Save in all formats
    print("\n" + "=" * 60)
    print("Saving data in multiple formats...")
    print("=" * 60)
    generator.save_all_formats('agl_data_output')
    
    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("Check the 'agl_data_output' directory for all files")
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
