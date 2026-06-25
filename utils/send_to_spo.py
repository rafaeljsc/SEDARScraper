import httpx
from pathlib import Path
from tqdm.asyncio import tqdm
from .auth import graph
from .get_spo_target_ids import get_spo_target_ids
from urllib.parse import quote
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

limits = httpx.Limits(max_connections=20, max_keepalive_connections=20)

async def bulk(client: httpx.AsyncClient, item: Path, site_id: str, drive_id: str, path:str):
    
    filename = item.name
    file_size = item.stat().st_size

    session_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:{path}{quote(filename)}:/createUploadSession"
    

    body = {"item": {"@microsoft.graph.conflictBehavior": "replace"}}

    resp_session = await client.post(session_url, json=body)

    if not resp_session.is_success:
        return {
            "file": filename,
            "status": resp_session.status_code,
            "error": resp_session.text,
        }

    upload_url = resp_session.json()["uploadUrl"]

    # Upload em Chunks
    chunk_size = 327680 * 40  # ~ 13 MB
    start = 0
    last_status = None

    with item.open("rb") as f:
        while start < file_size:
            chunk = f.read(chunk_size)
            actual_chunk_size = len(chunk)
            end = start + actual_chunk_size - 1

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(actual_chunk_size),
            }

            chunk_resp = await client.put(upload_url, content=chunk, headers=headers)

            if not chunk_resp.is_success:
                return {
                    "file": filename,
                    "status": chunk_resp.status_code,
                    "error": chunk_resp.text,
                }

            last_status = chunk_resp.status_code
            start += actual_chunk_size

    return {"file": filename, "status": last_status}

async def send_to_spo(items: list[Path], site: str, lib: str, path: str = "/") ->list[dict] | None:

    async with httpx.AsyncClient(limits=limits, timeout=None) as client:
        client.headers.update(graph())
        site_id, lib_id = await get_spo_target_ids(site, lib, client)
        
        if not site_id:
            return
        
        path = f"/{quote(path)}/" if path != "/" else path
        tasks = [bulk(client, item, site_id, lib_id, path) for item in items]

        results = await tqdm.gather(
            *tasks, total=len(items), desc="Enviando para o SharePoint",
        )
    
    return results
