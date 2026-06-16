import urllib.request
import urllib.parse
import mimetypes
import uuid

def send_multipart_request():
    url = "http://localhost:8000/api/analyse"
    file_path = "test_resume.docx"
    jd_text = "We are looking for a Software Engineer with experience in Python, FastAPI, React, Docker, and PostgreSQL. You will design, build, and deploy high-performance web applications."
    
    # Read file bytes
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    boundary = uuid.uuid4().hex
    
    # Construct multipart request body
    body = []
    
    # Add jd_text form field
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(b'Content-Disposition: form-data; name="jd_text"')
    body.append(b'')
    body.append(jd_text.encode('utf-8'))
    
    # Add resume file field
    body.append(f"--{boundary}".encode('utf-8'))
    body.append(b'Content-Disposition: form-data; name="resume"; filename="test_resume.docx"')
    body.append(b'Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    body.append(b'')
    body.append(file_bytes)
    
    body.append(f"--{boundary}--".encode('utf-8'))
    body.append(b'')
    
    data = b'\r\n'.join(body)
    
    req = urllib.request.Request(url, data=data)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('Content-Length', len(data))
    
    print("Sending request to backend...")
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            print("SUCCESS! Response received:")
            print(html[:500] + "...")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        try:
            print(e.read().decode('utf-8'))
        except Exception:
            pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_multipart_request()
