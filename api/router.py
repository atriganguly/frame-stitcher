import os
import shutil
import zipfile
import tempfile
import asyncio
import httpx
from urllib.parse import urlparse
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Security
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from starlette.background import BackgroundTask

from infra.config import settings
from api.schemas import UrlStitchRequest
from core.stitcher import compile_cfr_video

router = APIRouter(prefix="/v1/video", tags=["Video Compilation"])
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    return api_key

def _cleanup_temp_dir(dir_path: str):
    shutil.rmtree(dir_path, ignore_errors=True)

@router.post("/stitch/zip", dependencies=[Depends(verify_api_key)])
async def stitch_from_zip(
    file: UploadFile = File(...),
    fps: int = Form(30),
    width: int = Form(1280),
    height: int = Form(720),
    mse_threshold: float = Form(5.0),
    max_idle_ms: int = Form(10000)
):
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .zip archive.")

    temp_dir = tempfile.mkdtemp(prefix="framestitcher_")
    extract_dir = os.path.join(temp_dir, "frames")
    os.makedirs(extract_dir, exist_ok=True)
    zip_path = os.path.join(temp_dir, "upload.zip")
    output_mp4 = os.path.join(temp_dir, "compiled_tape.mp4")

    try:
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        compile_cfr_video(
            source_dir=extract_dir,
            output_filepath=output_mp4,
            fps=fps,
            resolution=(width, height),
            mse_threshold=mse_threshold,
            max_idle_ms=max_idle_ms
        )

        return FileResponse(
            path=output_mp4,
            media_type="video/mp4",
            filename="compiled_tape.mp4",
            background=BackgroundTask(_cleanup_temp_dir, temp_dir)
        )
    except Exception as e:
        _cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stitch/urls", dependencies=[Depends(verify_api_key)])
async def stitch_from_urls(payload: UrlStitchRequest):
    if not payload.image_urls:
        raise HTTPException(status_code=400, detail="Image URL array cannot be empty.")

    temp_dir = tempfile.mkdtemp(prefix="framestitcher_")
    extract_dir = os.path.join(temp_dir, "frames")
    os.makedirs(extract_dir, exist_ok=True)
    output_mp4 = os.path.join(temp_dir, "compiled_tape.mp4")

    semaphore = asyncio.Semaphore(settings.MAX_DOWNLOAD_CONCURRENCY)

    async def download_image(client: httpx.AsyncClient, url: str):
        async with semaphore:
            try:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    return
                resp = await client.get(url, timeout=15.0)
                resp.raise_for_status()
                with open(os.path.join(extract_dir, filename), "wb") as f:
                    f.write(resp.content)
            except Exception:
                pass

    try:
        async with httpx.AsyncClient(verify=False) as client:
            tasks = [download_image(client, url) for url in payload.image_urls]
            await asyncio.gather(*tasks)

        compile_cfr_video(
            source_dir=extract_dir,
            output_filepath=output_mp4,
            fps=payload.fps,
            resolution=(payload.width, payload.height),
            mse_threshold=payload.mse_threshold,
            max_idle_ms=payload.max_idle_ms
        )

        return FileResponse(
            path=output_mp4,
            media_type="video/mp4",
            filename="compiled_tape.mp4",
            background=BackgroundTask(_cleanup_temp_dir, temp_dir)
        )
    except Exception as e:
        _cleanup_temp_dir(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))