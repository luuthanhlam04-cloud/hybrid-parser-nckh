import pandas as pd
import json

def get_exact_metrics():
    df_vec = pd.read_csv('final_benchmark_results_VECTOR.csv')
    df_hyb = pd.read_csv('final_benchmark_results_HYBRID.csv')
    
    print("=== CHỈ SỐ CHÍNH XÁC TỪ CSV ===")
    
    # Tính trung bình Context Precision và Citation Accuracy
    for name, df in [("Vector", df_vec), ("Hybrid", df_hyb)]:
        cp = df['context_precision'].mean()
        ca = df['citation_accuracy'].mean()
        print(f"[{name}] Context Precision: {cp:.4f}")
        print(f"[{name}] Citation Accuracy: {ca:.4f}")

    print("\n=== TÌM CASE STUDY ĐIỂN HÌNH ===")
    # Tìm câu Hybrid thắng Vector ở MRR
    merged = pd.merge(df_vec, df_hyb, on='question_id', suffixes=('_vec', '_hyb'))
    hybrid_wins = merged[merged['mrr_at_5_hyb'] > merged['mrr_at_5_vec']].head(3)
    print("Các ID Hybrid thắng Vector (MRR):", hybrid_wins['question_id'].tolist())

    # Tìm câu bị lỗi Citation Hallucination (citation_accuracy = 0.0)
    vec_hallucination = df_vec[df_vec['citation_accuracy'] == 0.0].head(2)
    print("Các ID Vector bị lỗi Citation (0.0):", vec_hallucination['question_id'].tolist())

if __name__ == "__main__":
    get_exact_metrics()
