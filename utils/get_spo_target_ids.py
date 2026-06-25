import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_spo_target_ids(site: str, lib: str, client: httpx.AsyncClient) -> tuple[str, str]:
    """Retorna os ids do site e biblioteca. Esses dados serão necessários para a etapa de upload dos arquivos.

    Args:
        site (str): Nome do site
        lib (str): Nome da biblioteca
        client (httpx.AsyncClient): Sessão autenticada do Graph
    """
    
    spo_tenant_request = await client.get("https://graph.microsoft.com/v1.0/sites/root")
    if not spo_tenant_request.is_success:
        logger.error(
            f"Não foi possível buscar sites. Verifique a conexão e se o App Registration possui a permissão `Sites.ReadWrite.All` ({spo_tenant_request.status_code})"
        )
        return None, spo_tenant_request
    
    spo_tenant_host = spo_tenant_request.json()["webUrl"].split('/')[-1]

    site_request = await client.get(
        f"https://graph.microsoft.com/v1.0/sites/{spo_tenant_host}:/sites/{site}"
    )
    
    if not site_request.is_success:
        logger.error(
            f"Não foi possível encontrar o site `{site}` em `{spo_tenant_host}`. Verifique a conexão e se o App Registration possui a permissão `Sites.ReadWrite.All` ({site_request.status_code})"
        )
        return None, site_request
    
    site_id = site_request.json()["id"]

    lib_request = await client.get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives?$top=999"
    )
    
    lib_id = None
    if lib_request.is_success:
        lib_id = next((i["id"] for i in lib_request.json()["value"] if i["name"].lower() == lib.lower()), None)
    
    if not lib_id and not lib_request.is_success:
        logger.error(
            f"Não foi possível encontrar a biblioteca `{lib}` em `{site}`. Verifique a conexão e se o App Registration possui a permissão `Sites.ReadWrite.All` ({lib_request.status_code})"
        )
        return None, lib_request
    
    return site_id, lib_id   