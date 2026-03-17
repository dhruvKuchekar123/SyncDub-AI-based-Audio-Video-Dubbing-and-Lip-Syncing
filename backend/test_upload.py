import requests
import time
import os
import sys

# use the file provided as an argument or fallback to input.mp4 in the parent folder
video_file = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\Dhruv kuchekar\OneDrive\Documents\Desktop\lipdub_project_final\input.mp4"

if not os.path.exists(video_file):
    print(f"Error: Could not find {video_file}")
    sys.exit(1)

print(f"Uploading {video_file}...")
with open(video_file, 'rb') as f:
    r = requests.post("http://127.0.0.1:8000/upload-video/", files={"file": f})

print("Upload response:", r.json())
print("Waiting for processing to complete...")

while True:
    try:
        r = requests.get("http://127.0.0.1:8000/progress")
        data = r.json()
        print(f"Progress: {data.get('progress')}% - {data.get('status')}")
        
        if data.get("progress") == 100:
            print("Processing complete!")
            v = requests.get("http://127.0.0.1:8000/video")
            print("Video URL:", v.json())
            break
            
        time.sleep(2)
    except Exception as e:
        print("Error getting progress:", e)
        time.sleep(5)
