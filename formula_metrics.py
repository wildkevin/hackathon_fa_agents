import re
import os
import pandas as pd

# 创建 data 目录（如果不存在）
if not os.path.exists('data'):
    os.makedirs('data')

# 重新加载数据
data = pd.read_csv('data/KeyRatiosv2.csv')

# 定义一个函数来提取变量
def extract_variables(formula):
    # 使用空格分割字符串，并去除标点符号
    words = re.findall(r'[a-zA-Z_&]+(?:\s+[a-zA-Z0-9_&]+)*', formula)
    variables = [word.strip() for word in words if word.strip()]
    return variables

# 提取所有变量
all_variables = []
for formula in data['Formula']:
    all_variables.extend(extract_variables(formula))

# 转换为 DataFrame 并去除重复项
variables_df = pd.DataFrame({'Variable': all_variables}).drop_duplicates()

# 保存到 CSV 文件
csv_path = 'data/metrics.csv'
variables_df.to_csv(csv_path, index=False, header=False)

# 打印变量
print('提取到的变量：')
print(variables_df['Variable'].tolist())