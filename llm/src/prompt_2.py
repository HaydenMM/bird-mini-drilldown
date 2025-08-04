from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import GemmaTokenizer
import torch
from gpt_request import connect_gpt


from table_schema import generate_schema_prompt

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

seen_db_paths = set()

def generate_combined_prompts_one(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \nA schema-based schema contradiction refers to the instance where incorrect SQL contradicts schema structure.

        \nHere is an example of a schema-based schema contradiction:
        Question: What language is the set of 180 cards that belongs to the Ravnica block translated into?
        Correct SQL: SELECT T2.language FROM sets AS T1 INNER JOIN set_translations AS T2 ON WHERE T1.block = ‘Ravnica’ AND T1.baseSetSize = 180
        Wrong SQL: SELECT language FROM sets WHERE baseSetSize = 180 AND block = ‘Ravnica’

        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Schema-Based Schema Contradiction.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the {sql_dialect} SQL code that would cause a Schema-Based Schema Contradiction for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts

def generate_combined_prompts_two(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \nA schema-based attribute overanalysis efers to the instance where unnecessary attributes are introduced, leading to a contradiction with the intended result format.

        \nHere is an example of a schema-based attribute overanalysis:
        Question: Which player is the tallest?
        Correct SQL: SELECT player_name FROM Player ORDER BY height DESC LIMIT 1
        Wrong SQL: SELECT player_name, height FROM Player ORDER BY height DESC LIMIT 1
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Schema-Based Attribute Overanalysis.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```

        You only need to return the {sql_dialect} SQL code that would cause a Schema-Based Attribute Overanalysis for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts


def generate_combined_prompts_three(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \n A schema-based value misrepresentation refers to the instance where the model imagines a reasonable but non-existent value format in the schema.
        
        \nHere is an example of a schema-based value misrepresentation:
        Question: Give the race of the blue-haired men superhero.
        Correct SQL: SELECT ... WHERE colour.colour = ‘Blue’ AND gender.gender = ‘Male’
        Wrong SQL: SELECT ... WHERE colour.colour = ‘blue’ AND gender.gender = ‘M’
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Schema-Based Value Misrepresentation.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the {sql_dialect} SQL code that would cause a Schema-Based Value Misrepresentation for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts



def generate_combined_prompts_four(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \n A logic-based join redundancy refers to the instance where the SQL joins unnecessary tables for complex text-to-SQL cases.
        
        \nHere is an example of a logic-based join redundancy:
        Question: Determine the bond type formed in the chemical compound containing element Tellurium.
        Correct SQL: SELECT T2.bond_type FROM atom AS T1 INNER JOIN bond AS T2 ON WHERE T1.element = ‘te’
        Wrong SQL: SELECT bond_type FROM bond INNER JOIN connected ON ... INNER JOIN atom ON ... WHERE atom.element = ‘te’
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Logic-Based Join Redundancy.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the {sql_dialect} SQL code that would cause a Logic-Based Join Redundancy for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts

def generate_combined_prompts_five(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \n A logic-based clause abuse refers to the instance where clauses such as GROUP BY are abused, disrupting the correct order or limitation of results.
        
        \nHere is an example of a logic-based clause abuse:
        Question: Among the posts that were voted by user 14, what is the id of the most valuable post?
        Correct SQL: SELECT post.Id ... WHERE votes.UserId = 14 ORDER BY post.FavoriteCount DESC LIMIT 1
        Wrong SQL: SELECT post.Id FROM votes INNER JOIN posts ON ... WHERE votes.UserId = 14 GROUP BY post.Id ORDER BY post.FavoriteCount DESC LIMIT 1
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Logic-Based Clause Abuse.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the {sql_dialect} SQL code that would cause a Logic-Based Clause Abuse for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts


def generate_combined_prompts_six(db_path, question, sql_dialect, knowledge=None):
 
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    instruction_prompt_1 = f"""
        \n A logic-based mathematical delusion refers to the instance where the model fails to convert mathematical knowledge or logic into correct SQL functions, resorting to expressions such as imagined functions.
        
        \nHere is an example of a logic-based mathematical delusion:
        Question: What is the percentage of the amount 50 received by the Student Club among members?
        Correct SQL: SELECT CAST(SUM(CASE WHEN income.amount = 50 THEN 1.0 ELSE 0 END) AS REAL) * 100 / COUNT(income.income_id) FROM ... WHERE member.position = ‘Member’
        Wrong SQL: SELECT DIVIDE(SUM(CASE WHEN income.amount = 50 THEN 1 ELSE 0 END), COUNT(member.member_id)) FROM ... WHERE member.position = ‘Member’
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, 
        we want to generate an example of a Logic-Based Mathematical Delusion for this question: {question}.
    """

    instruction_prompt_2 = f"""
        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the {sql_dialect} SQL code that would cause a Logic-Based Mathematical Delusion for the question: {question}
        start from SELECT
    """

    combined_prompts = "\n\n".join([
        schema_prompt, instruction_prompt_1, instruction_prompt_2
    ])
    return combined_prompts


def generate_combined_prompts(db_path, question, sql_dialect, knowledge=None):
    schema_prompt = generate_schema_prompt(sql_dialect, db_path)

    combined_one = generate_combined_prompts_one(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    )
    # pass combined one through gpt turbo 4 to get an example of a Schema-Based Schema Contradiction Error
    gpt_response_one = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_one,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )

    combined_two = generate_combined_prompts_two(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    )
    # pass combined two through gpt turbo 4 to get an example of a Schema-Based Attribute Overanalysis Error
    gpt_response_two = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_two,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )

    combined_three = generate_combined_prompts_three(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    )

    # pass combined three through gpt turbo 4 to get an example of a Schema-Based Value Misrepresentation Error
    gpt_response_three = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_three,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )
    combined_four = generate_combined_prompts_four(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    )

    # pass combined four through gpt turbo 4 to get an example of a Logic-Based Join Redundancy
    gpt_response_four = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_four,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )

    combined_five = generate_combined_prompts_five(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    )
    # pass combined five through gpt turbo 4 to get an example of a Logic-Based Clause Abuse
    gpt_response_five = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_five,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )
    combined_six = generate_combined_prompts_six(
        db_path=db_path,
        question=question,
        sql_dialect=sql_dialect,
        knowledge=knowledge
    ) 
    # pass combined six through gpt turbo 4 to get an example of a Logic-Based Mathematical Delusion
    gpt_response_six = connect_gpt(
        engine="gpt-3.5-turbo",
        prompt=combined_six,
        max_tokens=512,
        temperature=0.0,
        stop=["--", "\n\n", ";", "#"],
        is_original=True
    )
    # Add categories to the responses
    gpt_response_one = f"Schema-Based Schema Contradiction: {gpt_response_one}"
    gpt_response_two = f"Schema-Based Attribute Overanalysis: {gpt_response_two}"
    gpt_response_three = f"Schema-Based Value Misrepresentation: {gpt_response_three}"
    gpt_response_four = f"Logic-Based Join Redundancy: {gpt_response_four}"
    gpt_response_five = f"Logic-Based Clause Abuse: {gpt_response_five}"
    gpt_response_six = f"Logic-Based Mathematical Delusion: {gpt_response_six}"

    # Combine all prompts and responses into a single string
    combined_error = f"""
        \nHere are some examples of Hallucinations to strictly avoid in your SQL generation: 
        {gpt_response_one}, 
        {gpt_response_two}, 
        {gpt_response_three}, 
        {gpt_response_four}, 
        {gpt_response_five}, 
        {gpt_response_six}
        
        \nUnderstanding this schema and knowledge: {knowledge if knowledge else ""}, and using valid {sql_dialect}, answer this question: {question}.

        \nIn your response, you do not need to mention your intermediate steps. 
        Do not include any comments in your response.
        Do not need to start with the symbol ```
        You only need to return the correct {sql_dialect}
        start from SELECT and answer this question: {question}
    """

    print("Combined Error Prompt: ", combined_error)

    combined_prompts = "\n\n".join([
        schema_prompt, combined_error
    ])
    return combined_prompts 