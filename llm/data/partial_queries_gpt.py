#!/usr/bin/env python3
import json
import re
import time
import os
import openai

from table_schema import generate_schema_prompt

openai.api_key = "YOUR_OPENAI_API_KEY"
client = openai

def extract_conditions(sql):
    match = re.search(r'WHERE\s+(.+)', sql, re.IGNORECASE)
    if not match:
        return []

    condition_str = match.group(1)
    tokens = []
    buffer = ''
    in_quotes = False
    parens = 0
    i = 0
    while i < len(condition_str):
        ch = condition_str[i]
        if ch == "'" and (i == 0 or condition_str[i-1] != "\\"):
            in_quotes = not in_quotes
            buffer += ch
        elif ch == '(':
            parens += 1
            buffer += ch
        elif ch == ')':
            parens -= 1
            buffer += ch
        elif not in_quotes and parens == 0 and condition_str[i:i+4].upper() == ' AND':
            tokens.append(buffer.strip())
            buffer = ''
            i += 3
        else:
            buffer += ch
        i += 1
    if buffer:
        tokens.append(buffer.strip())

    merged = []
    skip = False
    for j in range(len(tokens)):
        if skip:
            skip = False
            continue
        if 'BETWEEN' in tokens[j].upper() and j + 1 < len(tokens):
            merged.append(tokens[j] + ' AND ' + tokens[j + 1])
            skip = True
        else:
            merged.append(tokens[j])

    print(f"Extracted conditions: {merged}")
    return merged

def generate_partial_queries(original_sql):
    conditions = extract_conditions(original_sql)
    base_query = re.sub(r'WHERE .+', '', original_sql, flags=re.IGNORECASE).strip()
    
    partial_queries = [base_query]
    for i in range(len(conditions)):
        partial_sql = base_query + " WHERE " + " AND ".join(conditions[:i+1])
        partial_queries.append(partial_sql)
    
    return partial_queries

chat_history = []

def connect_gpt(engine, prompt, is_original, max_tokens=150, temperature=0.7, stop=None):
    global chat_history

    if is_original:
        print("Original question detected, resetting chat history.")
        chat_history = []
        return ""
    
    MAX_API_RETRY = 10
    
    for i in range(MAX_API_RETRY):
        time.sleep(1)
        try:
            chat_history.append({"role": "user", "content": prompt})
            result = client.chat.completions.create(
                model=engine,
                messages=chat_history,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
            )
            response_content = result.choices[0].message.content
            chat_history.append({"role": "assistant", "content": response_content})

            return result.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error: {e}")
            time.sleep(1)
    return ""

def generate_nl_question(original_question, partial_sql, is_original):
    prompt = f"""
        Let's take this step-by-step.

        Given the original question: "{original_question}"

        Generate a new natural language question that maintains the same structure and semantics but aligns with the following partial SQL query:

        {partial_sql}

        You are progressively generating questions that build on themselves from these provided partial queries. Do not include any information in your generated question that is not directly included in the partial query.

        The original question is the final query and should be used as reference to build out these progressive questions.

        Requirements:
        - The generated question must correspond exactly to what this partial SQL retrieves
        - Maintain the same domain context and terminology as the original question  
        - The question should be answerable using only this partial SQL query
        - This should be a logical step toward answering the original complex question

        Generate only the natural language question.
        """
    return connect_gpt("gpt-4", prompt, is_original)

def process_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    output_data = []
    for entry in data:
        partial_queries = generate_partial_queries(entry["SQL"])

        for pq in partial_queries:
            new_entry = entry.copy()
            new_entry["SQL"] = pq
            if pq == entry["SQL"]:
                continue
            new_entry["question"] = generate_nl_question(entry["question"], pq, False)
            new_entry["is_original"] = False

            output_data.append(new_entry)
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved {len(output_data)} entries so far...")

        original_entry = entry.copy()
        original_entry["is_original"] = True
        _ = generate_nl_question(entry["question"], "", True)
        output_data.append(original_entry)

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

if __name__ == "__main__":
    process_json("mini_dev_postgresql.json", "mini_dev_postgresql_drill_down_gpt.json")
