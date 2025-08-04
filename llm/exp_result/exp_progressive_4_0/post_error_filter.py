import json
import os

post_error_filter = {}

with open("/Users/hmmoore/Desktop/mini_dev/llm/exp_result/exp_progressive_4_0/predict_mini_dev_gpt-4-turbo_cot_PostgreSQL_cleaned_queries_error_filter.json", 'r') as f:
    data = json.load(f)

i = 0

for d in data:
    sql = data[d]["corrected"]

    post_error_filter[str(i)] = sql

    i += 1


# Save post error filter queries to a JSON file
output_file = "/Users/hmmoore/Desktop/mini_dev/llm/exp_result/exp_progressive_4_0/post_error_filter.json"
with open(output_file, 'w') as out_file:
    json.dump(post_error_filter, out_file, indent=4)


# with open("/Users/hmmoore/Desktop/mini_dev/llm/exp_result/exp_progressive_4_0/predict_mini_dev_gpt-4-turbo_cot_PostgreSQL_cleaned_queries_error_filter.json", 'r') as f:
#     data = json.load(f)


# with open("/Users/hmmoore/Desktop/mini_dev/llm/exp_result/exp_progressive_4_0/predict_mini_dev_gpt-4-turbo_cot_PostgreSQL_cleaned_queries.json", 'r') as f:
#     data_2 = json.load(f)

# i = 0

# for d in data:
#     if data[d]["original"] == data_2[str(i)]:
#         print("Match found for index:", i)
#     i += 1

    





# # for d in data:
# #     data[d]["original"]
