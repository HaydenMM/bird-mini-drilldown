## Appendix (A) Example

mini_dev/evaluation/path_eval_log_paper_path_halluc_4_0_o_mini_history.json

Input: mini_dev_postgresql.json

Snippet:

```
{
    "question_id": 39,
    "db_id": "california_schools",
    "question": "What is the average number of test takers from Fresno schools that opened between 1/1/1980 and 12/31/1980?",
    "evidence": "between 1/1/1980 and 12/31/1980 means the year = 1980",
    "SQL": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE TO_CHAR(CAST(T2.OpenDate AS TIMESTAMP), 'YYYY') = '1980' AND T2.County = 'Fresno'",
    "difficulty": "simple",
    "is_original": true
},
```

CMD: python partial_queries.py --engine gpt-4o

Output: mini_dev_postgresql_drill_down.json

Snippet:

```
{
    "question_id": 39,
    "db_id": "california_schools",
    "question": "What is the average number of test takers for schools based on the matching records between the SAT scores and school details tables?",
    "evidence": "between 1/1/1980 and 12/31/1980 means the year = 1980",
    "SQL": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode",
    "difficulty": "simple",
    "is_original": false
},
{
    "question_id": 39,
    "db_id": "california_schools",
    "question": "What is the average number of test takers from schools that opened in the year 1980?",
    "evidence": "between 1/1/1980 and 12/31/1980 means the year = 1980",
    "SQL": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE TO_CHAR(CAST(T2.OpenDate AS TIMESTAMP), 'YYYY') = '1980'",
    "difficulty": "simple",
    "is_original": false
},
{
    "question_id": 39,
    "db_id": "california_schools",
    "question": "What is the average number of test takers from Fresno schools that opened between 1/1/1980 and 12/31/1980?",
    "evidence": "between 1/1/1980 and 12/31/1980 means the year = 1980",
    "SQL": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE TO_CHAR(CAST(T2.OpenDate AS TIMESTAMP), 'YYYY') = '1980' AND T2.County = 'Fresno'",
    "difficulty": "simple",
    "is_original": true
},
```
Input: mini_dev_postgresql_drill_down.json

CMD: sh ./run/run_gpt.sh

Output: llm/exp_result/exp_progressive_4_0_o_history/predict_mini_dev_gpt_cot_PostgreSQL.json

Snippet:

```
{
    "question_id": null,
    "path": [
        {
            "question_id": 39,
            "db_id": "california_schools",
            "gt_query": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode",
            "predicted_query": "SELECT AVG(s.numtsttakr) AS average_test_takers FROM satscores s JOIN schools sc ON s.cds = sc.cdscode WHERE s.numtsttakr IS NOT NULL",
            "correct": 1,
            "error": null,
            "difficulty": "simple"
        },
        {
            "question_id": 39,
            "db_id": "california_schools",
            "gt_query": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE TO_CHAR(CAST(T2.OpenDate AS TIMESTAMP), 'YYYY') = '1980'",
            "predicted_query": "SELECT AVG(s.numtsttakr) AS average_test_takers FROM satscores s JOIN schools sc ON s.cds = sc.cdscode WHERE sc.opendate IS NOT NULL   AND EXTRACT(YEAR FROM sc.opendate) = 1980   AND s.numtsttakr IS NOT NULL",
            "correct": 1,
            "error": null,
            "difficulty": "simple"
        },
        {
            "question_id": 39,
            "db_id": "california_schools",
            "gt_query": "SELECT AVG(T1.NumTstTakr) FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode WHERE TO_CHAR(CAST(T2.OpenDate AS TIMESTAMP), 'YYYY') = '1980' AND T2.County = 'Fresno'",
            "predicted_query": "SELECT AVG(s.numtsttakr) AS average_test_takers FROM satscores s JOIN schools sc ON s.cds = sc.cdscode WHERE sc.city = 'Fresno'   AND sc.opendate IS NOT NULL   AND EXTRACT(YEAR FROM sc.opendate) = 1980   AND s.numtsttakr IS NOT NULL",
            "correct": 0,
            "error": null,
            "difficulty": "simple",
            "hallucination": [
                [
                    "Schema-Based: Schema Contradiction",
                    "Unknown table 'sc'",
                    "tsttakr) AS average_test_takers FROM satscores s JOIN schools sc ON s.cds = sc.cds"
                ],
                [
                    "Schema-Based: Attribute Overanalysis",
                    "Extra column 'city'",
                    "hools sc ON s.cds = sc.cdscode WHERE sc.city = 'Fresno'   AND sc.opendate IS NOT NUL"
                ],
                [
                    "Schema-Based: Value Misrepresentation",
                    "Missing cast for field 'opendate' (used in GT with cast)",
                    "scode WHERE sc.city = 'Fresno'   AND sc.opendate IS NOT NULL   AND EXTRACT(YEAR FROM sc."
                ],
                [
                    "Schema-Based: Value Misrepresentation",
                    "Value mismatch in WHERE clause: literal 'YYYY' differs from GT",
                    "YYYY"
                ],
                [
                    "Schema-Based: Value Misrepresentation",
                    "Value mismatch in WHERE clause: literal '1980' differs from GT",
                    "AND EXTRACT(YEAR FROM sc.opendate) = 1980   AND s.numtsttakr IS NOT NULL"
                ]
            ]
        }
    ]
 ```

