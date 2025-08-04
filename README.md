# BIRD-mini Progressive Drill-Down

![bird progressive drill down](materials/pipe-3.png?raw=true)

## Prompts:

**Text-to-SQL Task**

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

**Generating Sub-Questions**
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

## Citation:

```
@article{li2024can,
  title={Can llm already serve as a database interface? a big bench for large-scale database grounded text-to-sqls},
  author={Li, Jinyang and Hui, Binyuan and Qu, Ge and Yang, Jiaxi and Li, Binhua and Li, Bowen and Wang, Bailin and Qin, Bowen and Geng, Ruiying and Huo, Nan and others},
  journal={Advances in Neural Information Processing Systems},
  volume={36},
  year={2024}
}
```
