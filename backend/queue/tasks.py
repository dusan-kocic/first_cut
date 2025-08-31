# backend/queue/tasks.py
import time

def generate_article_job(item_id: str) -> dict:
    # Placeholder: simulira obradu (zameni stvarnom logikom kada bude spremna)
    time.sleep(2)  # simulacija obrade
    article_text = f"Generated article for {item_id}."
    return {"id": item_id, "status": "article_ready", "article": article_text}
