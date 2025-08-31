import os
from pathlib import Path

def generate_article_job(item_id: str) -> dict:
    outputs_dir = Path(os.getenv("STORAGE_PATH_OUTPUTS", "/tmp/first_cut/outputs"))
    outputs_dir.mkdir(parents=True, exist_ok=True)
    article_text = f"Generated article for {item_id}."
    out_file = outputs_dir / f"{item_id}.txt"
    out_file.write_text(article_text, encoding="utf-8")
    return {"id": item_id, "status": "article_ready", "article": article_text}
