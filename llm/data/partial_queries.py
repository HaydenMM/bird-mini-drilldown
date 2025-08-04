#!/usr/bin/env python3
import json
import re
import time
import os
import httpx
from openai import OpenAI

# Configure OpenAI client with SSL verification disabled

api_key="INSERT_API_KEY_HERE"

client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)  # Disable SSL verification
)

def extract_conditions(sql):
    """Extract removable conditional clauses from the SQL query."""
    conditions = re.findall(r'WHERE (.+)', sql, re.IGNORECASE)
    if conditions:
        # Split the conditions but handle BETWEEN separately
        all_conditions = conditions[0].split(" AND ")
        
        # Handle BETWEEN as a single unit
        final_conditions = []
        temp_condition = ""
        for condition in all_conditions:
            if "BETWEEN" in condition:
                if temp_condition:
                    final_conditions.append(temp_condition)
                temp_condition = condition  # Add BETWEEN condition as a whole
            else:
                if temp_condition:
                    final_conditions.append(temp_condition)
                    temp_condition = ""
                final_conditions.append(condition)
        
        if temp_condition:
            final_conditions.append(temp_condition)  # Add last BETWEEN condition if any

        return final_conditions
    return []

def generate_partial_queries(original_sql):
    """Generate a list of partial queries by progressively removing conditions."""
    conditions = extract_conditions(original_sql)
    base_query = re.sub(r'WHERE .+', '', original_sql, flags=re.IGNORECASE).strip()
    
    partial_queries = []
    for i in range(len(conditions)):
        partial_sql = base_query + " WHERE " + " AND ".join(conditions[:i+1])
        partial_queries.append(partial_sql)
    
    return partial_queries

def connect_gpt(engine, prompt, max_tokens=100, temperature=0.7, stop=None):
    """Connect to OpenAI GPT API and get the response."""
    MAX_API_RETRY = 10
    for i in range(MAX_API_RETRY):
        time.sleep(2)
        try:
            result = client.chat.completions.create(
                model=engine,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            return result.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {e}")
            time.sleep(4)
    return ""

def generate_nl_question(original_question, partial_sql):
    """Use LLM to generate a natural language question for a partial query."""
    prompt = f"""
    Lets take this step-by-step,
    Given the original question: "{original_question}", generate a new question that maintains the same structure and semantics but aligns with the following partial SQL query:
    {partial_sql}
    You are progressively generating questions that build on themselves from these provided partial queries. Do not include any information in your generated question that is not directly included in the partial query.
    The original question is the final query and should be used as reference to build out these progressive questions.
    """
    return connect_gpt("gpt-3.5-turbo-instruct", prompt)

def process_json(input_file, output_file):
    """Process the input JSON to generate partial queries and save the output JSON."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    output_data = []
    for entry in data:
        # Generate partial queries
        partial_queries = generate_partial_queries(entry["SQL"])

        for pq in partial_queries:
            new_entry = entry.copy()
            new_entry["SQL"] = pq
            if pq == entry["SQL"]:
                continue
            new_entry["question"] = generate_nl_question(entry["question"], pq)
            new_entry["is_original"] = False

            output_data.append(new_entry)

            # Save incrementally to avoid data loss in case of failure
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved {len(output_data)} entries so far...")

        # Mark and keep the original entry
        original_entry = entry.copy()
        original_entry["is_original"] = True
        output_data.append(original_entry)

    # Final save to ensure everything is written
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    process_json("mini_dev_postgresql.json", "mini_dev_postgresql_drill_down.json")

