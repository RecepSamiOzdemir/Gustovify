# Gustovify Faz 1 Saglamlastirma Tasarim Dokumani

## Context

Gustovify, mutfak yonetimi ve tarif optimizasyonu icin gelistirilen bir mobil uygulama ekosistemidir. Backend (FastAPI + SQLAlchemy + SQLite) ve Mobile (React Native/Expo + TypeScript + Drizzle ORM) olmak uzere iki ana katmandan olusur.

Faz 1'in buyuk kismi tamamlanmis durumda: kimlik dogrulama (JWT + refresh token), temel CRUD islemleri, auth-protected endpoint'ler, rate limiting ve CORS yapilandirilmis. Ancak production-ready olabilmesi icin test altyapisi, CI/CD, Docker, pagination, error handling ve kod kalitesi iyilestirmeleri gerekiyor.

**Hedef:** Faz 1'i production-ready kaliteye tasimak, Faz 2'ye gecis icin saglam bir altyapi olusturmak.

**Yaklasim:** Bottom-Up — altyapidan baslayarak yukari dogru ilerle.

**Kararlar:**
- Senkronizasyon (offline-first + cloud sync) simdilik atlanacak
- Backend router bolme BU faza dahil
- Deploy hedefi henuz belirlenmedi, Docker + CI hazirlanacak

---

## Bolum 1: CI/CD & Docker Altyapisi

### 1.1 Docker

- `Backend/Dockerfile` — Python 3.9-slim, multi-stage build, uvicorn
- `docker-compose.yml` — Backend servisi + volume'lar
- `docker-compose.dev.yml` — Hot-reload destekli gelistirme ortami
- `.env` mount edilir, image'a gomulmez
- PostgreSQL icin hazir yapilandirma (simdilik SQLite)

### 1.2 CI/CD (GitHub Actions)

- `.github/workflows/backend-ci.yml`: checkout → python → pip install → ruff → pytest → pip-audit
- `.github/workflows/mobile-ci.yml`: checkout → node → npm ci → tsc --noEmit → eslint → jest

### 1.3 App Branding

- `Mobile/app.json`: name "Mobile" → "Gustovify"
- `Mobile/package.json`: name → "gustovify-mobile"

### 1.4 Seed Data Otomasyonu

- `main.py` startup event'e entegre (lifespan context manager)
- Idempotent: zaten varsa tekrar eklemez

---

## Bolum 2: Test Altyapisi

### 2.1 Backend (pytest + httpx)

- `Backend/requirements-dev.txt`
- `Backend/tests/conftest.py` — In-memory SQLite, test client, auth helper
- Test dosyalari: test_auth, test_recipes, test_inventory, test_shopping, test_users

### 2.2 Frontend (jest + testing-library)

- `Mobile/jest.config.js`
- Service testleri: api, auth, inventory, recipes
- Component testleri: RecipeCard, CookingModeModal

---

## Bolum 3: API Iyilestirmeleri

### 3.1 Pagination

- skip/limit query params (default: skip=0, limit=50)
- Response: { items, total, skip, limit }

### 3.2 Resim Destegi

- Recipe modeline image_url (scraper'dan gelen gorsel URL'i)
- Mobile'da RecipeCard ve detay sayfasinda gosterim

### 3.3 Hata Mesajlari Standardizasyonu

- Validation error handler
- Tutarli Turkce mesaj formati

---

## Bolum 4: Mobile Duzeltmeler & Polish

### 4.1 Error Handling

- Global ErrorBoundary componenti
- Network hata bildirimi tutarliligi

### 4.2 UX Iyilestirmeleri

- Loading state tutarliligi
- Pull-to-refresh eksik sayfalarda
- EmptyState kullanimi

### 4.3 Backend Router Bolme

- main.py → routers/ (auth, recipes, inventory, shopping, users, utils)
- main.py sadece app setup, middleware, router include

### 4.4 Kod Kalitesi

- Dead code temizligi
- ruff linter config (pyproject.toml)
- TypeScript uyumsuzluk kontrolu

---

## Uygulama Sirasi

1. Docker + CI/CD
2. Backend router bolme
3. Seed data otomasyonu
4. App branding
5. Backend test altyapisi
6. API pagination
7. Resim destegi
8. Hata mesajlari standardizasyonu
9. Frontend test altyapisi
10. Error boundaries
11. UX iyilestirmeleri
12. Kod kalitesi
