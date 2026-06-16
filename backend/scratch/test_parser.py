import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from services.resume_parser import parse_resume
    print("Import successful")
    # Try a dummy parse
    # result = parse_resume(b"dummy text", "test.txt")
    # print("Parse successful")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
