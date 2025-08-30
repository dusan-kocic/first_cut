API UGOVOR (MVP – First Cut) — Konsolidovana verzija (Stavke 1–16)

Stavka 1 — Opseg i ciljevi API ugovora (First Cut MVP)
• Opseg: API pokriva minimalni korisnički tok aplikacije: upload audio fajla → transkripcija → unos lida → generisanje vesti → prikaz gotove vesti.
• Cilj: omogućiti da frontend i backend imaju jasno definisan dogovor o komunikaciji. Time se osigurava da frontend zna kako da pošalje fajl i lid, a backend da vrati tačno strukturisan transkript i generisanu vest.

Stavka 2 — Resursi i rute (endpointi API-ja za minimalni tok)
NAPOMENA: Sve rute u nastavku nasleđuju bazni prefiks iz Stavke 8 — /api/v1.
Za minimalni korisnički tok potrebno je definisati sledeće resurse i rute:
1) Upload audio fajla
   • POST /upload
   • Opis: prima audio fajl (multipart/form-data).
2) Dohvatanje transkripta
   • GET /transcript/{id}
   • Opis: vraća transkribovan tekst za uploadovani fajl.
3) Unos lida
   • POST /lead
   • Opis: prima lid (kratki uvod u vest) vezan za određeni transkript.
4) Generisanje vesti
   • POST /article
   • Opis: koristi transkript i lid da generiše gotovu vest.
5) Dohvatanje gotove vesti
   • GET /article/{id}
   • Opis: vraća finalni strukturisan tekst vesti spreman za prikaz.

Stavka 3 — Sheme zahteva i odgovora (First Cut MVP, engleski standard)
1) Upload audio file
   • POST /upload
   • Request (multipart/form-data):
     – file: binary (audio/mpeg, audio/wav, text/plain, application/msword)
   • Response (201 Created):
     {
       "id": "12345",
       "filename": "interview.wav",
       "status": "processing"
     }

2) Get transcript
   • GET /transcript/{id}
   • Response (200 OK):
     {
       "id": "12345",
       "transcript": "Predsednik je danas najavio mere...",
       "status": "ready"
     }

3) Submit lead
   • POST /lead
   • Request (application/json):
     {
       "id": "12345",
       "lead": "Predsednik najavio nove mere..."
     }
   • Response (200 OK):
     {
       "id": "12345",
       "lead": "Predsednik najavio nove mere...",
       "status": "lead_saved"
     }

4) Generate article
   • POST /article
   • Request (application/json):
     {
       "id": "12345"
     }
   • Response (200 OK):
     {
       "id": "12345",
       "article": "Predsednik je danas najavio nove mere...",
       "status": "article_ready"
     }

5) Get article
   • GET /article/{id}
   • Response (200 OK):
     {
       "id": "12345",
       "article": "Predsednik je danas najavio nove mere...",
       "status": "article_ready"
     }

Stavka 4 — Status kodovi i model grešaka (First Cut MVP)
Opšti status kodovi
• 200 OK — uspešan zahtev.
• 201 Created — resurs uspešno kreiran (npr. upload fajla).
• 400 Bad Request — nedostaju obavezni parametri ili pogrešan format.
• 401 Unauthorized — korisnik nema validnu autentikaciju (za kasnije faze).
• 404 Not Found — traženi resurs ne postoji (npr. transcript ID).
• 409 Conflict — pokušaj obrade već obrađenog resursa.
• 413 Payload Too Large — fajl veći od limita (vidi Stavku 6).
• 500 Internal Server Error — neočekivana greška na serveru.

Model greške (JSON odgovor)
Format:
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Transcript with id 12345 not found"
  }
}
Polja:
• code → mašinski čitljiv identifikator greške (ENG, UPPERCASE).
• message → opis greške čitljiv za korisnika.

Primeri po rutama
• POST /upload → 400 Bad Request (ako fajl nije podržan tip).
• GET /transcript/{id} → 404 Not Found (ako ID ne postoji).
• POST /lead → 400 Bad Request (ako lid nije poslat).
• POST /article → 409 Conflict (ako je vest već generisana).
• GET /article/{id} → 404 Not Found (ako ID ne postoji).

