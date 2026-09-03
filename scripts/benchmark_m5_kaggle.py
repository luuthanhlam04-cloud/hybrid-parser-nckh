# %% [markdown]
# # Benchmark Hệ thống Semantic Router (Module 5)
# Bài toán Tối ưu Cost-Recall Curve.
# Script này được thiết kế để chạy trên Kaggle (GPU T4x2).

# %% [markdown]
# ## 1. Cài đặt và Import
# (Trên Kaggle, `sentence-transformers` thường có sẵn, nếu thiếu hãy uncomment)
# !pip install -q sentence-transformers plotly seaborn

# %%
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import gc
import torch
import os

# Cấu hình
DATA_PATH = "/kaggle/input/luat-dat-dai-golden-v2/full_golden_set_annotation_v2.csv" # Sửa tên folder nếu bạn đặt tên dataset khác trên Kaggle
THRESHOLD_SWEEP = np.arange(0.30, 1.01, 0.05) # 0.3 đến 1.0, step 0.05
W_VALUES = [0.7, 0.3] # Bỏ 0.5 vì trùng hoàn toàn với Average-Fusion

# Danh sách 6 Models
MODELS = {
    "Qwen-0.5B": "Qwen/Qwen2.5-0.5B", # Dùng Qwen2.5 tạm do Qwen3 chưa release public
    "Qwen-1.5B": "Qwen/Qwen2.5-1.5B", 
    "Qwen-3B": "Qwen/Qwen2.5-3B",     
    "BGE-M3": "BAAI/bge-m3",
    "E5-Large": "intfloat/multilingual-e5-large",
    "Viet-BiEncoder": "bkai-foundation-models/vietnamese-bi-encoder"
}

# Anchors semantic
ANCHORS = [
    "trừ trường hợp", "ngoại lệ", "trừ khi", "ngoại trừ",
    "trong trường hợp", "điều kiện",
    "theo quy định tại", "căn cứ khoản", "căn cứ điều", "quy định tại"
]

# %% [markdown]
# ## 2. Nạp Dataset và Tiền xử lý (Input Preprocessing)

# %%
df = pd.read_csv(DATA_PATH)
print(f"Original shape: {df.shape}")

# Bước 1: Resolve/Exclude 0.5 (Loại bỏ các ca borderline chưa chốt)
df = df[df['is_semantic_human'].isin(['0', '1', 0, 1])].copy()
df['is_semantic_human'] = df['is_semantic_human'].astype(int)

# Bước 2: Remove Title Nodes (Lọc các node tiêu đề)
# - Đảm bảo cột Text là chuỗi để tránh lỗi NaN
df['Text'] = df['Text'].fillna("").astype(str)
# - Loại bỏ các node Text viết hoa toàn bộ (thường là tiêu đề CHƯƠNG, MỤC)
# - Loại bỏ các node quá ngắn (ví dụ chỉ chứa "..." do lỗi parse)
df = df[~df['Text'].str.isupper()].copy()
df = df[df['Text'].str.strip().str.len() > 5].copy()
# (Tùy chọn) Lọc chỉ giữ lại các node có chứa 'dieu' trong Node_id
df = df[df['Node_id'].fillna("").astype(str).str.contains('dieu')].copy()

print(f"Final Evaluation Set shape: {df.shape}")
print("Label distribution:", df['is_semantic_human'].value_counts().to_dict())

texts = df['Text'].tolist()
regex_scores = df['EXP-A(Regex)'].astype(float).values
true_labels = df['is_semantic_human'].values
TOTAL_NODES = len(texts)
TOTAL_POSITIVES = np.sum(true_labels)

# %% [markdown]
# ## 3. Hàm Tính Toán Confusion Matrix và Cost-Recall
# Dựa trên State Determinism Invariant

# %%
def get_metrics(score_array: np.ndarray, threshold: float, true_labels: np.ndarray) -> dict:
    """Tính các metric tại một threshold cụ thể."""
    preds = (score_array >= threshold).astype(int)
    
    tp = np.sum((preds == 1) & (true_labels == 1))
    fp = np.sum((preds == 1) & (true_labels == 0))
    tn = np.sum((preds == 0) & (true_labels == 0))
    fn = np.sum((preds == 0) & (true_labels == 1))
    
    cost = tp + fp # Candidate nodes
    recall = tp / TOTAL_POSITIVES if TOTAL_POSITIVES > 0 else 0
    precision = tp / cost if cost > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "Threshold": threshold,
        "Cost": cost,
        "Recall": recall,
        "Precision": precision,
        "F1": f1,
        "TP": tp, "FP": fp, "TN": tn, "FN": fn
    }

