# BIRD-mini Drill-Down Analysis

![bird progressive drill down](materials/pipe.png?raw=true)

## Introduction
Despite impressive benchmark scores, Large Language Models (LLMs) can still produce flawed and incorrect responses
for Text-to-SQL tasks. While prior work has decomposed complex SQL queries in an attempt to improve LLM benchmark performance, none have systematically analyzed hallu-
cination propagation patterns within these decomposed structures. We present a drill-down evaluation framework that decomposes complex SQL queries and questions from the
BIRD-mini dataset (Li et al. 2023), allowing for a fine-grained analysis of hallucination propagation. Through our analysis, we report three key findings: (1) Recurrent Hallu-
cinations: Many hallucinations persistently propagate from early, structurally simple sub-queries through to final steps, indicating systematic misalignment. (2) Final-Step Emergence: Fewer, but specific hallucination types emerge in the final step, suggesting a distinct failure mode tied to query
complexity. (3) History Amplifies Recurrence: While contextual information between sub-queries can improve overall accuracy and reduce the frequency of emergent hallucinations, it consequently increases the recurrence of early-stage hallucinations. This framework establishes a methodology to better understand LLM weaknesses and failure modes for Text-to-SQL systems.

## Methodology

### Progressive Sub-Query and Sub-Question Generation
We expand the original BIRD-mini dataset by:
1. **Decomposing the original queries** by their SQL Keywords: `SELECT --> WHERE --> AND --> AND ...`
2. **Generating Sub-Questions** for each sub-query by prompting an LLM to reword the original question based on what was removed from the partial query (Prompt 1).
    - GPT-4-Turbo
    - Claude-3.5-Sonnet

    ```
    cd llm/data/
    python partial_queries.py --engine gpt-4-turbo
    python partial_queries.py --engine claude-3-5-sonnet-latest
    ```
    Example Output:
    ```
    mini_dev_postgresql_drill_down_gpt.json
    mini_dev_postgresql_drill_down_claude.json
    ```

3. **Cross Validate (Filter)** sub-question from both models using `CosineSimilarity(GPT-4-Turbo, Claude-3.5-Sonnet) >= 0.65`, indicating strong agreement between the model's generated outputs.
    ```
    python compare_questions.py --file1 mini_dev_postgresql_drill_down_gpt.json
                                --file2 mini_dev_postgresql_drill_down_claude.json
                                --threshold 0.65
    ```

### Drill-Down Analysis
We have effectively expanded the original BIRD-mini 500 to **1021 question/query** pairs, additionally, created a progressive path that we can test where errors/hallucinations manifest.

1. We **evaluate six LLMs** on this new BIRD-mini drill-down dataset (GPT-4-Turbo, GPT-4.0o, GPT-4.0o-mini, GPT-4.1-mini, Claude-3.5-Sonnet, Claude-3.7-Sonnet)

    You will need to configure the engine in the run_gpt.sh or run_claude.sh file (i.e. `engine='gpt-4-turbo, claude-3-5-sonnet-latest'`)
    Additionally, you will need to set the path to your BIRD-mini drill-down dataset generated in the last section (i.e `eval_path='./data/mini_dev_postgresql_drill_down_claude.json'`)
    
    ```
    cd llm
    sh ./run/run_gpt.sh
    sh ./run/run_claude.sh
    ```
    
    Example Output:
    `llm/exp_result/exp_progressive_3_5_claude/predict_mini_dev_claude-3-5-sonnet-latest_cot_PostgreSQL.json`
    
    These outputs need to be cleaned since the outputs include deliminators for the bird database categories (i.e. `t----- bird -----\tdebit_card_specializing",`)
    Adjust the input and output file names at the bottom of the file 
    ```
    input_file = "predict_mini_dev_claude-3-5-sonnet-latest_cot_PostgreSQL.json"  # Replace with your input JSON file
    output_file = "predict_mini_dev_claude-3-5-sonnet-latest_cot_PostgreSQL_cleaned_queries.json"
    ```
    
    ```
    cd llm/data/
    python fix_data.py
    ```

