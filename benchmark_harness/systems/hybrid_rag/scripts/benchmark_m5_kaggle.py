# %% [markdown]
# # Benchmark Hệ thống Semantic Router (Module 5)
# Bài toán Tối ưu Cost-Recall Curve.
# Script này được thiết kế để chạy trên Kaggle (GPU T4x2).

# %% [markdown]
# ## 1. Cài đặt và Import
# (Trên Kaggle, `sentence-transformers` thường có sẵn, nếu thiếu hãy uncomment)
# !pip install -q sentence-transformers plotly seaborn
# bitsandbytes cần cho INT8 quantization của Qwen3-Embed-8B
!pip install -q bitsandbytes

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

# Giảm phân mảnh CUDA memory — bắt buộc khai báo TRƯỚC khi load bất kỳ model nào
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"

# Cấu hình
DATA_PATH = "/kaggle/input/luat-dat-dai-golden-v2/full_golden_set_annotation_v2.csv" # Sửa tên folder nếu bạn đặt tên dataset khác trên Kaggle
THRESHOLD_SWEEP = np.arange(0.30, 1.01, 0.05) # 0.3 đến 1.0, step 0.05
W_VALUES = [0.7, 0.3] # Bỏ 0.5 vì trùng hoàn toàn với Average-Fusion

# Danh sách 10 Models — Phân theo 4 nhóm thực nghiệm
MODELS = {
    # Nhóm 1: Causal LLM as Embedder (phát kiến từ sự cố cấu hình lần benchmark trước)
    # SentenceTransformers tự động mean-pool hidden states của Causal LLM → cho kết quả bất ngờ
    "Qwen-0.5B (Causal)": "Qwen/Qwen2.5-0.5B",
    "Qwen-1.5B (Causal)": "Qwen/Qwen2.5-1.5B",
    "Qwen-3B (Causal)":   "Qwen/Qwen2.5-3B",

    # Nhóm 2: Qwen3-Embedding chính quy — thiết kế chuyên cho text embedding & ranking
    # Encode texts/anchors bằng model.encode() trực tiếp (không dùng prompt_name='query'
    # vì cả texts và anchors đều là passage, không phải user query)
    "Qwen3-Embed-0.6B": "Qwen/Qwen3-Embedding-0.6B",
    "Qwen3-Embed-4B":   "Qwen/Qwen3-Embedding-4B",
    "Qwen3-Embed-8B":   "Qwen/Qwen3-Embedding-8B",

    # Nhóm 3: Multilingual Baseline — mốc so sánh với cộng đồng quốc tế
    "BGE-M3":   "BAAI/bge-m3",
    "E5-Large": "intfloat/multilingual-e5-large",

    # Nhóm 4: Vietnamese-optimized — domain relevance
    # BKAI: fine-tuned 80% Legal Retrieval Zalo 2021 — domain gần nhất với dataset
    # AITeamVN: BGE-M3 fine-tuned tiếng Việt (1.1M triplets) — so sánh cặp BGE-M3 gốc vs Việt hóa
    # Lưu ý: AITeamVN dùng dot product làm similarity function.
    # Với normalized vectors: dot(a,b) ≡ cosine(a,b) → code chuẩn hoá L2 bên dưới vẫn đúng.
    "BKAI-VN":     "bkai-foundation-models/vietnamese-bi-encoder",
    "AITeamVN-V2": "AITeamVN/Vietnamese_Embedding_v2",
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
print(f"[0] Loaded:           {len(df)} rows")

# Bước 1: Loại nhãn 0.5 (borderline chưa chốt)
df = df[df['is_semantic_human'].isin(['0', '1', 0, 1])].copy()
df['is_semantic_human'] = df['is_semantic_human'].astype(int)
print(f"[1] After drop 0.5:   {len(df)} rows")

# Bước 2: Ép kiểu Text về string để tránh lỗi NaN
df['Text'] = df['Text'].fillna("").astype(str)

# Bước 3: Loại node tiêu đề (Text toàn chữ hoa — CHƯƠNG, MỤC, ...)
df = df[~df['Text'].str.isupper()].copy()
print(f"[2] After drop upper: {len(df)} rows")

# Bước 4: Loại node quá ngắn (rỗng hoặc chỉ có "...", do lỗi parse)
df = df[df['Text'].str.strip().str.len() > 5].copy()
print(f"[3] After drop short: {len(df)} rows")

# Bước 5: Chỉ giữ node Điều (Node_id chứa 'dieu')
df = df[df['Node_id'].fillna("").astype(str).str.contains('dieu')].copy()
print(f"[4] Final eval set:   {len(df)} rows (expected 193)")
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
# **Checkpoint Architecture**: Mỗi model save CSV ngay khi xong.
# Nếu session crash giữa chừng, kết quả các model trước vẫn còn nguyên.
# Khởi động lại chỉ cần chạy lại cell này — model nào đã có CSV sẽ bị skip tự động.

# %%
import os
import datetime

RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)

