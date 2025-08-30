# SECURITY CHECKLIST (MVP)
- HTTPS enabled (prod), HTTP->HTTPS redirect, TLS >= 1.2
- CORS: allow FRONTEND_ORIGIN (+ localhost:3000 in dev)
- Access-Control-Expose-Headers: X-Request-ID
- Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, CSP, no-store on sensitive endpoints