2. We **annotate hallucinations** that are identified in the drill-down evaluation results
We evaluate all six models performance and hallucination patterns via two Jupyter notebooks:

    This first notebook allows you to pass in your cleaned results from the drill-down (i.e. `predict_mini_dev_claude-3-5-sonnet-latest_cot_PostgreSQL_cleaned_queries.json`) and for all of the queries that fail Execution Accuracy (EX) will be annotated with the hallucination taxonomy adopted from "Before Generation, Align it! A Novel and Effective Strategy for Mitigating Hallucinations in Text-to-SQL Generation" (Qu et al. 2024)
    
    `notebooks/Eval.ipynb`
    
    After annotating the results with the identified hallucination categories this second notebook plots hallucination patterns and results based on hallucination types:
    - P(Hallucination in Final Step | Hallucination Occured Earlier in Drill-Down)
    - P(Hallucination in Final Step | Hallucination Did NOT Occur Earlier in Drill-Down)
    
    `notebooks/Figures.ipynb`

## Results
![graph 1 probability of emergent hallucination in final step](materials/g1.png?raw=true)
![graph 2 probability of recurrent hallucination in final step](materials/g2.png?raw=true)
![graph 3 probability of emergent hallucination in final step with added LLM history context](materials/g3.png?raw=true)
![graph 3 probability of recurrent hallucination in final step with added LLM history context](materials/g4.png?raw=true)

## Prompts
**Prompt 1: Generating Sub-Questions**
```
Given the original question: {original question}

Generate a new natural language question that maintains the same structure and semantics but aligns with the following partial SQL query: {partial sql}

You are progressively generating questions that build on themselves from these provided partial queries. Do not include any information in your generated question that is not directly included in the partial query. The original question is the final query and should be used as reference to build out these progressive questions.

Requirements:
- The generated question must correspond exactly to what this partial SQL retrieves
- Maintain the same domain context and terminology as the original question
- The question should be answerable using only this partial SQL query
- This should be a logical step toward answering the original complex question

Generate only the natural language question.
```

**Prompt 2: Text-to-SQL Task**

```
Using valid {sql_dialect} and understanding External Knowledge

External Knowledge: {knowledge}

{base_prompt}{knowledge_text}, answer the following questions for the tables provided above. Generate the {sql_dialect} for the above question after thinking step by step:

In your response, you do not need to mention your intermediate steps.

Do not include any comments in your response.

Do not need to start with the symbol ```

You only need to return the result {sql_dialect} SQL code

start from SELECT
```

## Citation:

```
@article{li2024can,
  title={Can llm already serve as a database interface? a big bench for large-scale database grounded text-to-sqls},
  author={Li, Jinyang and Hui, Binyuan and Qu, Ge and Yang, Jiaxi and Li, Binhua and Li, Bowen and Wang, Bailin and Qin, Bowen and Geng, Ruiying and Huo, Nan and others},
  journal={Advances in Neural Information Processing Systems},
  volume={36},
  year={2024}
}

@article{Qu2024BeforeGAA,
  title={Before Generation, Align it! A Novel and Effective Strategy for Mitigating Hallucinations in Text-to-SQL Generation},
  author={Ge Qu and Jinyang Li and Bowen Li and Bowen Qin and Nan Huo and Chenhao Ma and Reynold Cheng},
  journal={ArXiv},
  year={2024},
  volume={abs/2405.15307},
  url={https://api.semanticscholar.org/CorpusId:270045343}
}
@article{li2023bird,
  title     = {BIRD: BIg Bench for LaRge-scale Database Grounded Text-to-SQL Evaluation},
  author    = {Li, Jinyang and Hui, Binyuan and Qu, Ge and Yang, Jiaxi and Li, Binhua and Li, Bowen and Wang, Bailin and Qin, Bowen and Cao, Rongyu and Geng, Ruiying and Huo, Nan and Zhou, Xuanhe and Ma, Chenhao and Li, Guoliang and Chang, Kevin C. C. and Huang, Fei and Cheng, Reynold and Li, Yongbin},
  journal   = {arXiv preprint arXiv:2305.03111},
  year      = {2023},
  url       = {https://arxiv.org/abs/2305.03111}
}
```