# Regex-Only Baseline — tính 1 lần, dùng xuyên suốt
regex_metrics = get_metrics(regex_scores, 0.5, true_labels)
print(f"Regex-Only Baseline: Cost={regex_metrics['Cost']}, "
      f"Recall={regex_metrics['Recall']:.3f}, "
      f"Precision={regex_metrics['Precision']:.3f}\n")

print("Bắt đầu Benchmark...")
print(f"Kết quả từng model lưu tại: {RESULT_DIR}/\n")

for model_name, hf_id in MODELS.items():
    # Tạo tên file an toàn từ model name
    safe_name = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    out_path = f"{RESULT_DIR}/{safe_name}.csv"

    # SKIP nếu đã chạy rồi — cho phép resume khi session crash
    if os.path.exists(out_path):
        print(f"[SKIP] {model_name} — đã có {out_path}")
        continue

    print(f"\n--- Đang xử lý: {model_name} ---")
    t_start = datetime.datetime.now()

    try:
        # Load model:
        # - Model ≤4B: FP16 (giảm VRAM 50% so với FP32)
        # - Model 8B: INT8 (giảm thêm 50% nữa so với FP16) vì T4 chỉ có 16GB
        #   8B × 2 bytes FP16 = 16GB = sát trần → không đủ chỗ cho activation
        #   8B × 1 byte  INT8 = 8GB  = còn ~8GB cho activation, batch
        hf_lower = hf_id.lower()
        is_8b = "8b" in hf_lower
        
        if is_8b:
            # INT8 quantization cho 8B — cần bitsandbytes: !pip install -q bitsandbytes
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(load_in_8bit=True)
            model = SentenceTransformer(
                hf_id,
                trust_remote_code=True,
                model_kwargs={"quantization_config": bnb_config}
            )
            batch_size = 4  # INT8 nhẹ hơn, có thể batch_size cao hơn
            print(f"  dtype=INT8 (quantized), batch_size={batch_size}")
        elif "4b" in hf_lower or "3b" in hf_lower:
            model = SentenceTransformer(
                hf_id,
                trust_remote_code=True,
                model_kwargs={"torch_dtype": torch.float16}
            )
            batch_size = 4
            print(f"  dtype=FP16, batch_size={batch_size}")
        else:
            model = SentenceTransformer(
                hf_id,
                trust_remote_code=True,
                model_kwargs={"torch_dtype": torch.float16}
            )
            batch_size = 16
            print(f"  dtype=FP16, batch_size={batch_size}")

        # Không dùng multi_process_pool — dễ deadlock trong Kaggle Notebook
        text_embeds   = model.encode(texts,   batch_size=batch_size, show_progress_bar=True)
        anchor_embeds = model.encode(ANCHORS, batch_size=batch_size, show_progress_bar=False)

        # Cast về float32 TRƯỚC khi normalize
        # Lý do: SentenceTransformer trả về FP16 array khi model load ở FP16/INT8.
        # np.linalg.norm trên FP16 dễ bị overflow → norm = inf → similarity = NaN
        # (Log Qwen-0.5B đã cho thấy: "RuntimeWarning: overflow encountered in reduce")
        text_embeds   = text_embeds.astype(np.float32)
        anchor_embeds = anchor_embeds.astype(np.float32)

        # Cosine Similarity (L2-normalize → dot product ≡ cosine)
        t_norm = text_embeds / np.linalg.norm(text_embeds, axis=1, keepdims=True)
        a_norm = anchor_embeds / np.linalg.norm(anchor_embeds, axis=1, keepdims=True)
        sim_matrix   = np.dot(t_norm, a_norm.T)  # (num_nodes, num_anchors)
        embed_scores = np.max(sim_matrix, axis=1)

        # Sanity check: phát hiện NaN/Inf ngay tại đây, không chờ tới lúc plot
        nan_count = np.isnan(embed_scores).sum()
        inf_count = np.isinf(embed_scores).sum()
        if nan_count > 0 or inf_count > 0:
            raise ValueError(f"embed_scores có {nan_count} NaN và {inf_count} Inf — "
                             f"kiểm tra lại model encode hoặc float32 cast.")
        print(f"  embed_scores: min={embed_scores.min():.4f}, max={embed_scores.max():.4f}, "
              f"mean={embed_scores.mean():.4f} — OK")

        # --- Tính 5 Chiến Lược Fusion ---
        model_results = []

        # 1. Embed-Only
        model_results.append(sweep_thresholds(embed_scores, model_name, "Embed-Only"))

        # 2. Average Fusion
        model_results.append(sweep_thresholds((regex_scores + embed_scores) / 2, model_name, "Average-Fusion"))

        # 3. Weighted Fusion
        for w in W_VALUES:
            w_scores = w * regex_scores + (1 - w) * embed_scores
            model_results.append(sweep_thresholds(w_scores, model_name, f"Weighted-Fusion (w={w})"))

        # 4. Max Fusion
        model_results.append(sweep_thresholds(np.maximum(regex_scores, embed_scores), model_name, "Max-Fusion"))

        # CHECKPOINT: Save ngay sau khi tính xong, trước khi giải phóng VRAM
        model_df = pd.concat(model_results, ignore_index=True)
        model_df.to_csv(out_path, index=False)

        elapsed = (datetime.datetime.now() - t_start).total_seconds()
        print(f"  ✓ Saved → {out_path}  ({elapsed:.0f}s)")

    except Exception as e:
        print(f"  ✗ Lỗi khi chạy {model_name}: {e}")
        import traceback; traceback.print_exc()

    finally:
        # Fix: dùng try/del trực tiếp thay vì loop string
        # (loop string bị lỗi Python scoping: `del var` xóa biến string 'var', không xóa biến 'model')
        try: del model
        except NameError: pass
        try: del text_embeds
        except NameError: pass
        try: del anchor_embeds
        except NameError: pass
        try: del t_norm
        except NameError: pass
        try: del a_norm
        except NameError: pass
        try: del sim_matrix
        except NameError: pass
        try: del embed_scores
        except NameError: pass
        gc.collect()
        torch.cuda.empty_cache()
        print(f"  [VRAM freed]")

