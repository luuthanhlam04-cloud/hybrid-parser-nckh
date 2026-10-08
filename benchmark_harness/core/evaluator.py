import os
from datetime import datetime
from core.dataset_loader import DatasetLoader
from core.cost_tracker import CostTracker
from core.checkpoint import CheckpointManager
from core.base_system import BaseRAGSystem
from metrics.tier1_retrieval import Tier1RetrievalMetrics
from metrics.tier2_5_correctness import Tier25Correctness
from metrics.tier4_legal_structure import LSVExtractor

class BenchmarkEvaluator:
    """
    Trái tim của hệ thống Benchmark Harness.
    Điều phối Dataset, Hệ thống RAG (Tay súng), và Metrics (Trọng tài).
    Áp dụng Option B: Per-Question Atomic Checkpoint.
    """
    def __init__(self, dataset_path: str, results_dir: str, ontology_path: str):
        self.loader = DatasetLoader(dataset_path)
        self.cost_tracker = CostTracker()
        self.results_dir = results_dir
        
        # Khởi tạo các trọng tài
        self.tier25 = Tier25Correctness(self.cost_tracker)
        self.tier4_lsv = LSVExtractor(self.cost_tracker, ontology_path)
        
    def run_evaluation(self, system: BaseRAGSystem, system_name: str):
        print(f"=== KHỞI ĐỘNG BENCHMARK: {system_name} ===")
        
        # Thư mục checkpoint độc lập cho mỗi tay súng
        system_dir = os.path.join(self.results_dir, system_name)
        checkpoint = CheckpointManager(system_dir)
        
        # Lọc Stratified Reporting
        t1_t25_questions = self.loader.get_questions_for_tier("T1") # N = 165
        t4_questions = self.loader.get_questions_for_tier("T4")     # N = 200 (Toàn bộ)
        
        for q in t4_questions:
            if checkpoint.is_completed(q.question_id):
                continue
                
            print(f"Đang xử lý: {q.question_id}", end=" ... ", flush=True)
            
            try:
                # 1. Gọi RAG System
                retrieval_res = system.retrieve(q.question_id, q.question)
                sys_ans = system.generate_answer(q.question, retrieval_res)
                
                metrics_score = {
                    "question_id": q.question_id,
                    "system_name": system_name,
                    "error": None,
                    "timestamp": datetime.now().isoformat(),
                    "latency_ms": retrieval_res.latency_ms
                }
                
                # 2. Chấm Tầng 1 và 2.5 (N=165)
                if q in t1_t25_questions:
                    gold_ctx = q.ground_truth_context or {}
                    metrics_score["t1_mrr"] = Tier1RetrievalMetrics.calculate_mrr(retrieval_res, gold_ctx)
                    
                    # [BLINDING MECHANISM]: Chỉ truyền Q, Sys_Ans, Gold_Ans. Tuyệt đối không truyền system_name.
                    t25_res = self.tier25.evaluate(q.question, sys_ans, q.expected_answer)
                    metrics_score["t25_score"] = t25_res.score
                    metrics_score["t25_reasoning"] = t25_res.reasoning
                    
                # 3. Chấm Tầng 4 (LSV Gold-free - N=200)
                metrics_score["t4_lsv_score"] = self.tier4_lsv.validate(sys_ans)
                
                # 4. Ghi Atomic Checkpoint (Mỗi câu 1 file)
                checkpoint.save(q.question_id, metrics_score)
                print("OK")
                
            except Exception as e:
                print(f"FAIL ({str(e)})")
                error_state = {
                    "question_id": q.question_id,
                    "system_name": system_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "latency_ms": None,
                    "t1_mrr": None,
                    "t25_score": None,
                    "t4_lsv_score": None
                }
                checkpoint.save(q.question_id, error_state)
                
        print(f"=== HOÀN TẤT BENCHMARK: {system_name} ===")
        print(self.cost_tracker.report())
        print("Note: Gộp các file JSON thành CSV bằng script aggregate.py riêng.")
