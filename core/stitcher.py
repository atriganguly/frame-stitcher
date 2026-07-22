import os
import cv2
import glob
import numpy as np
from typing import Dict, Any

def _parse_ms_from_filename(filename: str) -> int | None:
    try:
        base = os.path.basename(filename)
        time_part = base[:10]
        hh = int(time_part[0:2])
        mm = int(time_part[2:4])
        ss = int(time_part[4:6])
        fff = int(time_part[7:10])
        return (hh * 3600 + mm * 60 + ss) * 1000 + fff
    except Exception:
        return None

def compile_cfr_video(
    source_dir: str, 
    output_filepath: str, 
    fps: int = 30, 
    resolution: tuple[int, int] = (1280, 720),
    mse_threshold: float = 5.0,
    max_idle_ms: int = 10000
) -> Dict[str, Any]:
    
    images = sorted([
        f for f in glob.glob(os.path.join(source_dir, "*"))
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    if not images:
        raise ValueError("No valid image frames found in the target directory.")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_filepath, fourcc, fps, resolution)

    prev_frame_gray = None
    prev_ms = None
    frames_written = 0
    frames_dropped = 0
    ms_per_frame = 1000.0 / fps

    try:
        for img_path in images:
            curr_ms = _parse_ms_from_filename(img_path)
            frame = cv2.imread(img_path)
            
            if frame is None:
                continue

            resized_frame = cv2.resize(frame, resolution, interpolation=cv2.INTER_AREA)
            gray_curr = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

            if prev_frame_gray is not None:
                err = np.sum((gray_curr.astype("float") - prev_frame_gray.astype("float")) ** 2)
                err /= float(gray_curr.shape[0] * gray_curr.shape[1])
                
                if err < mse_threshold:
                    frames_dropped += 1
                    continue

            write_count = 1
            if prev_ms is not None and curr_ms is not None and curr_ms >= prev_ms:
                delta_ms = curr_ms - prev_ms
                if delta_ms > max_idle_ms:
                    delta_ms = max_idle_ms
                write_count = max(1, int(round(delta_ms / ms_per_frame)))

            for _ in range(write_count):
                video_writer.write(resized_frame)
                frames_written += 1

            prev_frame_gray = gray_curr
            if curr_ms is not None:
                prev_ms = curr_ms

        if prev_frame_gray is not None:
            for _ in range(fps * 2):
                video_writer.write(resized_frame)
                frames_written += 1

    finally:
        video_writer.release()

    return {
        "status": "SUCCESS",
        "frames_written": frames_written,
        "frames_deduplicated": frames_dropped,
        "resolution": f"{resolution[0]}x{resolution[1]}",
        "fps": fps
    }