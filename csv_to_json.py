import csv
import json

# 定义 CSV 文件路径和要保存的 JSON 文件路径
csv_file = 'data/KeyRatiosv2.csv'
json_file = 'data/KeyRatiosv2_all.json'

# 读取 CSV 文件
with open(csv_file, 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = [row for row in reader]

# 将数据写入 JSON 文件
with open(json_file, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)