Stavka 5 — Autentikacija i autorizacija (First Cut MVP)
MVP faza
• Nije obavezna autentikacija (cilj MVP-a je demonstracija minimalnog toka: upload → transcript → lead → article).
• Endpointi su dostupni bez login sistema.

Plan za proširenje
• JWT (JSON Web Token) autentikacija za API korisnike.
• Token se dobija nakon prijave (POST /auth/login) i šalje se u Authorization: Bearer <token> zaglavlju.
• Svi endpointi u produkciji zahtevaju validan token.

Dozvole (autorizacija)
• U MVP-u: nema podele rola.
• U kasnijim fazama:
  – ROLE_JOURNALIST → može uploadovati fajl i unositi lid.
  – ROLE_EDITOR → može pregledati i objaviti finalne vesti.

Primer HTTP zaglavlja za autorizovani zahtev (kasnija faza):
GET /article/12345
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Stavka 6 — Pravila za upload (First Cut MVP)
Dozvoljeni tipovi fajla
• audio/mpeg (.mp3)
• audio/wav (.wav)
• text/plain (.txt)
• application/msword (.doc)
• (kasnije opcionalno: application/vnd.openxmlformats-officedocument.wordprocessingml.document → .docx)

Maksimalna veličina fajla
• MVP: 50 MB po fajlu.
• Kasnije: konfigurisano u cloud okruženju (npr. 200 MB).

Ograničenja po broju
• MVP: 1 fajl po upload-u.
• Kasnije: batch upload (više fajlova odjednom).

Validacija na serveru
• Ako tip fajla nije podržan → 400 Bad Request.
• Ako je fajl veći od limita → 413 Payload Too Large.

Bezbednosna pravila
• Skeniranje fajla pre obrade (antivirus, MIME-type check).
• Čuvanje fajla u privremenom storage-u dok se ne transkribuje.

Prikaz u transkriptu (za .txt i .doc)
• Ako se pošalje .txt ili .doc fajl → sadržaj dokumenta se učitava u celosti i prikazuje direktno u sekciji Transcript.
• Status se tretira isto kao i kod audio fajla: "status": "ready".

Stavka 7 — Paginacija, filtriranje i sort (First Cut MVP i proširenja)
MVP faza
• Paginacija, filtriranje i sortiranje nisu potrebni jer se u minimalnom korisničkom toku radi samo sa jednim fajlom/vesti po sesiji.
• Svi odgovori API-ja vraćaju kompletan sadržaj bez presecanja.

Plan za proširenje (kada se uvede history bar ili rad sa listom transkripata/članaka)
• Paginacija: standardna polja page, per_page i meta-informacije u odgovoru:
  {
    "data": [ ... ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total_pages": 5,
      "total_items": 45
    }
  }
• Filtriranje: podrška za query parametre (npr. GET /articles?status=ready&author=editor1).
• Sort: parametar sort sa prefiksom - za opadajuće (GET /articles?sort=-created_at).

Standard
• Sva meta polja i query parametri u engleskom jeziku.
• Default sortiranje po created_at DESC.

Stavka 8 — Verzionisanje API-ja (pravila i konvencije)
MVP faza
• API se objavljuje kao v1.
• Svi endpointi nose prefiks /api/v1/ (npr. /api/v1/upload).

Pravila za nove verzije
• Kada se uvedu promene koje nisu kompatibilne unazad, pravi se nova verzija (npr. /api/v2/).
• Manje promene koje su kompatibilne (npr. dodavanje opcionalnog polja u odgovoru) ostaju u istoj verziji.

Konvencija verzionisanja
• Verzija se uvek definiše u URL-u.
• Semantičko verzionisanje u dokumentaciji (npr. 1.0.0, 1.1.0).
• Stabilne verzije označene brojem (v1, v2), eksperimentalne kao beta ili alpha (/api/v1beta/).

Preporuke za klijente
• Frontend i integracije se obavezno vezuju na tačnu verziju (/api/v1/).
• Kada se objavi nova verzija, stara ostaje aktivna tokom prelaznog perioda (npr. 6 meseci).

