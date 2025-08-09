import random
from typing import Any, List
from collections import defaultdict

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(str(value).replace(',', ''))
    except:
        return default

def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(safe_float(value))
    except:
        return default

def generate_random_sparkline(points: int = 30) -> List[float]:
    base_price = random.uniform(0.1, 100)
    sparkline = []
    current_price = base_price
    
    for i in range(points):
        change_percent = random.uniform(-0.05, 0.05)
        current_price = current_price * (1 + change_percent)
        sparkline.append(round(current_price, 8))
    
    return sparkline

def deduplicate_records(records: List[dict], key_field: str) -> List[dict]:
    grouped = defaultdict(list)
    
    for record in records:
        if record.get('is_deleted', False):
            continue
        key = record.get(key_field, '')
        if key:
            grouped[key].append(record)
    
    result = []
    for key, group in grouped.items():
        if len(group) == 1:
            result.append(group[0])
        else:
            latest = sorted(group, key=lambda x: x.get('updated_at', ''), reverse=True)[0]
            result.append(latest)
    
    return result