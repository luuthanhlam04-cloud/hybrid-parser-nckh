import pandas as pd
df = pd.read_csv('c:/Users/luuth/NCKH/full_golden_set_annotation_v2.csv')
df1 = df[df['is_semantic_human'].isin(['0', '1', 0, 1])].copy()
df1['Text'] = df1['Text'].fillna('').astype(str)
df2 = df1[~df1['Text'].str.isupper()].copy()
short = df2[df2['Text'].str.strip().str.len() <= 5]
print('--- CÁC NODE RÁC/QUÁ NGẮN (<= 5 KÝ TỰ) ---')
for idx, row in short.iterrows():
    print(f"Node: {row['Node_id']} | Text: '{row['Text']}'")

print('\n--- NODE 0.5 (CHƯA CHỐT) ---')
borderline = df[~df['is_semantic_human'].isin(['0', '1', 0, 1])]
for idx, row in borderline.iterrows():
    print(f"Node: {row['Node_id']} | Text: '{row['Text']}'")
