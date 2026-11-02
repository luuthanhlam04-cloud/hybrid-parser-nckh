import pandas as pd
from scipy import stats

def run_test():
    try:
        # Đọc dữ liệu
        df_vec = pd.read_csv('final_benchmark_results_VECTOR.csv')
        df_hyb = pd.read_csv('final_benchmark_results_HYBRID.csv')

        # Hợp nhất theo question_id để đảm bảo thứ tự khớp tuyệt đối
        merged = pd.merge(df_vec, df_hyb, on='question_id', suffixes=('_vec', '_hyb'))
        
        metrics = ['mrr_at_5', 'recall_at_5', 'faithfulness']
        
        print("=== KẾT QUẢ KIỂM ĐỊNH T-TEST TỪNG CẶP (PAIRED T-TEST) ===")
        print(f"Tổng số mẫu n = {len(merged)}\n")
        
        for m in metrics:
            col_vec = f'{m}_vec'
            col_hyb = f'{m}_hyb'
            
            # Lọc bỏ NaN nếu có
            valid = merged.dropna(subset=[col_vec, col_hyb])
            vec_vals = valid[col_vec]
            hyb_vals = valid[col_hyb]
            
            # Tính Paired T-test
            t_stat, p_val = stats.ttest_rel(vec_vals, hyb_vals)
            
            # Tính Wilcoxon Signed-Rank Test (Robust hơn nếu dữ liệu không phân phối chuẩn)
            w_stat, p_val_w = stats.wilcoxon(vec_vals, hyb_vals, zero_method='zsplit')
            
            print(f"--- CHỈ SỐ: {m.upper()} ---")
            print(f"Trung bình Vector: {vec_vals.mean():.4f}")
            print(f"Trung bình Hybrid: {hyb_vals.mean():.4f}")
            print(f"Chênh lệch (Hybrid - Vector): {hyb_vals.mean() - vec_vals.mean():.4f}")
            print(f"Paired t-test: t-statistic = {t_stat:.4f}, p-value = {p_val:.4e}")
            print(f"Wilcoxon test: w-statistic = {w_stat:.4f}, p-value = {p_val_w:.4e}")
            
            if p_val < 0.05:
                print(f"-> KẾT LUẬN: Khác biệt CÓ ý nghĩa thống kê (p < 0.05)")
            else:
                print(f"-> KẾT LUẬN: Khác biệt KHÔNG CÓ ý nghĩa thống kê (p >= 0.05)")
            print("\n")
            
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    run_test()
