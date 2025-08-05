import json

# Load JSON file
with open("./llm/data/mini_dev_postgresql_drill_down.json", "r") as json_file:
    data = json.load(json_file)  # Load as list of dictionaries

# Write to JSONL file
with open("./llm/data/mini_dev_postgresql_drill_down.jsonl", "w") as jsonl_file:
    for item in data:
        jsonl_file.write(json.dumps(item) + "\n")  # Write each object as a new line

