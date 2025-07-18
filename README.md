# BIRD-mini Progressive Drill-Down

## Prompts:

**(1)**

```
**Using valid {sql_dialect} and understanding External Knowledge**

**External Knowledge: {knowledge}**

**{base_prompt}{knowledge_text}, answer the following questions for the tables provided above. Generate the {sql_dialect} for the above question after thinking step by step:**

**In your response, you do not need to mention your intermediate steps.**

**Do not include any comments in your response.**

**Do not need to start with the symbol ```**

**You only need to return the result {sql_dialect} SQL code**

**start from SELECT**
```

## [NOT USING Chat History Attention]

| Model:        | Experiment # | Prompt Used | Simple EX | Moderate EX | Challenging EX | Total EX |
|---------------|--------------|-------------|-----------|-------------|----------------|----------|
| GPT-4-Turbo   | exp_1        | 1           | 56.76     | 29.60       | 13.73          | 34.40    |

## [USING Chat History Attention]

| Model:     | Experiment # | Prompt Used | Simple EX | Moderate EX | Challenging EX | Total EX |
|------------|--------------|-------------|-----------|-------------|----------------|----------|
| GPT-4-Turbo | exp_2       | 1           | 57.43     | 34.00       | 14.71          | 37.00    |
| GPT-3.5-Turbo | exp_14    | 1           | 50.00     | 25.20       | 10.78          | 29.60    |


## Text-To-SQL Benchmarks

- BIRD-mini

## Benchmarking LLM Hallucinations in Text-to-SQL through Progressive Query Path Analysis

- A paper that presents a novel methodology for identifying and characterizing hallucinations in Large Language Models (LLMs) performing text-to-SQL tasks by leveraging progressive query decomposition.

- Instead of evaluating model performance solely on complete complex queries, our approach systematically breaks down SQL queries into progressively complex partial queries, creating checkpoints to pinpoint exactly where and why hallucinations occur without requiring additional annotations.

- Using the BIRD and Spider dataset, we implement a structured decomposition framework that isolates specific failure points along the progressive query path.

- Our experiments with GPT-3.5-Turbo, GPT-4-Turbo, Gemma, etc. reveal distinctive patterns of model hallucinations that would otherwise remain hidden in current end-to-end evaluation approaches.

- By analyzing points where the model fails along the progressive path, we provide insights into underlying model limitations and what aspects of SQL structure present particular challenges for the LLM.

- This methodology uniquely leverages the structured nature of SQL to create a diagnostic framework that reveals fundamental aspects of how LLMs process and generate structured database queries from Natural Language.

- Hopefully our findings could suggest that progressive query path analysis represents a valuable diagnostic tool for understanding model behavior in text-to-SQL tasks, with implications for targeted improvement strategies in model development, retraining, and prompting techniques

