import io
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze():
    with open('src/ontology/logs/unresolved_entities.log', encoding='utf-8') as f:
        lines = f.readlines()
        
    entities = [l.split('|', 1)[1].strip() for l in lines if '|' in l]
    
    print('=== TOP 50 UNRESOLVED ENTITIES ===')
    for k, v in Counter(entities).most_common(50):
        print(f'{v} - {k}')
        
if __name__ == '__main__':
    analyze()
