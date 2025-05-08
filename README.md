This dataset results from community feedback, leading to the compilation
of **500 high-quality text2sql pairs** derived from 11 distinct
databases in a development environment.

Prompts:

**(1)**

> \`\`\`
>
> **Using valid {sql_dialect} and understanding External Knowledge**
>
> **External Knowledge: {knowledge}**
>
> **{base_prompt}{knowledge_text}, answer the following questions for
> the tables provided above. Generate the {sql_dialect} for the above
> question after thinking step by step:**
>
> **In your response, you do not need to mention your intermediate
> steps.**
>
> **Do not include any comments in your response.**
>
> **Do not need to start with the symbol \`\`\`**
>
> **You only need to return the result {sql_dialect} SQL code**
>
> **start from SELECT**
>
> **\`\`\`**

**(4)**

> \`\`\`
>
> **INSTRUCTIONS FOR SQL GENERATION:**
>
> **\*\*Using valid {sql_dialect} syntax\*\***
>
> **\*\*External Knowledge: {knowledge}\*\***
>
> **\*\*{base_prompt}{knowledge_text}\*\***
>
> **For the tables provided above, generate {sql_dialect} code for each
> question.**
>
> **CRITICAL INSTRUCTIONS:**
>
> **- ATTENTION: Each question builds directly on previous ones**
>
> **- REMEMBER previous questions and your successful solutions**
>
> **- APPLY knowledge gained from earlier responses to solve new
> questions**
>
> **- MAINTAIN context across the entire conversation**
>
> **- TRACK the logical progression of the drill-down sequence**
>
> **OUTPUT REQUIREMENTS:**
>
> **- Return ONLY the SQL code**
>
> **- Start directly with SELECT**
>
> **- No explanations, comments, or markdown formatting**
>
> **- No prefixes or additional text**
>
> **This is a progressive drill-down exercise. Your ability to remember
> and build upon previous answers is essential for success.**
>
> **Start with SELECT for each response.**
>
> **\`\`\`**

**[NOT USING Chat History Attention]{.underline}**

  --------------------------------------------------------------------------------
  Model:        Experiment   Prompt   Simple   Moderate   Challenging   Total EX
                \#           Used     EX       EX         EX            
  ------------- ------------ -------- -------- ---------- ------------- ----------
  GPT-4-Turbo   exp_1        1        56.76    29.60      13.73         34.40

  --------------------------------------------------------------------------------

**[USING Chat History Attention]{.underline}**

**Performance Change when using Partial Queries:**

**Simple: -2.02, Moderate: +0.40, Challenging: +2.94, Total: +0.20**

+------------+-------+-------+-------+---------+---------+---------+
| Model:     | Exper | P     | S     | M       | Chal    | Total   |
|            | iment | rompt | imple | oderate | lenging | EX      |
|            | \#    | Used  | EX    | EX      | EX      |         |
+============+=======+=======+=======+=========+=========+=========+
| G          | exp_2 | 1     | 57.43 | 34.00   | 14.71   | 37.00   |
| PT-4-Turbo |       |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+
| G          | e     | 1     | 55.41 | 34.40   | 17.65   | 37.20   |
| PT-4-Turbo | xp_12 |       |       |         |         |         |
|            |       |       |       |         |         |         |
| (Partial   |       |       |       |         |         |         |
| Queries)   |       |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+

**Performance Change when using Partial Queries:**

**Simple: +4.05, Moderate: +3.60, Challenging: +4.91, Total: +4.00**

+------------+-------+-------+-------+---------+---------+---------+
| Model:     | Exper | P     | S     | M       | Chal    | Total   |
|            | iment | rompt | imple | oderate | lenging | EX      |
|            | \#    | Used  | EX    | EX      | EX      |         |
+============+=======+=======+=======+=========+=========+=========+
| GPT        | e     | 1     | 50.00 | 25.20   | 10.78   | 29.60   |
| -3.5-Turbo | xp_14 |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+
| GPT        | e     | 1     | 54.05 | 28.80   | 15.69   | 33.60   |
| -3.5-Turbo | xp_16 |       |       |         |         |         |
|            |       |       |       |         |         |         |
| (Partial   |       |       |       |         |         |         |
| Queries)   |       |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+

**Performance Change when using Partial Queries:**

**Simple: -2.71, Moderate: +4.80, Challenging: +3.92, Total: +2.40**

+------------+-------+-------+-------+---------+---------+---------+
| Model:     | Exper | P     | S     | M       | Chal    | Total   |
|            | iment | rompt | imple | oderate | lenging | EX      |
|            | \#    | Used  | EX    | EX      | EX      |         |
+============+=======+=======+=======+=========+=========+=========+
| G          | e     | 4     | 56.76 | 32.00   | 15.69   | 36.00   |
| PT-4-Turbo | xp_11 |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+
| G          | e     | 4     | 54.05 | 36.80   | 19.61   | 38.40   |
| PT-4-Turbo | xp_10 |       |       |         |         |         |
|            |       |       |       |         |         |         |
| (Partial   |       |       |       |         |         |         |
| Queries)   |       |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+

**Performance Change when using Partial Queries:**

**Simple: -0.68, Moderate: +0.40, Challenging: +3.93, Total: +0.80**

+------------+-------+-------+-------+---------+---------+---------+
| Model:     | Exper | P     | S     | M       | Chal    | Total   |
|            | iment | rompt | imple | oderate | lenging | EX      |
|            | \#    | Used  | EX    | EX      | EX      |         |
+============+=======+=======+=======+=========+=========+=========+
| GPT        | e     | 4     | 50.68 | 25.60   | 10.78   | 30.00   |
| -3.5-Turbo | xp_15 |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+
| GPT        | e     | 4     | 50.00 | 26.00   | 14.71   | 30.80   |
| -3.5-Turbo | xp_13 |       |       |         |         |         |
|            |       |       |       |         |         |         |
| (Partial   |       |       |       |         |         |         |
| Queries)   |       |       |       |         |         |         |
+------------+-------+-------+-------+---------+---------+---------+

What Metrics are Researchers using for Hallucinations in General?

-   **BLEU Score (Bilingual Evaluation Understudy)**

    -   Measures n-gram overlap between generated text and a reference
        > (often used for translation, but applied to hallucination
        > detection by comparing prompt, context, and output)

    -   [[https://huggingface.co/spaces/evaluate-metric/bleu]{.underline}](https://huggingface.co/spaces/evaluate-metric/bleu)

-   **ROUGE Score**

    -   Evaluates overlap of n-grams, word sequences, and word pairs
        > between generated and reference texts. Common in summarization
        > and QA hallucination detection.

    -   [[https://medium.com/nlplanet/two-minutes-nlp-learn-the-rouge-metric-by-examples-f179cc285499]{.underline}](https://medium.com/nlplanet/two-minutes-nlp-learn-the-rouge-metric-by-examples-f179cc285499)

-   **[LLM-as-a-Judge / HallucinationMetric]{.mark}**

    -   Uses another LLM to compare the generated output to the ground
        > truth or context and assign a hallucination score.

    -   [[https://www.evidentlyai.com/llm-guide/llm-as-a-judge]{.underline}](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)

-   **Faithfulness / Factualness Metrics**

    -   Measures how well the generated output adheres to the provided
        > context or source documents (especially in Retrieval-Augmented
        > Generation systems).

    -   [[https://arxiv.org/html/2504.14891v1]{.underline}](https://arxiv.org/html/2504.14891v1)

-   **[Uncertainty-Based Metrics]{.mark}**

    -   Uses model uncertainty (e.g., entropy, variance of predictions)
        > as a feature for binary classification of hallucinated vs.
        > accurate content.

-   **Hidden State and Attention Map Analysis**

    -   Analyzes internal model activations, attention kernel maps, and
        > output prediction probabilities to detect hallucinations, both
        > in white-box (access to model internals) and black-box
        > settings.

    -   

-   **FEWL (Factualness Evaluations via Weighting LLMs)**

    -   Leverages answers from multiple reference LLMs, weighting them
        > by their estimated expertise when gold-standard answers are
        > unavailable. Designed for scenarios lacking human-annotated
        > ground truth.

    -   [[https://arxiv.org/html/2402.10412v1]{.underline}](https://arxiv.org/html/2402.10412v1)

-   **[Self-Consistency and Self-Check Methods]{.mark}**

    -   Compares multiple outputs from the same or different models to
        > check for consistency; inconsistent outputs may indicate
        > hallucination.

-   **Benchmark-Based Human Evaluation**

    -   Uses datasets like HaluEval, TruthfulQA, and CHALE, where human
        > annotators label outputs as hallucinated or not, often used to
        > validate or calibrate automatic metrics.

What Metrics are Researchers using for Hallucination in Text-To-SQL?

-   **Execution Accuracy (EX)**

    -   Measures whether the generated SQL query executes successfully
        > and returns correct results against the target database. Used
        > as the primary metric in benchmarks like BIRD and Spider.

-   **Reward Based Valid Efficiency Score**

-   **Soft F1 Score**

-   **Schema Linking Accuracy**

    -   Evaluates precision/recall in mapping natural language queries
        > to correct database schema elements (tables, columns, values).

-   **Logical Synthesis Correctness**

    -   Assesses the accuracy of SQL logic, including JOIN operations,
        > clauses (GROUP BY, LIMIT), and mathematical functions.

-   **RAGAS Faithfulness**

    -   Scores how well claims in the SQL match the schema

Text-To-SQL Benchmarks

-   BIRD

-   Spider

**Benchmarking LLM Hallucinations in Text-to-SQL through Progressive
Query Path Analysis**

-   A paper that presents a novel methodology for identifying and
    > characterizing hallucinations in Large Language Models (LLMs)
    > performing text-to-SQL tasks by leveraging progressive query
    > decomposition.

-   Instead of evaluating model performance solely on complete complex
    > queries, our approach systematically breaks down SQL queries into
    > progressively complex partial queries, creating checkpoints to
    > pinpoint exactly where and why hallucinations occur without
    > requiring additional annotations.

-   Using the BIRD and Spider dataset, we implement a structured
    > decomposition framework that isolates specific failure points
    > along the progressive query path.

-   Our experiments with GPT-3.5-Turbo, GPT-4-Turbo, Gemma, etc. reveal
    > distinctive patterns of model hallucinations that would otherwise
    > remain hidden in current end-to-end evaluation approaches.

-   By analyzing points where the model fails along the progressive
    > path, we provide insights into underlying model limitations and
    > what aspects of SQL structure present particular challenges for
    > the LLM.

-   This methodology uniquely leverages the structured nature of SQL to
    > create a diagnostic framework that reveals fundamental aspects of
    > how LLMs process and generate structured database queries from
    > Natural Language.

-   Hopefully our findings could suggest that progressive query path
    > analysis represents a valuable diagnostic tool for understanding
    > model behavior in text-to-SQL tasks, with implications for
    > targeted improvement strategies in model development, retraining,
    > and prompting techniques

Next Steps:

-   Bucketing similar queries and seeing their difference in drill down

-   Sub-query arrangement differences

    -   More broadly

    -   Maybe not hallucinations but just patters in the results

-   Figure out which Hall metrics make most sense to incorporate

-   Look into other models besides GPT, maybe even bad performing

-   Deeper dive into reasoning models

-   HaluEval metrics

-   3 "Facts" about the query

    -   The correct SELECT on the right table

    -   The correct conditions on the table

    -   The correct output column the conditions are placed

```{=html}
<!-- -->
```
-   