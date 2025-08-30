# Definition of Done — MVP
[] Svi endpointi iz API_CONTRACT.md prolaze smoke test (scripts/curl)
[] Upload: 201 Created + id
[] Transcript: 200 OK + status "ready"
[] Lead: 200 OK + status "lead_saved"
[] Article (asinhrono): POST /article → 202 Accepted + status "queued"; GET /article/{id} → 200 OK sa statusom "queued"/"processing"; kada je gotovo → 200 OK + status "article_ready" + article
[] Greške: 400/413 (upload), 404 (transcript/article), 409 (article) obrađene prema ugovoru
[] X-Request-ID vraćen u svim odgovorima
[] CORS/HTTPS podešeno u skladu sa Stavkom 13
[] Logovi upisuju endpoint, status, trajanje, request_id
