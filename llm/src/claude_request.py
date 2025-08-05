#!/usr/bin/env python3
import argparse
import json
import os
import time
from anthropic import Anthropic
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import GemmaTokenizer
import torch

from prompt import generate_combined_prompts_one

""" Anthropic configure """
api_key = "API_KEY"

os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HF_TOKEN"] = "HF_API_KEY"

# Create Anthropic client
client = Anthropic(api_key=api_key)

def new_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

chat_history = []
gemma_model = None
gemma_tokenizer = None

def connect_gpt(engine, prompt, max_tokens, temperature, stop, is_original):
    """
    Unified Claude interface using Messages API (Claude 3.5 Sonnet).
    """
    global chat_history
    MAX_API_RETRY = 10

    for _ in range(MAX_API_RETRY):
        try:
            response = client.messages.create(
                model=engine,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    *chat_history,
                    {"role": "user", "content": prompt}
                ]
            )

            response_content = response.content[0].text.strip()

            chat_history.append({"role": "user", "content": prompt})
            chat_history.append({"role": "assistant", "content": response_content})

            if is_original:
                print("Original question detected, resetting chat history.")
                chat_history = []

            break

        except Exception as e:
            response_content = f"error: {e}"
            print(response_content)
            time.sleep(4)

    return response_content

def decouple_question_schema(datasets, db_root_path):
    question_list = []
    is_original = []
    db_path_list = []
    knowledge_list = []
    for data in datasets:
        is_original.append(data.get("is_original", True))
        question_list.append(data["question"])
        cur_db_path = os.path.join(db_root_path, data["db_id"], f"{data['db_id']}.sqlite")
        db_path_list.append(cur_db_path)
        if data["is_original"]:
            knowledge_list.append(data["evidence"])
        else:
            knowledge_list.append(None)

    return question_list, db_path_list, knowledge_list, is_original

def generate_sql_file(sql_lst, output_path=None):
    sql_lst.sort(key=lambda x: x[1])
    result = {i: sql for i, (sql, _) in enumerate(sql_lst)}

    if output_path:
        new_directory(os.path.dirname(output_path))
        with open(output_path, "w") as f:
            json.dump(result, f, indent=4)

    return result

def post_process_response(response, db_path):
    sql = response if isinstance(response, str) else response.strip()
    db_id = os.path.basename(db_path).replace(".sqlite", "")
    sql = f"{sql}\t----- bird -----\t{db_id}"
    return sql

def worker_function(question_data):
    prompt, engine, db_path, question, i, is_original = question_data
    response = connect_gpt(engine, prompt, 512, 0, ["--", "\n\n", ";", "#"], is_original)
    sql = post_process_response(response, db_path)
    print(f"Processed {i}th question: {question}")
    return sql, i

def collect_response_from_gpt(
    db_path_list, question_list, is_original, engine, sql_dialect, num_threads=3, knowledge_list=None
):
    tasks = [
        (
            generate_combined_prompts_one(
                db_path=db_path_list[i],
                question=question_list[i],
                sql_dialect=sql_dialect,
                knowledge=knowledge_list[i] if knowledge_list else None,
            ),
            engine,
            db_path_list[i],
            question_list[i],
            i,
            is_original[i],
        )
        for i in range(len(question_list))
    ]
    responses = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_task = {executor.submit(worker_function, task): task for task in tasks}
        for future in tqdm(as_completed(future_to_task), total=len(tasks)):
            responses.append(future.result())
    return responses

if __name__ == "__main__":
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--eval_path", type=str, default="")
    args_parser.add_argument("--mode", type=str, default="dev")
    args_parser.add_argument("--test_path", type=str, default="")
    args_parser.add_argument("--use_knowledge", type=str, default="False")
    args_parser.add_argument("--db_root_path", type=str, default="")
    args_parser.add_argument("--api_key", type=str, required=True)
    args_parser.add_argument("--engine", type=str, required=True, default="claude-3.5-sonnet-20240620")
    args_parser.add_argument("--data_output_path", type=str)
    args_parser.add_argument("--chain_of_thought", type=str)
    args_parser.add_argument("--num_processes", type=int, default=3)
    args_parser.add_argument("--sql_dialect", type=str, default="SQLite")
    args = args_parser.parse_args()

    eval_data = json.load(open(args.eval_path, "r"))

    question_list, db_path_list, knowledge_list, is_original = decouple_question_schema(
        datasets=eval_data, db_root_path=args.db_root_path
    )
    print(len(question_list), len(db_path_list), len(knowledge_list))
    assert len(question_list) == len(db_path_list) == len(knowledge_list)

    responses = collect_response_from_gpt(
        db_path_list,
        question_list,
        is_original,
        args.engine,
        args.sql_dialect,
        args.num_processes,
        knowledge_list if args.use_knowledge == "True" else None,
    )

    output_name = (
        f"{args.data_output_path}predict_{args.mode}_{args.engine}"
        f"{'_cot' if args.chain_of_thought == 'True' else ''}_{args.sql_dialect}.json"
    )

    generate_sql_file(sql_lst=responses, output_path=output_name)

    print(
        f"Successfully collected results from {args.engine} for {args.mode} evaluation; "
        f"SQL dialect: {args.sql_dialect}, Use knowledge: {args.use_knowledge}, Use COT: {args.chain_of_thought}"
    )
