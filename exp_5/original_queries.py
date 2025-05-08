import json
import os

def save_sql_queries(input_file, partial_file, output_file):
    """Read the input JSON file and save all SQL queries into a single .sql file."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    with open(partial_file, 'r') as f:
        partial = json.load(f)

    json_out = {}
    i = 0
    # Open the output file in append mode
    with open(output_file, 'w') as out_file:
        for entry in data:
            if partial[int(entry)]["is_original"] == True:
                json_out[str(i)] = data[entry]
                i += 1
        
        json.dump(json_out, out_file, indent=4)

if __name__ == "__main__":
    save_sql_queries("predict_mini_dev_gpt-4-turbo_cot_PostgreSQL_cleaned_queries.json", "/Users/hmmoore/Desktop/mini_dev/llm/data/mini_dev_postgresql_partial.json", "original_queries.json")