Stavka 9 — Rate limiting i kvote (osnovna pravila za zaštitu API-ja)
MVP faza
• Rate limiting i kvote nisu obavezni u MVP-u.
• Fokus je na minimalnom korisničkom toku bez ograničenja.

Plan za produkciju
• Rate limiting po korisniku/IP-u: npr. 100 zahteva u minuti.
• Kvote po korisniku (pretplatnički model):
  – Basic plan: npr. 200 fajlova mesečno.
  – Pro plan: npr. 2000 fajlova mesečno.
• Kada se dostigne limit → API vraća 429 Too Many Requests.

Odgovor u slučaju prekoračenja limita
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later."
  }
}

Tehnička implementacija
• Token bucket ili leaky bucket algoritam.
• Praćenje kroz Redis ili sličan in-memory store.
• Informacije o preostalim zahtevima u HTTP zaglavljima:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 25
  X-RateLimit-Reset: 1694096400

Stavka 10 — Performanse i SLA (MVP faza)
MVP
• Nema formalnog SLA.
• Beleže se samo ciljani odzivi radi testiranja vrednosti sistema:
  – Upload validacija: < 1s
  – Transkripcija fajla do 5 MB: do 10s
  – Generisanje vesti: do 3s
Produkcija (placeholder)
• Formalni SLA (dostupnost, garancije, kompenzacije) biće definisan kada sistem pređe iz MVP-a u komercijalnu fazu.

Stavka 11 — Logging i monitoring (osnovna pravila za praćenje sistema)
MVP faza
• Osnovni server logovi (request/response statusi, greške).
• Beleži se: vreme zahteva, endpoint, status kod, trajanje obrade.
• Greške se loguju sa stack trace-om.

Monitoring u MVP-u
• Health-check endpoint: GET /health → vraća 200 OK.
• Jednostavno praćenje up-time-a (ping servis).

Plan za produkciju
• Centralizovan logging (npr. ELK stack ili cloud logging servis).
• Struktura logova u JSON formatu radi lakšeg pretraživanja.
• Metrike performansi: latency, error rate, broj obrada u minutu.
• Alerting sistem (email/Slack) za kritične greške i prekide rada.

Sigurnost logova
• Bez logovanja osetljivih podataka (npr. sadržaj fajla, lead tekst).
• Logovi čuvani u skladu sa pravilima zadržavanja (rotacija, max 30 dana u MVP fazi).

Stavka 12 — Kompatibilnost i promene (pravila za backward compatibility i deprecation)
Backward compatibility (MVP faza)
• Svi endpointi i odgovori moraju ostati stabilni tokom MVP-a.
• Dodavanje novih polja u JSON odgovor je dozvoljeno samo kao opciono (ne sme da razbije postojeće klijente).
• Uklanjanje ili preimenovanje polja nije dozvoljeno u MVP fazi.

Pravila za promene
• Minor changes (kompatibilne): dodavanje opcionalnih parametara, novih status kodova, novih vrednosti u enum poljima.
• Breaking changes: uklanjanje polja, promena strukture JSON-a, menjanje URL ruta → zahtevaju novu verziju API-ja (/api/v2/).

Deprecation policy
• Kada se endpoint ili polje označi kao zastarelo (deprecated), ostaje dostupno minimalno 6 meseci.
• Dokumentacija mora jasno označiti zastarele elemente (DEPRECATED tag).
• API može vraćati HTTP zaglavlje Deprecation: true i opcioni Sunset datum.

Transparentnost prema klijentima
• Svaka izmena se beleži u changelog-u.
• Verzije dokumentacije čuvane u repozitorijumu (npr. docs/changelog.md).

Stavka 13 — CORS, HTTPS i sigurnosna zaglavlja (MVP)
1) HTTPS (obavezno)
• Produkcija: samo HTTPS; HTTP → 301 na HTTPS; TLS ≥ 1.2; HSTS aktivan.
• Dev: HTTP dozvoljen samo za http://localhost:*.

