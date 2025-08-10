import csv
import json
import os
from datetime import datetime
import uuid

class FileManager:
    def __init__(self):
        self.base_path = 'data'
    
    def read_csv(self, filepath):
        """Read CSV file and return list of dictionaries"""
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except FileNotFoundError:
            return []
    
    def write_csv(self, filepath, data, fieldnames):
        """Write data to CSV file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def append_csv(self, filepath, data, fieldnames):
        """Append data to CSV file"""
        file_exists = os.path.exists(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
    
    def read_json(self, filepath):
        """Read JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def write_json(self, filepath, data):
        """Write data to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def generate_id(self):
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def get_timestamp(self):
        """Get current timestamp"""
        return datetime.now().isoformat()

# Global instance
file_manager = FileManager()
