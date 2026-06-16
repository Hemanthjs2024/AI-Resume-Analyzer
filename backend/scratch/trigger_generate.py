import urllib.request
import urllib.parse
import json
import uuid

def run_pipeline():
    # Step 1: Run /api/analyse
    url_analyse = "http://localhost:8000/api/analyse"
    file_path = "test_resume.docx"
    jd_text = "We are looking for a Software Engineer with experience in Python, FastAPI, React, Docker, and PostgreSQL. You will design, build, and deploy high-performance web applications."
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    boundary = uuid.uuid4().hex
    
    body = [
        f"--{boundary}".encode('utf-8'),
        b'Content-Disposition: form-data; name="jd_text"',
        b'',
        jd_text.encode('utf-8'),
        f"--{boundary}".encode('utf-8'),
        b'Content-Disposition: form-data; name="resume"; filename="test_resume.docx"',
        b'Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        b'',
        file_bytes,
        f"--{boundary}--".encode('utf-8'),
        b''
    ]
    
    data = b'\r\n'.join(body)
    
    req = urllib.request.Request(url_analyse, data=data)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('Content-Length', len(data))
    
    print("1. Running Analysis...")
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("   Analysis Succeeded.")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error in Analyse: {e.code}")
        print(e.read().decode('utf-8'))
        return
    except Exception as e:
        print(f"Error in Analyse: {e}")
        return

    # Step 2: Prepare inputs for /api/generate
    review_items = res_data["review_items"]
    # Mark all as accepted for generation
    for item in review_items:
        item["status"] = "accepted"
        
    project_suggestions = res_data["project_suggestions"]
    # Commit first project suggestion
    if project_suggestions:
        project_suggestions[0]["committed"] = True
        
    selected_skills = ["FastAPI", "React", "Docker"]
    candidate_name = res_data.get("candidate_name", "John Doe")
    structured_data = res_data["structured_data"]
    
    # Step 3: Run /api/generate
    url_generate = "http://localhost:8000/api/generate"
    gen_payload = {
        "review_items": review_items,
        "committed_projects": project_suggestions,
        "selected_skills": selected_skills,
        "candidate_name": candidate_name,
        "template": "chronological_classic",
        "structured_data": structured_data
    }
    
    gen_data = json.dumps(gen_payload).encode('utf-8')
    req_gen = urllib.request.Request(url_generate, data=gen_data)
    req_gen.add_header('Content-Type', 'application/json')
    req_gen.add_header('Content-Length', len(gen_data))
    
    print("2. Running Generation...")
    try:
        with urllib.request.urlopen(req_gen) as gen_response:
            gen_res = json.loads(gen_response.read().decode('utf-8'))
            print("   Generation Succeeded! Response:")
            print(json.dumps(gen_res, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error in Generate: {e.code} - {e.reason}")
        try:
            print(e.read().decode('utf-8'))
        except Exception:
            pass
    except Exception as e:
        print(f"Error in Generate: {e}")

if __name__ == "__main__":
    run_pipeline()
