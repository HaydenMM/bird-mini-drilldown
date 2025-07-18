# BIRD-mini Progressive Drill-Down

![bird progressive drill down](materials/progressive-drill-down.png?raw=true)

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


