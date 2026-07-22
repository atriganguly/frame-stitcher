# FrameStitcher

An independent, state-free microservice dedicated to compiling high-speed JPEG telemetry streams into Constant Frame Rate (CFR) MP4 video tapes. Built for extreme I/O efficiency using OpenCV bindings.

## Core Capabilities
* **MSE Deduplication:** Calculates Mean Squared Error between consecutive frames to silently drop redundant static images, heavily reducing output file sizes.
* **CFR Padding Verification:** Automatically parses `HHMMSS_fff` file string conventions to inject deterministic time-padding blocks for accurately simulating interface delays.
* **Dual Execution Routes:** Operates on both streamed `.zip` archives or concurrent outbound array HTTP fetches depending on the orchestrator's payload methodology.