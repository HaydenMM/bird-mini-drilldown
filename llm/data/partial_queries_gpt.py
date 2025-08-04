#!/usr/bin/env python3
import json
import re
import time
import os
import httpx
from openai import OpenAI

from table_schema import generate_schema_prompt

# Configure OpenAI client with SSL verification disabled
api_key="YOUR_API_KEY"

client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)  # Disable SSL verification
)

def parse_sql_components(sql):
    """Parse SQL into its atomic components: SELECT, FROM, WHERE conditions."""
    sql = sql.strip()
    
    # Extract SELECT clause
    select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
    select_columns = select_match.group(1).strip() if select_match else ""
    
    # Extract FROM clause
    from_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
    table_name = from_match.group(1).strip() if from_match else ""
    
    # Extract WHERE conditions
    where_conditions = extract_conditions(sql)
    
    return {
        'select': select_columns,
        'from': table_name,
        'where_conditions': where_conditions
    }

def extract_conditions(sql):
    """Extract conditional clauses from the SQL query safely."""
    match = re.search(r'WHERE\s+(.+)', sql, re.IGNORECASE)
    if not match:
        return []

    condition_str = match.group(1)

    # Tokenize while respecting BETWEEN and quoted strings
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
            i += 3  # skip 'AND'
        else:
            buffer += ch
        i += 1
    if buffer:
        tokens.append(buffer.strip())

    # Fix re-joining BETWEEN pieces
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

def generate_atomic_queries(original_sql):
    """Generate progressive queries starting with SELECT FROM, then progressive WHERE conditions."""
    components = parse_sql_components(original_sql)
    queries = []
    
    # Step 1: SELECT + FROM (everything before WHERE)
    base_query = f"SELECT {components['select']} FROM {components['from']}"
    queries.append(base_query)
    
    # Step 2+: Progressive WHERE conditions
    if components['where_conditions']:
        for i in range(len(components['where_conditions'])):
            where_clause = " AND ".join(components['where_conditions'][:i+1])
            partial_sql = f"{base_query} WHERE {where_clause}"
            queries.append(partial_sql)
    
    print(f"Generated progressive queries: {queries}")
    return queries

chat_history = []

def connect_gpt(engine, prompt, is_original, max_tokens=150, temperature=0.7, stop=None):
    """Connect to OpenAI GPT API and get the response."""
    global chat_history

    if is_original:
        print("Original question detected, resetting chat history.")
        chat_history = []
        return ""
    
    MAX_API_RETRY = 10
    
    for i in range(MAX_API_RETRY):
        time.sleep(1)  # Simple backoff strategy
        try:
            if engine == "gpt-4-turbo-2":
                result = client.completions.create(
                    model="gpt-4-turbo",
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=stop,
                )
                return result.choices[0].text.strip()
            else:
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

def generate_atomic_nl_question(original_question, partial_sql, step_type, is_original):
    """Generate natural language questions for progressive SQL components."""
    
    if step_type == "select_from":
        prompt = f"""
        Given the original complex question: "{original_question}"
        
        Generate a natural language question that asks for the data columns from the specific table, but without any filtering conditions.
        
        The SQL query is: {partial_sql}
        
        This should ask for all the data from the table, like "What are the [columns] for all [table entities]?"
        
        Generate only the natural language question.
        """
    else:  # progressive where conditions
        prompt = f"""
        Given the original complex question: "{original_question}"
        
        Generate a natural language question that corresponds exactly to this partial SQL query:
        {partial_sql}
        
        This is a progressive step building toward the original complex question. The question should:
        - Ask for the same data columns as the original
        - Include only the filtering conditions present in this partial SQL
        - Be a logical step in the progression toward answering the original question
        - Use the same domain terminology and context as the original
        
        Generate only the natural language question.
        """
    
    return connect_gpt("gpt-4-turbo", prompt, is_original)

def process_json(input_file, output_file):
    """Process the input JSON to generate atomic progressive queries and save the output JSON."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    output_data = []
    
    for entry in data:
        print(f"\nProcessing entry {entry.get('question_id', 'unknown')}: {entry['question']}")
        
        # Generate atomic progressive queries
        atomic_queries = generate_atomic_queries(entry["SQL"])
        
        # Reset chat history for this entry
        _ = connect_gpt("gpt-4-turbo", "", True)
        
        for i, atomic_sql in enumerate(atomic_queries):
            # Skip if this is the original SQL (we'll add it at the end)
            if atomic_sql == entry["SQL"]:
                continue
                
            new_entry = entry.copy()
            new_entry["SQL"] = atomic_sql
            new_entry["is_original"] = False
            
            # Determine step type for appropriate prompt
            if i == 0:  # First query (SELECT FROM)
                step_type = "select_from"
            else:  # WHERE conditions
                step_type = "where_progressive"
            
            # Generate appropriate natural language question
            new_entry["question"] = generate_atomic_nl_question(
                entry["question"], 
                atomic_sql, 
                step_type, 
                False
            )
            
            output_data.append(new_entry)
            
            # Save incrementally
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"Generated: {new_entry['question']}")

        # Add the original entry at the end
        original_entry = entry.copy()
        original_entry["is_original"] = True
        output_data.append(original_entry)
        
        # Save after each complete entry
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Completed entry. Total entries so far: {len(output_data)}")

if __name__ == "__main__":
    process_json("full_dev_postgresql.json", "full_dev_postgresql_drill_down.json")