def sweep_thresholds(score_array: np.ndarray, model_name: str, strategy: str) -> pd.DataFrame:
    """Quét qua dải threshold và tính metric."""
    results = []
    for t in THRESHOLD_SWEEP:
        m = get_metrics(score_array, t, true_labels)
        m["Model"] = model_name
        m["Strategy"] = strategy
        results.append(m)
    return pd.DataFrame(results)

# %% [markdown]
# ## 4. Main Execution: Tính Embedding và Điểm Fusion

# %%
all_results_df = []

print("Bắt đầu Benchmark...")

for model_name, hf_id in MODELS.items():
    print(f"\n--- Đang xử lý: {model_name} ---")
    try:
        model = SentenceTransformer(hf_id, trust_remote_code=True)
        # Sử dụng multi-GPU nếu có (Kaggle T4x2)
        if torch.cuda.device_count() > 1:
            pool = model.start_multi_process_pool()
            text_embeds = model.encode_multi_process(texts, pool)
            anchor_embeds = model.encode_multi_process(ANCHORS, pool)
            model.stop_multi_process_pool(pool)
        else:
            text_embeds = model.encode(texts, show_progress_bar=True)
            anchor_embeds = model.encode(ANCHORS, show_progress_bar=False)
            
        # Cosine Similarity
        # Normalize vectors
        t_norm = text_embeds / np.linalg.norm(text_embeds, axis=1, keepdims=True)
        a_norm = anchor_embeds / np.linalg.norm(anchor_embeds, axis=1, keepdims=True)
        sim_matrix = np.dot(t_norm, a_norm.T) # shape: (num_nodes, num_anchors)
        
        # Điểm Embed-Only = max similarity với bất kỳ anchor nào
        embed_scores = np.max(sim_matrix, axis=1)
        
        # --- Các Chiến Lược Fusion ---
        
        # 1. Embed-Only
        df_embed = sweep_thresholds(embed_scores, model_name, "Embed-Only")
        all_results_df.append(df_embed)
        
        # 2. Average Fusion
        avg_scores = (regex_scores + embed_scores) / 2
        df_avg = sweep_thresholds(avg_scores, model_name, "Average-Fusion")
        all_results_df.append(df_avg)
        
        # 3. Weighted Fusion
        for w in W_VALUES:
            w_scores = w * regex_scores + (1 - w) * embed_scores
            df_w = sweep_thresholds(w_scores, model_name, f"Weighted-Fusion (w={w})")
            all_results_df.append(df_w)
            
        # 4. Max Fusion (Proposed)
        max_scores = np.maximum(regex_scores, embed_scores)
        df_max = sweep_thresholds(max_scores, model_name, "Max-Fusion")
        all_results_df.append(df_max)
        
        # Clear VRAM
        del model
        del text_embeds
        del anchor_embeds
        gc.collect()
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"Lỗi khi chạy {model_name}: {e}")

# Gom dữ liệu
if all_results_df:
    master_df = pd.concat(all_results_df, ignore_index=True)
    master_df.to_csv("benchmark_full_results.csv", index=False)
    print("\nĐã xuất kết quả thô ra benchmark_full_results.csv")
    
    # 5. Regex-Only (Rule baseline)
    # Có giá trị tĩnh (vì chỉ ∈ 0,1)
    regex_metrics = get_metrics(regex_scores, 0.5, true_labels) # Threshold 0.5 vì nhãn cứng
    print(f"\nRegex-Only Baseline: Cost={regex_metrics['Cost']}, Recall={regex_metrics['Recall']:.3f}, Precision={regex_metrics['Precision']:.3f}")
else:
    print("Không có kết quả nào. Có thể các model không tải được.")

# %% [markdown]
# ## 5. Vẽ Đồ Thị Plotly (Interactive HTML)
# Bạn có thể copy HTML này xem ở Local.

