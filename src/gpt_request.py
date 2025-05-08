#!/usr/bin/env python3
import argparse
import json
import os
import time
import requests
from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import GemmaTokenizer
import torch


from prompt import generate_combined_prompts_one

""" OpenAI configure """
api_key="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"

import os
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HF_TOKEN"] = "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"


# Create OpenAI client with SSL verification disabled
import httpx
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)  # Disable SSL verification safely
)


def new_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


import os
import torch
from transformers import AutoModelForCausalLM, GemmaTokenizer

chat_history = []
gemma_model = None
gemma_tokenizer = None

def connect_gpt(engine, prompt, max_tokens, temperature, stop):
    """
    Unified GPT/Gemma interface with chat history support.
    """
    MAX_API_RETRY = 10
    global chat_history, gemma_model, gemma_tokenizer

    for _ in range(MAX_API_RETRY):
        try:
            if engine == "gemma":
                if gemma_model is None or gemma_tokenizer is None:
                    print("Loading Gemma model...")
                    gemma_tokenizer = GemmaTokenizer.from_pretrained(
                        "google/gemma-2b",
                        trust_remote_code=True
                    )
                    gemma_model = AutoModelForCausalLM.from_pretrained(
                        "google/gemma-2b",
                        torch_dtype=torch.float16
                    )
                    gemma_model.eval()

                # Append user input to chat history
                chat_history.append({"role": "user", "content": prompt})
                if len(chat_history) > 10:
                    chat_history = chat_history[-5:]

                # Convert history to a single prompt string
                history_prompt = ""
                for turn in chat_history:
                    role = "User" if turn["role"] == "user" else "Assistant"
                    history_prompt += f"{role}: {turn['content']}\n"
                history_prompt += "Assistant:"

                device = "cuda" if torch.cuda.is_available() else "cpu"
                inputs = gemma_tokenizer(history_prompt, return_tensors="pt").to(device)
                gemma_model.to(device)

                with torch.no_grad():
                    outputs = gemma_model.generate(
                        **inputs,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        do_sample=temperature > 0,
                        eos_token_id=gemma_tokenizer.eos_token_id,
                    )

                full_output = gemma_tokenizer.decode(outputs[0], skip_special_tokens=True)
                response_content = full_output[len(history_prompt):].strip()
                chat_history.append({"role": "assistant", "content": response_content})

            else:
                # OpenAI GPT fallback
                chat_history.append({"role": "user", "content": prompt})
                if len(chat_history) > 10:
                    chat_history = chat_history[-5:]

                result = client.chat.completions.create(
                    model=engine,
                    messages=chat_history,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stop=stop,
                )
                response_content = result.choices[0].message.content
                chat_history.append({"role": "assistant", "content": response_content})

            print(response_content)
            break

        except Exception as e:
            response_content = f"error: {e}"
            print(response_content)
            time.sleep(4)

    return response_content



# def connect_gpt(engine, prompt, max_tokens, temperature, stop):
#     """
#     Function to connect to the GPT API and get the response.
#     """
#     MAX_API_RETRY = 10
#     for i in range(MAX_API_RETRY):
#         time.sleep(2)
#         try:
#             if engine == "gpt-3.5-turbo-instruct":
#                 result = client.completions.create(
#                     model="gpt-3.5-turbo-instruct",
#                     prompt=prompt,
#                     max_tokens=max_tokens,
#                     temperature=temperature,
#                     stop=stop,
#                 )
#                 result = result.choices[0].text
#             else:  # gpt-4-turbo, gpt-4, gpt-4-32k, gpt-3.5-turbo
#                 result = client.chat.completions.create(
#                     model=engine,
#                     messages=[{"role": "user", "content": prompt}],
#                     temperature=temperature,
#                     max_tokens=max_tokens,
#                     stop=stop,
#                 )
#                 result = result.choices[0].message.content
#                 print(result)
#             break
#         except Exception as e:
#             result = f"error: {e}"
#             print(result)
#             time.sleep(4)
#     return result


def decouple_question_schema(datasets, db_root_path):
    question_list = []
    db_path_list = []
    knowledge_list = []
    for data in datasets:
        question_list.append(data["question"])
        cur_db_path = os.path.join(db_root_path, data["db_id"], f"{data['db_id']}.sqlite")
        db_path_list.append(cur_db_path)
        # Uncomment if using partial/progressive query dataset
        # if data["is_original"]:
        #     knowledge_list.append(data["evidence"])
        # else:
        #     knowledge_list.append(None)

        knowledge_list.append(data["evidence"])

    return question_list, db_path_list, knowledge_list


def generate_sql_file(sql_lst, output_path=None):
    """
    Function to save the SQL results to a file.
    """
    sql_lst.sort(key=lambda x: x[1])
    result = {i: sql for i, (sql, _) in enumerate(sql_lst)}

    if output_path:
        new_directory(os.path.dirname(output_path))
        with open(output_path, "w") as f:
            json.dump(result, f, indent=4)

    return result


def post_process_response(response, db_path):
    sql = response if isinstance(response, str) else response.choices[0].message.content
    db_id = os.path.basename(db_path).replace(".sqlite", "")
    sql = f"{sql}\t----- bird -----\t{db_id}"
    return sql


def worker_function(question_data):
    """
    Function to process each question, generate the prompt,
    and collect the GPT response.
    """
    prompt, engine, db_path, question, i = question_data
    response = connect_gpt(engine, prompt, 512, 0, ["--", "\n\n", ";", "#"])
    sql = post_process_response(response, db_path)
    print(f"Processed {i}th question: {question}")
    return sql, i


def collect_response_from_gpt(
    db_path_list, question_list, engine, sql_dialect, num_threads=3, knowledge_list=None
):
    """
    Collect responses from GPT using multiple threads.
    """
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
    args_parser.add_argument("--engine", type=str, required=True, default="gpt-3.5-turbo")
    args_parser.add_argument("--data_output_path", type=str)
    args_parser.add_argument("--chain_of_thought", type=str)
    args_parser.add_argument("--num_processes", type=int, default=3)
    args_parser.add_argument("--sql_dialect", type=str, default="SQLite")
    args = args_parser.parse_args()

    eval_data = json.load(open(args.eval_path, "r"))

    question_list, db_path_list, knowledge_list = decouple_question_schema(
        datasets=eval_data, db_root_path=args.db_root_path
    )
    assert len(question_list) == len(db_path_list) == len(knowledge_list)

    responses = collect_response_from_gpt(
        db_path_list,
        question_list,
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

