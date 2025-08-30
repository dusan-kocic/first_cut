# TECH_STACK (MVP)

## Backend
- Jezik: Python (3.11+)
- Framework: FastAPI (ASGI)
- ASGI server: uvicorn
- Log format: JSON
- Request tracing: X-Request-ID middleware (generiše/prosleđuje i vraća `X-Request-ID` u odgovor)

## Obrada
- STT: Whisper preko API-ja
- Režim obrade: asinhrono putem job queue (enqueue → klijent prati status preko GET /article/{id})

## Skladištenje (MVP)
- Upload fajlovi: `/tmp/first_cut/uploads`
- Izlazni artefakti (transkripti/članci): `/tmp/first_cut/outputs`
- Metapodaci: SQLite (MVP)
- Retencija: brisanje fajlova i artefakata nakon **72h**

## Identiteti
- ID formati: **UUID v4**
- Imenovanje fajlova: `{id}_{original_name}` (sprečava kolizije i olakšava tracing)

## Konfiguracija (.env)
- Obavezno koristiti `.env` (u repou samo `.env.example`)
- Ključevi (MVP):  
  `BASE_URL`, `FRONTEND_ORIGIN`, `MAX_UPLOAD_MB`,  
  `ALLOWED_UPLOAD_TYPES`, `LOG_LEVEL`,  
  `STORAGE_PATH_UPLOADS`, `STORAGE_PATH_OUTPUTS`, `RETENTION_HOURS`

## Deploy (dev/staging)
- Dev: `uvicorn` na portu **8000** → `BASE_URL=http://localhost:8000/api/v1`
- Staging (minimalno): stabilan `BASE_URL` + **HTTPS** terminacija; OpenAPI dostupan na `/docs` i `/openapi.json`

## CI (minimalno, GitHub Actions)
- **Lint:** ruff (stil i brze greške)
- **Test:** kratki `pytest` koji proverava status kodove i sheme odgovora
- **Smoke:** pokretanje `scripts/curl` toka (upload → transcript → lead → article GET)

