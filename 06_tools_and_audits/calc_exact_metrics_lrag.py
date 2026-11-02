import pandas as pd
import json

def get_exact_metrics():
    df_lrag = pd.read_csv('backup_lightrag_512.csv')
    
    # Lọc bỏ các câu N/A, FAILED
    valid = df_lrag[df_lrag['faithfulness'].notnull()]
    
    cp = valid['context_precision'].mean()
    ca = valid['citation_accuracy'].mean()
    
    print(f"[LightRAG] Context Precision: {cp:.4f}")
    print(f"[LightRAG] Citation Accuracy: {ca:.4f}")

if __name__ == "__main__":
    get_exact_metrics()