# %%
if all_results_df:
    # Cấu hình thẩm mỹ chung (Aesthetics)
    marker_style = dict(size=8, line=dict(width=1, color='white'))
    star_style = dict(size=14, symbol='star', color='black', line=dict(width=1, color='gold'))
    
    # Template tooltip siêu chi tiết và đẹp
    hovertemplate = (
        "<b>[%{fullData.name}]</b><br>" # Hiển thị rõ tên đường (Model/Strategy)
        "Threshold(s): %{customdata[0]}<br>"
        "Cost: %{x} nodes<br>"
        "Recall: %{y:.1%}<br>"
        "Precision: %{customdata[1]:.1%}<br>"
        "F1: %{customdata[2]:.3f}<br>"
        "TP: %{customdata[3]} | FP: %{customdata[4]} | TN: %{customdata[5]} | FN: %{customdata[6]}"
        "<extra></extra>" # Ẩn hộp phụ, tập trung vào hộp chính
    )

    # --- Figure 1: Core Experiment (So sánh các Model trên Max-Fusion) ---
    fig1 = go.Figure()
    max_fusion_df = master_df[master_df['Strategy'] == "Max-Fusion"].copy()
    
    for model_name in MODELS.keys():
        m_df = max_fusion_df[max_fusion_df['Model'] == model_name].copy()
        if m_df.empty: continue
        
        # Nhóm các điểm trùng tọa độ để hiện chung Threshold
        m_df = m_df.groupby(['Cost', 'Recall'], as_index=False).agg({
            'Threshold': lambda x: ', '.join([f"{t:.2f}" for t in sorted(x)]),
            'Precision': 'first', 'F1': 'first',
            'TP': 'first', 'FP': 'first', 'TN': 'first', 'FN': 'first'
        }).sort_values(by='Cost', ascending=False) # Xếp Cost giảm dần để vẽ line đúng chiều
        
        # Đóng gói dữ liệu phụ vào customdata (Object array để giữ đúng type)
        custom_data = np.empty((len(m_df), 7), dtype=object)
        custom_data[:, 0] = m_df['Threshold'].values
        custom_data[:, 1] = m_df['Precision'].values
        custom_data[:, 2] = m_df['F1'].values
        custom_data[:, 3] = m_df['TP'].values
        custom_data[:, 4] = m_df['FP'].values
        custom_data[:, 5] = m_df['TN'].values
        custom_data[:, 6] = m_df['FN'].values
        
        fig1.add_trace(go.Scatter(
            x=m_df['Cost'], y=m_df['Recall'],
            mode='lines+markers', name=model_name,
            marker=marker_style, line=dict(width=3),
            customdata=custom_data, hovertemplate=hovertemplate
        ))
        
    # Thêm điểm Regex-Only
    regex_custom = np.array([["Fixed (0.5)", regex_metrics['Precision'], regex_metrics['F1'], regex_metrics['TP'], regex_metrics['FP'], regex_metrics['TN'], regex_metrics['FN']]], dtype=object)
    fig1.add_trace(go.Scatter(
        x=[regex_metrics["Cost"]], y=[regex_metrics["Recall"]],
        mode='markers', marker=star_style, name='Regex-Only Baseline',
        customdata=regex_custom, hovertemplate=hovertemplate
    ))

    fig1.update_layout(
        title="Figure 1: Cost-Recall Frontier of Different Embedding Models (Max-Fusion)",
        xaxis_title="Cost (Number of Candidate Nodes thrown to LLM)",
        yaxis_title="Recall (Semantic Nodes retained)",
        yaxis=dict(tickformat=".0%", gridcolor='lightgrey'),
        xaxis=dict(autorange="reversed", gridcolor='lightgrey'),
        hovermode="x", # HIỂN THỊ TOOLTIP CHO TẤT CẢ CÁC ĐƯỜNG TRÙNG NHAU TẠI CÙNG TRỤC X
        template="plotly_white",
        plot_bgcolor='rgba(245, 247, 250, 1)', # Nền hơi xám xanh nhạt cho premium
        height=700
    )
    
    fig1.write_html("Figure_1_Model_Comparison.html")
    print("Đã xuất Figure_1_Model_Comparison.html")
    
    # --- Figure 2: Ablation Study (Tất cả 6 Models) ---
    model_names = list(MODELS.keys())
    fig2 = make_subplots(
        rows=2, cols=3, subplot_titles=model_names,
        shared_yaxes=True, horizontal_spacing=0.04, vertical_spacing=0.1
    )
    
    strategies = master_df['Strategy'].unique()
    colors = sns.color_palette("Set2", len(strategies)).as_hex()
    
    for i, model_name in enumerate(model_names):
        row = (i // 3) + 1
        col = (i % 3) + 1
        m_df = master_df[master_df['Model'] == model_name]
        
        for j, strategy in enumerate(strategies):
            s_df = m_df[m_df['Strategy'] == strategy].copy()
            if s_df.empty: continue
            
            # Nhóm các điểm trùng
            s_df = s_df.groupby(['Cost', 'Recall'], as_index=False).agg({
                'Threshold': lambda x: ', '.join([f"{t:.2f}" for t in sorted(x)]),
                'Precision': 'first', 'F1': 'first',
                'TP': 'first', 'FP': 'first', 'TN': 'first', 'FN': 'first'
            }).sort_values(by='Cost', ascending=False)
            
            custom_data = np.empty((len(s_df), 7), dtype=object)
            custom_data[:, 0] = s_df['Threshold'].values
            custom_data[:, 1] = s_df['Precision'].values
            custom_data[:, 2] = s_df['F1'].values
            custom_data[:, 3] = s_df['TP'].values
            custom_data[:, 4] = s_df['FP'].values
            custom_data[:, 5] = s_df['TN'].values
            custom_data[:, 6] = s_df['FN'].values
            
            fig2.add_trace(go.Scatter(
                x=s_df['Cost'], y=s_df['Recall'],
                mode='lines+markers', name=strategy,
                marker=marker_style, line=dict(color=colors[j], width=2),
                customdata=custom_data, hovertemplate=hovertemplate,
                showlegend=True if i == 0 else False
            ), row=row, col=col)
            
        # Thêm điểm Regex-Only
        fig2.add_trace(go.Scatter(
            x=[regex_metrics["Cost"]], y=[regex_metrics["Recall"]],
            mode='markers', marker=star_style, name='Regex-Only Baseline',
            customdata=regex_custom, hovertemplate=hovertemplate,
            showlegend=True if i == 0 else False
        ), row=row, col=col)
        
        fig2.update_xaxes(autorange="reversed", title_text="Cost" if row==2 else "", gridcolor='lightgrey', row=row, col=col)
        if col == 1:
            fig2.update_yaxes(title_text="Recall", tickformat=".0%", gridcolor='lightgrey', row=row, col=col)
            
    fig2.update_layout(
        title="Figure 2: Fusion Strategy Ablation Across All Models",
        height=800, width=1500,
        template="plotly_white", hovermode="x",
        plot_bgcolor='rgba(245, 247, 250, 1)'
    )
    
    fig2.write_html("Figure_2_Fusion_Ablation.html")
    print("Đã xuất Figure_2_Fusion_Ablation.html")

# %% [markdown]
# ## 6. Bảng Phân Tích Điểm Hoạt Động (Operating Point)

# %%
if all_results_df:
    target_recalls = [0.80, 0.85, 0.90]
    op_results = []
    
    for r_target in target_recalls:
        # Lấy những điểm đạt recall mục tiêu
        valid = max_fusion_df[max_fusion_df['Recall'] >= r_target]
        if not valid.empty:
            # Chọn cấu hình tiết kiệm Cost nhất
            best = valid.loc[valid['Cost'].idxmin()]
            op_results.append({
                "Target Recall": f"≥ {r_target*100}%",
                "Best Model": best['Model'],
                "Cost (Nodes)": best['Cost'],
                "Actual Recall": f"{best['Recall']:.1%}",
                "Precision": f"{best['Precision']:.1%}",
                "Threshold": best['Threshold'],
                "F1": round(best['F1'], 3)
            })
            
    op_df = pd.DataFrame(op_results)
    print("\n--- Bảng Phân Tích Operating Points ---")
    print(op_df.to_string(index=False))