# %% [markdown]
# ## 5. Merge — Gom kết quả từ tất cả các file CSV

# %%
csv_files = sorted([
    os.path.join(RESULT_DIR, f)
    for f in os.listdir(RESULT_DIR)
    if f.endswith(".csv")
])
print(f"Tìm thấy {len(csv_files)} file kết quả:")
for f in csv_files: print(f"  {f}")

if not csv_files:
    raise RuntimeError("Không có file CSV nào trong thư mục results/. Chạy lại Cell 4 trước.")

master_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
master_df.to_csv("benchmark_full_results.csv", index=False)
print(f"\nMerge xong: {len(master_df)} rows → benchmark_full_results.csv")
print(f"Models có trong kết quả: {master_df['Model'].nunique()} / {len(MODELS)}")
print(master_df.groupby('Model')['Strategy'].nunique().to_string())


# %% [markdown]
# ## 6. Vẽ Đồ Thị Plotly (Interactive HTML)
# Bạn có thể copy HTML này xem ở Local.

# %%
if not master_df.empty:
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
    
    # --- Figure 2: Ablation Study (Toàn bộ Models) ---
    model_names = list(MODELS.keys())
    import math
    cols = 3
    rows = math.ceil(len(model_names) / cols)
    
    fig2 = make_subplots(
        rows=rows, cols=cols, subplot_titles=model_names,
        shared_yaxes=True, horizontal_spacing=0.04, vertical_spacing=0.08
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
        
        fig2.update_xaxes(autorange="reversed", title_text="Cost" if row==rows else "", gridcolor='lightgrey', row=row, col=col)
        if col == 1:
            fig2.update_yaxes(title_text="Recall", tickformat=".0%", gridcolor='lightgrey', row=row, col=col)
            
    fig2.update_layout(
        title="Figure 2: Fusion Strategy Ablation Across All Models",
        height=1200, width=1500, # Tăng height để vẽ vừa 3 hàng (9 models)
        template="plotly_white", hovermode="x",
        plot_bgcolor='rgba(245, 247, 250, 1)'
    )
    
    fig2.write_html("Figure_2_Fusion_Ablation.html")
    print("Đã xuất Figure_2_Fusion_Ablation.html")

# %% [markdown]
# ## 7. Bảng Phân Tích Điểm Hoạt Động (Operating Point)

# %%
if not master_df.empty:
    target_recalls = [0.80, 0.85, 0.90]
    op_results = []
    
    for r_target in target_recalls:
        # Lấy những điểm đạt recall mục tiêu
        valid = max_fusion_df[max_fusion_df['Recall'] >= r_target]
        if not valid.empty:
            # Tie-break: min Cost → max Recall → max Precision (đảm bảo kết quả xác định)
            valid_sorted = valid.sort_values(
                by=['Cost', 'Recall', 'Precision'],
                ascending=[True, False, False]
            )
            best = valid_sorted.iloc[0]
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
