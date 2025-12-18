
import sys
import os

sys.path.append(os.getcwd())

try:
    from app.models import CountSchedule
    print("Import successful")
    print(f"CountSchedule.id: {CountSchedule.id}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
