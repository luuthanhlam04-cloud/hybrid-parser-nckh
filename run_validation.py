import logging
logging.basicConfig(level=logging.INFO)

from src.validation import ValidationEngine

engine = ValidationEngine()
report = engine.run()

s = report["summary"]
print(f"Score: {s['structural_integrity_score']}%")
print(f"Errors: {s['fatal_errors_count']}")
print(f"Warnings: {s['warnings_count']}")
print(f"Validated: {s['total_nodes_validated']}/{s['total_nodes_received']}")
