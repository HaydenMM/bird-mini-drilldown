import json
import re

def clean_query(query):
    """Removes unwanted characters from SQL queries."""
    # Remove tab characters, newlines, slashes, and triple dashes
    query = re.sub(r'[\t\n/]', ' ', query)
    query = re.sub(r'---.*', '', query)  # Remove anything after ---
    return query.strip()

def process_json(file_path, output_path):
    """Reads a JSON file, cleans queries, and saves the cleaned output."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {key: clean_query(value) for key, value in data.items()}
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4)
    
    print(f"Cleaned data saved to {output_path}")

# Example usage
input_file = "predict_mini_dev_gpt-4-turbo_cot_PostgreSQL.json"  # Replace with your input JSON file
output_file = "predict_mini_dev_gpt-4-turbo_cot_PostgreSQL_cleaned_queries.json"
process_json(input_file, output_file)

