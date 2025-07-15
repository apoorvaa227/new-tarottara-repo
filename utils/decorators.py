# decorators.py
import time
from functools import wraps

def log_timing(label=""):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"\n🧙 {label} Drawing cards and interpreting...")
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"⏱️ {label} took {duration:.2f} sec")
            return result, duration  # we return both
        return wrapper
    return decorator
