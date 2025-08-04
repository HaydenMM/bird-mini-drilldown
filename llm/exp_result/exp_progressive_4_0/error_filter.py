#!/usr/bin/env python3

import argparse
import json
import os
import hashlib
from openai import OpenAI
from tqdm import tqdm
import httpx
from table_schema import generate_schema_prompt

# ---------- Environment ----------
api_key = "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"
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HF_TOKEN"] = "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"

client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))

# ---------- Utilities ----------

def call_gpt4_turbo(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def build_prompt(schema_prompt: str, question: str, hallucination_type: str, sql_query: str) -> str:
    return f"""
    Given the following schema: {schema_prompt}

    Given this Natural Language question: "{question}"

    Given the tables above please adjust the SQL query to remove any instances of hallucination type: {hallucination_type}.
    The SQL query is: {sql_query}

    In your response, you do not need to mention your intermediate steps. 
    Do not include any comments in your response.
    Do not start with the symbol ```
    Only return the result PostgreSQL SQL code.
    Start from SELECT
    """.strip()

def load_questions(question_file):
    with open(question_file, "r") as f:
        data = json.load(f)
    q_map = {}
    for entry in data:
        q_map[(entry["question_id"], entry["db_id"])] = entry["question"]
    return q_map

def extract_categories(hallucinations):
    seen = set()
    for h in hallucinations:
        raw = h[0].strip()
        cleaned = raw.replace("Schema-Based: ", "").replace("Logic-Based: ", "").strip()
        seen.add(cleaned)
    return list(seen)

def make_entry_key(question_id, predicted_query):
    h = hashlib.md5(predicted_query.encode()).hexdigest()
    return f"{question_id}_{h[:8]}"

# ---------- Main ----------

def main(input_path: str, output_path: str, question_file: str):
    with open(input_path, "r") as f:
        full_data = json.load(f)

    question_map = load_questions(question_file)

    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            output_data = json.load(f)
    else:
        output_data = {}

    with open(output_path, "w") as out_file:
        for outer_entry in tqdm(full_data, desc="Processing SQL paths"):
            path_list = outer_entry.get("path", [])
            for entry in path_list:
                

                predicted_query = entry["predicted_query"]
                question_id = entry.get("question_id", "null")
                db_id = entry["db_id"]
                key = make_entry_key(question_id, predicted_query)


               
                question = question_map.get((question_id, db_id), "(No matching question found.)")
                hallucinations = entry.get("hallucination", [])

                halluc_categories = extract_categories(hallucinations)
                schema_path = f"/Users/hmmoore/Desktop/mini_dev/llm/data/dev_databases_old/{db_id}"
                schema_prompt = generate_schema_prompt("PostgreSQL", schema_path)

                current_query = predicted_query
                for halluc_type in halluc_categories:
                    prompt = build_prompt(schema_prompt, question, halluc_type, current_query)
                    current_query = call_gpt4_turbo(prompt)

                output_data[key] = {
                    "question_id": question_id,
                    "db_id": db_id,
                    "original": predicted_query,
                    "corrected": current_query,
                    "applied_fixes": halluc_categories
                    }

                
                # Save incrementally
                out_file.seek(0)
                json.dump(output_data, out_file, indent=2)
                out_file.truncate()
                out_file.flush()
                os.fsync(out_file.fileno())

    print(f"✅ Done. Output saved to {output_path}")


# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input SQL JSON")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    parser.add_argument("--questions", required=True, help="Path to questions JSON")
    args = parser.parse_args()

    main(args.input, args.output, args.questions)
