
- Mapiranje na API:
  1) Upload → POST /api/v1/upload
  2) Transcript → GET /api/v1/transcript/{id}
  3) Lead → POST /api/v1/lead
  4) Napravi vest → POST /api/v1/article
  5) Prikaz vesti → GET /api/v1/article/{id}

- Tipovi i limit: MP3/WAV/TXT/DOC, max 50 MB.

- Kriterijumi uspeha:
  1) Upload: odgovor 201 sa `id`.
  2) Transcript: 200 sa `status: "ready"` i tekstom.
  3) Lead: 200 sa `status: "lead_saved"`.
  4) Article: 200 sa `status: "article_ready"`.
  5) Prikaz vesti: 200 sa punim tekstom.

- Greške (primeri): 400/413 na upload, 404 na transcript/article, 409 na ponovni `POST /article`.

- Podrška: na grešci prikazati `Request ID` (header `X-Request-ID`).