2) CORS (minimalna pravila)
• Dozvoljeni origin-i: tačan FRONTEND_ORIGIN iz konfiguracije + http://localhost:3000 u dev-u.
• Dozvoljene metode: GET, POST, OPTIONS.
• Dozvoljena zaglavlja: Content-Type, Authorization, X-Request-ID.
• Credentials: false.
• Preflight (OPTIONS 204) mora vraćati:
  – Access-Control-Allow-Origin: <FRONTEND_ORIGIN>
  – Access-Control-Allow-Methods: GET, POST, OPTIONS
  – Access-Control-Allow-Headers: Content-Type, Authorization, X-Request-ID
  – Access-Control-Max-Age: 600
• Izlaganje ID zahteva za JavaScript klijent:
  – Access-Control-Expose-Headers: X-Request-ID

3) Sigurnosna zaglavlja (na sve API odgovore)
• X-Content-Type-Options: nosniff
• X-Frame-Options: DENY
• Referrer-Policy: no-referrer
• Content-Security-Policy: default-src 'none'; frame-ancestors 'none'; base-uri 'none'
• Cache-Control: no-store (za /transcript i /article)

Stavka 14 — Observability (trace i correlation IDs, MVP)
Request ID (MVP obavezno)
• Klijent može poslati X-Request-ID (UUID v4). Ako ga nema, backend ga generiše.
• Backend uvek vraća isto ID u odgovoru u zaglavlju X-Request-ID.
• X-Request-ID se upisuje u sve log zapise tog zahteva.

JSON odgovor (dopuna, ne-breaking)
• U slučaju greške, pored error objekta, može biti dodatno polje:
  { "error": { "code": "…", "message": "…" }, "request_id": "…" }
• Ovo polje je opciono i usklađeno sa Stavkom 12 (bez razbijanja klijenata).

Kontrakt zaglavlja
• Dozvoljeno u CORS (vidi Stavku 13): X-Request-ID.
• Na svim ishodima (uklj. 500, timeout), odgovor i log i dalje sadrže X-Request-ID.

Trace/Correlation (placeholder za proširenje)
• Za budući multi-service: passtrough W3C traceparent/tracestate bez obaveze u MVP.
• Po potrebi uvesti X-Correlation-ID za grupisanje više zahteva u jedan poslovni tok.

Stavka 15 — Deployment i environment (dev/staging/prod)
Okruženja (minimalno)
• dev: lokalni razvoj; HTTP dozvoljen samo na localhost; CORS → http://localhost:3000; test podaci, bez trajnog čuvanja.
• staging (opciono): kopija produkcije za proveru; HTTPS obavezno; CORS → tačan staging frontend origin; odvojeni podaci i logovi.
• prod: HTTPS obavezno; HSTS aktivan (vidi Stavku 13); odvojeni podaci i logovi od drugih okruženja.

Konfiguracija (env varijable, bez koda)
• ENV: dev|staging|prod
• FRONTEND_ORIGIN: tačan origin frontenda po okruženju
• MAX_UPLOAD_MB: 50 (MVP limit)
• ALLOWED_UPLOAD_TYPES: audio/mpeg,audio/wav,text/plain,application/msword
• LOG_LEVEL: INFO (MVP)

Build & release (MVP)
• Jedan artefakt po verziji; označavanje tagom (npr. v1.0.0), usklađeno sa /api/v1/.
• Deploy = zamena artefakta; čuvati poslednji stabilan za brz rollback.

Migracije i kompatibilnost
• U MVP-u izbegavati migracije šeme podataka; sve promene idu kao kompatibilne (vidi Stavku 12).
• Breaking promene zahtevaju novu API verziju (vidi Stavku 8).

Health & monitoring (osnovno)
• GET /health mora vraćati 200 OK u svim okruženjima.
• Minimalni logovi aktivni (vidi Stavku 11); logovi i podaci razdvojeni po okruženju.

CORS/HTTPS napomena
• CORS origin se postavlja po okruženju (vidi Stavku 13).
• Produkcija: samo HTTPS; dev: HTTP samo za localhost.

Stavka 16 — Dokumentacija i primeri korišćenja (OpenAPI + README + curl/JS primeri)
16.1 OpenAPI 3.0 (minimalni izvod za v1)
(openapi.yaml će sadržati punu specifikaciju; ovde je izvod za ključne rute)
------------------------------------------------------------
openapi: 3.0.3
info:
  title: First Cut API
  version: 1.0.0
