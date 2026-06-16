import urllib.request
import urllib.parse
import json

def test_roadmap():
    url = "http://localhost:8000/api/roadmap"
    
    # Payload with a committed project
    payload = {
        "committed_projects": [
            {
                "title": "Automated Web Testing Suite",
                "description": "Build a full automated test suite for an e-commerce website.",
                "tech_stack": ["Python", "Selenium", "Pytest"],
                "estimated_time": "2–3 weeks",
                "difficulty": "Beginner",
                "target_skill": "Selenium",
                "skill_path": ["Python", "Selenium"],
                "committed": True
            }
        ],
        "skill_gaps": [
            {
                "skill": "Selenium",
                "reachable": True,
                "confidence": 90,
                "risk": "LOW"
            }
        ],
        "user_level": "fresher"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Content-Length', len(data))
    
    print("Sending roadmap request to backend...")
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print("SUCCESS! Roadmap generated:")
            print(json.dumps(res, indent=2)[:500] + "...")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_roadmap()
