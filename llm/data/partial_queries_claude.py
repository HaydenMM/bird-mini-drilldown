#!/usr/bin/env python3
import json
import time
import os
import httpx
import sqlparse
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from table_schema import generate_schema_prompt

claude_api_key = "YOUR_API_KEY"

client = Anthropic(
    api_key=claude_api_key,
    http_client=httpx.Client(verify=False)
)

def extract_conditions(sql):
    parsed = sqlparse.parse(sql)[0]
    where_clause = None

    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.Where):
            where_clause = token
            break

    if not where_clause:
        return []

    tokens = where_clause.tokens[2:]  # Skip "WHERE" and the whitespace
    conditions = []

    buffer = ""
    parens = 0
    in_between = False
    i = 0

    while i < len(tokens):
        token = tokens[i]
        val = str(token).strip().upper()

        # Stop parsing if we hit GROUP BY, ORDER BY, etc.
        if val.startswith(("GROUP BY", "ORDER BY", "LIMIT", "HAVING")):
            break

        # Parentheses tracking for subqueries or functions
        parens += token.value.count('(')
        parens -= token.value.count(')')

        if val == "BETWEEN":
            in_between = True
            buffer += " " + str(token)
            i += 1
            continue

        # Handle AND inside BETWEEN (BETWEEN X AND Y)
        if val == "AND" and in_between:
            buffer += " AND"
            i += 1
            if i < len(tokens):
                buffer += " " + str(tokens[i])
            in_between = False
        elif val == "AND" and parens == 0:
            # Top-level AND → condition split point
            if buffer.strip():
                conditions.append(buffer.strip())
            buffer = ""
        else:
            buffer += " " + str(token)

        i += 1

    if buffer.strip():
        conditions.append(buffer.strip())

    print(f"Extracted conditions: {conditions}")
    return conditions


def generate_partial_queries(original_sql):
    conditions = extract_conditions(original_sql)
    base_query = original_sql.split("WHERE")[0].strip()
    
    partial_queries = [base_query]
    for i in range(len(conditions)):
        partial_sql = base_query + " WHERE " + " AND ".join(conditions[:i+1])
        partial_queries.append(partial_sql)
    
    return partial_queries

chat_history = []

def connect_claude(engine, prompt, is_original, max_tokens=100, temperature=0.7, stop=None):
    global chat_history

    if is_original:
        print("Original question detected, resetting chat history.")
        chat_history = []
        return ""

    MAX_API_RETRY = 10

    for i in range(MAX_API_RETRY):
        time.sleep(1)
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            chat_history.append({"role": "user", "content": prompt})
            chat_history.append({"role": "assistant", "content": response.content[0].text})
            return response.content[0].text.strip()
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
    return connect_claude("claude-3.5-sonnet", prompt, is_original)

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
    process_json("mini_dev_postgresql.json", "mini_dev_postgresql_drill_down_claude.json")