servers:
  - url: <BASE_URL>/api/v1
paths:
  /upload:
    post:
      summary: Upload a file (audio/txt/doc)
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
              required: [file]
            # Allowed types per contract: audio/mpeg, audio/wav, text/plain, application/msword
      responses:
        '201': { description: Created }
        '400': { description: Bad Request }
        '413': { description: Payload Too Large }
        '500': { description: Internal Server Error }

  /transcript/{id}:
    get:
      summary: Get transcript by id
      parameters:
        - in: path
          name: id
          schema: { type: string }
          required: true
      responses:
        '200': { description: OK }
        '404': { description: Not Found }
        '500': { description: Internal Server Error }

  /lead:
    post:
      summary: Submit lead for a transcript
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                id:   { type: string }
                lead: { type: string }
              required: [id, lead]
      responses:
        '200': { description: OK }
        '400': { description: Bad Request }
        '404': { description: Not Found }
        '500': { description: Internal Server Error }

  /article:
    post:
      summary: Generate article for a transcript
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                id: { type: string }
              required: [id]
      responses:
        '200': { description: OK }
        '404': { description: Not Found }
        '409': { description: Conflict }
        '500': { description: Internal Server Error }

  /article/{id}:
    get:
      summary: Get generated article by id
      parameters:
        - in: path
          name: id
          schema: { type: string }
          required: true
      responses:
        '200': { description: OK }
        '404': { description: Not Found }
        '500': { description: Internal Server Error }
------------------------------------------------------------

16.2 README — Kako koristiti API (MVP tok)
1) Upload fajla
------------------------------------------------------------
curl -X POST "<BASE_URL>/api/v1/upload" \
  -H "Accept: application/json" \
  -F "file=@/path/to/file.mp3"
------------------------------------------------------------
Odgovor (201): {"id":"12345","filename":"file.mp3","status":"processing"}

2) Dohvati transkript
------------------------------------------------------------
curl "<BASE_URL>/api/v1/transcript/12345" -H "Accept: application/json"
------------------------------------------------------------
Odgovor (200): {"id":"12345","transcript":"...","status":"ready"}

3) Pošalji lid
------------------------------------------------------------
curl -X POST "<BASE_URL>/api/v1/lead" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"id":"12345","lead":"Predsednik najavio nove mere..."}'
------------------------------------------------------------

4) Generiši vest
------------------------------------------------------------
curl -X POST "<BASE_URL>/api/v1/article" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"id":"12345"}'
------------------------------------------------------------

5) Dohvati vest
------------------------------------------------------------
curl "<BASE_URL>/api/v1/article/12345" -H "Accept: application/json"
------------------------------------------------------------

16.3 JavaScript (fetch) — primeri iz browser-a
------------------------------------------------------------
// 1) Upload (multipart/form-data)
async function uploadFile(file) {
  const form = new FormData();
  form.append('file', file); // MP3/WAV/TXT/DOC
  const res = await fetch('<BASE_URL>/api/v1/upload', { method: 'POST', body: form });
  if (!res.ok) throw new Error('Upload failed');
  return res.json(); // { id, filename, status }
}

// 2) Get transcript
async function getTranscript(id) {
  const res = await fetch(`<BASE_URL>/api/v1/transcript/${id}`);
  if (!res.ok) throw new Error('Transcript fetch failed');
  return res.json(); // { id, transcript, status }
}

// 3) Submit lead
async function submitLead(id, leadText) {
  const res = await fetch('<BASE_URL>/api/v1/lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, lead: leadText })
  });
  if (!res.ok) throw new Error('Lead submit failed');
  return res.json(); // { id, lead, status }
}

// 4) Generate article
async function generateArticle(id) {
  const res = await fetch('<BASE_URL>/api/v1/article', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  });
  if (!res.ok) throw new Error('Article generation failed');
  return res.json(); // { id, article, status }
}

// 5) Get article
async function getArticle(id) {
  const res = await fetch(`<BASE_URL>/api/v1/article/${id}`);
  if (!res.ok) throw new Error('Article fetch failed');
  return res.json(); // { id, article, status }
}
------------------------------------------------------------
