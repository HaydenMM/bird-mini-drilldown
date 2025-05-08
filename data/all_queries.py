import json
import os

def save_sql_queries(input_file, output_file):
    """Read the input JSON file and save all SQL queries into a single .sql file."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Open the output file in append mode
    with open(output_file, 'w') as sql_file:
        for entry in data:
            sql_query = entry.get("SQL")
            db_id = entry.get("db_id", "unknown_db")

            if sql_query:
                # Write the SQL query and db_id to the file in the required format
                sql_file.write(f"{sql_query}\t{db_id}\n")
                print(f"Added SQL query to: {output_file}")

if __name__ == "__main__":
    save_sql_queries("mini_dev_postgresql_partial.json", "all_queries.sql")

