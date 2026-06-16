import urllib.request
import urllib.parse
import json

def test_chat():
    url = "http://localhost:8000/api/chat"
    
    payload = {
        "message": "Can you summarize my strong points based on my resume?",
        "resume_context": "Summary: Experienced software engineer with Python and Docker skills.",
        "jd_context": "We need a Senior Software Engineer with Python and Docker."
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Content-Length', len(data))
    
    print("Sending chat request to backend...")
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("SUCCESS! Chat reply received:")
            print(json.dumps(res, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
