<div align="center">

# FrameStitcher

**An independent, state-free microservice dedicated to compiling high-speed JPEG telemetry streams into Constant Frame Rate (CFR) MP4 video tapes.**

Created by [@YourGitHubUsername](https://github.com/YourGitHubUsername)

[Repository](https://github.com/YourGitHubUsername/FrameStitcher) | [Live Demo](https://demo-url.com) | [Documentation](https://docs-url.com)

</div>

---

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-GPLv3-green)
![Language](https://img.shields.io/badge/Language-Python-informational)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement & Solution](#problem-statement--solution)
3. [Target Audience & Use Cases](#target-audience--use-cases)
4. [System Architecture](#system-architecture)
5. [Core Engineering Mechanics](#core-engineering-mechanics)
6. [Technology Stack](#technology-stack)
7. [Environment Configuration](#environment-configuration)
8. [Installation & Quick Start](#installation--quick-start)
9. [Operational Execution Modes](#operational-execution-modes)
10. [Data Lifecycle & Output Schema](#data-lifecycle--output-schema)
11. [Deployment & Infrastructure](#deployment--infrastructure)
12. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
13. [AI Agent Execution Boundaries](#ai-agent-execution-boundaries)
14. [Support & Contributions](#support--contributions)
15. [License](#license)

---

## Executive Summary

FrameStitcher is an extreme I/O microservice built to eliminate storage bloat and sequence misalignment in high-speed telemetry recording. 

The system maintains operational visibility through structured CFR padding and MSE deduplication, offering a low-maintenance infrastructure that scales efficiently while heavily reducing output file sizes and simulating accurate interface delays.

---

## Problem Statement & Solution

### The Problem
Processing high-speed automated visual streams often yields bloated, redundant, and out-of-sync video outputs. 
* **System Volatility:** Telemetry platforms drop frames under heavy load, ruining downstream video playback sync.
* **High Infrastructure Overhead:** Storing hundreds of thousands of identical static frames wastes storage and network bandwidth.
* **Telemetry Gaps:** Arbitrary timing delays make recreating exact session timing impossible from raw JPEGs.

### The Solution
FrameStitcher resolves structural instability by introducing deterministic time-padding and visual deduplication.

* **Deterministic Execution:** Automatically parses `HHMMSS_fff` file strings to inject exact time-padding blocks for CFR synchronization.
* **Cost & Overhead Reduction:** Calculates Mean Squared Error (MSE) between consecutive frames to silently drop redundant static images.
* **Audit-Ready Logging:** Exposes a stateless API with strict error boundaries, returning exactly the compiled MP4 and execution telemetry.

---

## Target Audience & Use Cases

* **Technical Leadership:** Provides clear visibility into system reliability, audit readiness, and operational cost efficiency through storage reduction.
* **Software & QA Engineers:** Delivers a modular architecture with isolated subsystems for rapid testing, handling concurrent outbound array HTTP fetches.
* **Data & System Operations:** Guarantees reliable data collection via streamlined `.zip` archives or asynchronous array processing.

---

## System Architecture

The application uses a decoupled architecture to isolate presentation, orchestration, execution, and persistent storage layers.

```text
+-------------------+      +-------------------+      +-------------------+
|  Control / UI     | ---> |  Orchestration    | ---> |  Execution Core   |
|  (Client Layer)   |      |  (FastAPI Router) |      |  (OpenCV Engine)  |
+-------------------+      +-------------------+      +-------------------+
                                     |                          |
                                     v                          v
                           +-------------------+      +-------------------+
                           | Output Artifacts  | <--- | Temporary State   |
                           | (CFR MP4 Videos)  |      | (Extracted Zips)  |
                           +-------------------+      +-------------------+
```

### Component Breakdown

* **Orchestration Layer:** Handles request routing (`/stitch/zip` & `/stitch/urls`), payload validation (Pydantic), and API Key authentication.
* **Execution Core:** Processes business logic through `compile_cfr_video`, ensuring independent error boundaries and MSE comparisons.
* **Persistence & Telemetry Layer:** Manages temporary background cleanup (`_cleanup_temp_dir`), and streams the resulting MP4 tape back to the client.

---

## Core Engineering Mechanics

To maintain system resilience under heavy loads or platform constraints, the application incorporates key engineering patterns:

### 1. Dual Execution Routes
Operates on both streamed `.zip` archives or concurrent outbound array HTTP fetches (using `asyncio` and `httpx`), adapting to the orchestrator's payload methodology.

### 2. MSE Deduplication
Execution paths evaluate the Mean Squared Error (MSE) of grayscale matrix representations between consecutive frames, silently discarding those that fall below the tolerance threshold.

### 3. CFR Padding Verification
Parses exact millisecond timing from filename strings. If a gap exceeds standard frame duration, the engine automatically injects deterministic padding copies, bound by the `max_idle_ms` ceiling.

### 4. Graceful Error & Failure Isolation
Temporary directory isolation using `tempfile`. Even in the event of frame corruption or network failure, background tasks reliably trigger cleanup routines, preventing disk space exhaustion.

---

## Technology Stack

| Category | Technology | Operational Purpose |
| :--- | :--- | :--- |
| **Core Engine** | Python 3.10 | Primary runtime environment and business logic execution. |
| **API Framework** | FastAPI & Uvicorn | Asynchronous request handling, routing, and endpoint exposure. |
| **Automation / Driver**| OpenCV Headless & Numpy | Low-level image matrix manipulation, greyscale conversion, and MP4 encoding. |
| **Data Layer** | HTTPX & aiofiles | Concurrent network I/O for fetching external telemetry arrays. |

---

## Environment Configuration

System settings are managed independently of application logic through environment variables or configuration files.

### Configuration Parameters Matrix

| Variable Name | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | String | `production` | Tracks the active deployment environment. |
| `FRAMESTITCHER_API_KEY` | String | `default_dev_key` | X-API-Key header secret for endpoint security. |
| `MAX_DOWNLOAD_CONCURRENCY` | Integer | `10` | Semaphore limit for concurrent HTTPX image fetch tasks. |

---

## Installation & Quick Start

### Prerequisites

* Python 3.10+ installed and configured in your system environment.
* `pip` available on the host machine.
* System-level dependencies for OpenCV (`libgl1`, `libglib2.0-0`).

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/YourGitHubUsername/FrameStitcher.git](https://github.com/YourGitHubUsername/FrameStitcher.git)
   cd FrameStitcher
   ```

2. **Configure Environment Parameters**
   ```bash
   cp .env.sample .env
   ```
   Open `.env` and configure your `FRAMESTITCHER_API_KEY`.

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Core Engine**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

---

## Operational Execution Modes

The engine can be initialized under distinct operational profiles based on endpoint targeting:

* **High-Throughput Zip Mode (`/v1/video/stitch/zip`):** Designed for bulk payload processing where the client compresses all frames prior to transit, reducing HTTP overhead.
* **Concurrent Fetch Mode (`/v1/video/stitch/urls`):** Executes high-concurrency downloads directly from pre-signed cloud storage URLs, bounded by system semaphores.

---

## Data Lifecycle & Output Schema

System outputs and execution logs are processed transiently and returned directly to the client as an octet-stream response.

### Primary Output Schema (API Response)

The API responds directly with the compiled `.mp4` binary file (`video/mp4` media type). The execution context (telemetry) is calculated internally:

| Field Name | Data Type | Field Description |
| :--- | :--- | :--- |
| `status` | String | Execution result (e.g., `SUCCESS`). |
| `frames_written` | Integer | Total frames baked into the final output. |
| `frames_deduplicated` | Integer | Total static frames dropped via MSE logic. |
| `resolution` | String | Formatted output dimensions (`WIDTHxHEIGHT`). |
| `fps` | Integer | Target constant frame rate of the MP4. |

*(Note: Internal metrics are visible in the engine return signature prior to the FastAPI FileResponse.)*

---

## Deployment & Infrastructure

### Docker Containerization
Deploy the application inside an isolated container using the provided Dockerfile setup. This handles the system-level OpenCV dependencies out-of-the-box.

Build and execute the image:

```bash
docker build -t framestitcher:latest .
docker run -d -p 8080:8080 --env-file .env framestitcher:latest
```

---

## Troubleshooting & Diagnostics

* **Issue: Output MP4 has broken or missing frames.**
  * *Cause:* Filenames do not perfectly match the `HHMMSS_fff` pattern, causing the padding calculator to return `None`.
  * *Resolution:* Ensure the first 10 characters of your source images map exactly to the chronological timestamp.

* **Issue: Image download arrays are failing with timeouts.**
  * *Cause:* Request frequencies exceeded host system HTTPX timeout limits.
  * *Resolution:* Reduce `MAX_DOWNLOAD_CONCURRENCY` in your `.env` to avoid bottlenecking outbound ports.

* **Issue: 401 Unauthorized API Responses.**
  * *Cause:* Missing or mismatched security headers.
  * *Resolution:* Ensure your request contains the `X-API-Key` header perfectly matching your `FRAMESTITCHER_API_KEY`.

---

## AI Agent Execution Boundaries

Autonomous LLMs, coding agents, and automated patch routines operating on this codebase must adhere to these structural boundaries:

1. Maintain strict decoupling between configuration parameters and core execution engines.
2. Do not introduce arbitrary delay loops (`sleep`) into operational state paths.
3. Keep all persistent file write operations asynchronous and heavily bound by temporary directory contexts.
4. Never modify `cv2.VideoWriter` configurations without explicitly preserving the `mp4v` codec standardization.

---

## Support & Contributions

This project is actively maintained to deliver reliable, open-source automation and execution infrastructure.

* **Bug Reports & Feature Suggestions:** [Open an Issue](https://github.com/YourGitHubUsername/FrameStitcher/issues)
* **Direct Enquiries:** Contact [@YourGitHubUsername](https://github.com/YourGitHubUsername) for technical questions, contributions, or pull request reviews.

---

## License

Distributed under the [GNU General Public License v3.0](LICENSE).