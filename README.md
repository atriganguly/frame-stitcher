# FrameStitcher

An independent, state-free microservice dedicated to compiling high-speed JPEG telemetry streams into Constant Frame Rate (CFR) MP4 video tapes. Built for extreme I/O efficiency using OpenCV bindings.

## Core Capabilities
* **MSE Deduplication:** Calculates Mean Squared Error between consecutive frames to silently drop redundant static images, heavily reducing output file sizes.
* **CFR Padding Verification:** Automatically parses `HHMMSS_fff` file string conventions to inject deterministic time-padding blocks for accurately simulating interface delays.
* **Dual Execution Routes:** Operates on both streamed `.zip` archives or concurrent outbound array HTTP fetches depending on the orchestrator's payload methodology.

## Usage 

### Option 1: ZIP Upload (Ideal for Local File Systems)
```bash
curl -X POST "http://localhost:8080/v1/video/stitch/zip" \
  -H "X-API-Key: your_secure_api_key_here" \
  -F "file=@/path/to/frames.zip" \
  -F "fps=30" \
  --output compiled_tape.mp4```
  
### Option 2: Array of URLs (Ideal for Cloud Integrations)
```curl -X POST "http://localhost:8080/v1/video/stitch/urls" \
  -H "X-API-Key: your_secure_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "[https://s3.aws.com/bucket/123045_001_frame.jpg](https://s3.aws.com/bucket/123045_001_frame.jpg)",
      "[https://s3.aws.com/bucket/123046_050_frame.jpg](https://s3.aws.com/bucket/123046_050_frame.jpg)"
    ],
    "fps": 30,
    "mse_threshold": 5.0
  }' \
  --output compiled_tape.mp4```
