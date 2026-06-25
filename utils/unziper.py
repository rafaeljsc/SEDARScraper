import zipfile
from pathlib import Path
from uuid import uuid4

def unziper(
    origin: Path = Path.joinpath(Path(__file__).parent.parent, "output"),
) -> list[Path]:
    """Descompacta arquivos numa pasta específica.
    
    Args:
        origin (Path): Pasta com os zips a serem descompactados. Padrão: Pasta `output` na raiz do projeto
    """
    
    zips = origin.rglob("*.zip")
       
    for zip in zips:
        with zipfile.ZipFile(zip, "r") as zip_ref:
            zip_ref.extractall(origin)
    
    pdfs = origin.rglob("*.pdf*")

    for pdf in pdfs:
        pdf_uuid = str(uuid4()) + "_" + pdf.name
        extension_missing = not pdf_uuid.lower().endswith(".pdf")
        pdf_renamed = (
            pdf.parent / (pdf_uuid + ".pdf")
            if extension_missing
            else pdf.parent / pdf_uuid
        )
        pdf.rename(pdf_renamed)
        
    return list(origin.rglob("*.pdf*"))
