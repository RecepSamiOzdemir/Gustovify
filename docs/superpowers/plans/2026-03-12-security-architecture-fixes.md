# Security & Architecture Fixes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all critical bugs, security vulnerabilities, and architectural issues in the Gustovify backend to bring Faz 1 to production-ready quality.

**Architecture:** Environment-based config for secrets, JWT refresh tokens, user-owned recipes with auth-protected endpoints, JSON-based instruction storage, password validation, rate limiting, and proper CORS configuration.

**Tech Stack:** FastAPI, SQLAlchemy, python-dotenv, slowapi (rate limiting), Pydantic v2

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `Backend/.env` | Create | Environment variables (SECRET_KEY, CORS origins, DB URL) |
| `Backend/.env.example` | Create | Template for .env without secrets |
| `Backend/config.py` | Create | Centralized config loading from environment |
| `Backend/auth.py` | Modify | Use config, fix deprecated datetime, add refresh token |
| `Backend/models.py` | Modify | Fix duplicate column, add user_id to Recipe, add RefreshToken model |
| `Backend/schemas.py` | Modify | Add password validation, refresh token schemas, update Recipe schema |
| `Backend/main.py` | Modify | Auth-protect recipes, JSON instructions, rate limiting, CORS config, fix duplicate endpoint |
| `Backend/database.py` | Modify | Use config for DB URL |
| `Backend/requirements.txt` | Modify | Add python-dotenv, slowapi |
| `Backend/migrate_recipes_user.py` | Create | Migration script: add user_id to recipes table |
| `Backend/migrate_instructions_json.py` | Create | Migration script: convert pipe-delimited instructions to JSON |
| `Mobile/services/auth.ts` | Modify | Add token refresh logic |
| `Mobile/services/api.ts` | Modify | Auto-refresh on 401 |
| `Mobile/types/index.ts` | Modify | Add user_id to Recipe type |
| `.gitignore` | Modify | Add .env to gitignore |

---

## Chunk 1: Configuration & Critical Bug Fixes

### Task 1: Environment Configuration

**Files:**
- Create: `Backend/.env`
- Create: `Backend/.env.example`
- Create: `Backend/config.py`
- Modify: `Backend/requirements.txt`
- Modify: `.gitignore`

- [ ] **Step 1: Add python-dotenv and slowapi to requirements.txt**

```
fastapi
uvicorn
sqlalchemy
pydantic
python-multipart
python-jose[cryptography]
passlib[bcrypt]
bcrypt==3.2.0
recipe-scrapers
python-dotenv
slowapi
```

- [ ] **Step 2: Create .env file with actual secrets**

```env
SECRET_KEY=<generate-a-64-char-random-hex-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./gustovify.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8081,http://127.0.0.1:8000
ENVIRONMENT=development
```

- [ ] **Step 3: Create .env.example (no secrets)**

```env
SECRET_KEY=change-me-to-a-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./gustovify.db
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
ENVIRONMENT=development
```

- [ ] **Step 4: Create config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-dev-only-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gustovify.db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
```

- [ ] **Step 5: Add .env to .gitignore**

Append `Backend/.env` to `.gitignore` if not already present.

- [ ] **Step 6: Update database.py to use config**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 7: Install new dependencies**

Run: `cd Backend && pip install python-dotenv slowapi`

---

### Task 2: Fix Critical Bugs in models.py

**Files:**
- Modify: `Backend/models.py:117-118` (duplicate hashed_password)

- [ ] **Step 1: Remove duplicate hashed_password line**

In `Backend/models.py`, the User class has:
```python
hashed_password = Column(String)
hashed_password = Column(String)  # DELETE THIS LINE
```

Remove the second `hashed_password = Column(String)` on line 118.

---

### Task 3: Fix Duplicate Endpoint in main.py

**Files:**
- Modify: `Backend/main.py:486-501` (duplicate /users/me GET)

- [ ] **Step 1: Remove the first /users/me GET endpoint (lines 486-488)**

The endpoint at line 486 (`def read_users_me`) is a duplicate of the one at line 499 (`async def read_users_me`). Remove the first one (lines 486-488) since the second one is under the correct "Kullanıcı" tag.

---

## Chunk 2: Auth Hardening

### Task 4: Update auth.py — Config, Datetime Fix, Refresh Tokens

**Files:**
- Modify: `Backend/auth.py`
- Modify: `Backend/models.py` (add RefreshToken model)
- Modify: `Backend/schemas.py` (add token schemas)

- [ ] **Step 1: Add RefreshToken model to models.py**

Add after the User class:

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(Date)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User")
```

- [ ] **Step 2: Add refresh token schemas to schemas.py**

```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str
```

- [ ] **Step 3: Add password validation to UserCreate in schemas.py**

```python
from pydantic import BaseModel, field_validator

class UserCreate(UserBase):
    password: str
    allergen_ids: Optional[List[int]] = []
    preference_ids: Optional[List[int]] = []

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not any(c.isupper() for c in v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not any(c.isdigit() for c in v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v
```

- [ ] **Step 4: Rewrite auth.py with config, datetime fix, and refresh tokens**

```python
import secrets
from datetime import datetime, timedelta, timezone
from typing import Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas, database, config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_refresh_token(user_id: int, db: Session) -> str:
    token = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = models.RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at.date(),
        is_revoked=False
    )
    db.add(db_token)
    db.commit()
    return token

def verify_refresh_token(token: str, db: Session) -> models.User:
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token,
        models.RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Geçersiz refresh token")
    if db_token.expires_at < datetime.now(timezone.utc).date():
        db_token.is_revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token süresi dolmuş")
    return db.query(models.User).filter(models.User.id == db_token.user_id).first()

def revoke_refresh_token(token: str, db: Session):
    db_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama başarısız",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
```

---

### Task 5: Update Login Endpoint & Add Refresh Endpoint in main.py

**Files:**
- Modify: `Backend/main.py` (login endpoint, add /auth/refresh)

- [ ] **Step 1: Update login endpoint to return refresh token**

```python
@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Kimlik Doğrulama"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
```

- [ ] **Step 2: Add /auth/refresh endpoint**

```python
@app.post("/auth/refresh", response_model=schemas.TokenResponse, tags=["Kimlik Doğrulama"])
def refresh_access_token(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    user = auth.verify_refresh_token(request.refresh_token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz refresh token")
    # Revoke old, issue new
    auth.revoke_refresh_token(request.refresh_token, db)
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = auth.create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
```

- [ ] **Step 3: Add /auth/logout endpoint**

```python
@app.post("/auth/logout", tags=["Kimlik Doğrulama"])
def logout(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    auth.revoke_refresh_token(request.refresh_token, db)
    return {"message": "Çıkış yapıldı"}
```

---

## Chunk 3: Recipe Ownership & Auth Protection

### Task 6: Add user_id to Recipe Model

**Files:**
- Modify: `Backend/models.py` (Recipe model)
- Modify: `Backend/schemas.py` (Recipe schema)
- Create: `Backend/migrate_recipes_user.py`

- [ ] **Step 1: Add user_id to Recipe model**

```python
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    instructions = Column(String)  # Will be JSON string
    servings = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    owner = relationship("User")
```

Note: `nullable=True` for backward compatibility with existing recipes. Also added `cascade="all, delete-orphan"` so deleting a recipe auto-deletes its ingredients.

- [ ] **Step 2: Update Recipe schema to include user_id**

In schemas.py, update the Recipe response schema:

```python
class Recipe(RecipeBase):
    id: int
    user_id: Optional[int] = None
    ingredients: List[Ingredient]

    class Config:
        from_attributes = True
```

- [ ] **Step 3: Create migration script for user_id on recipes**

Create `Backend/migrate_recipes_user.py`:

```python
"""Add user_id column to recipes table."""
import sqlite3

def migrate():
    conn = sqlite3.connect("gustovify.db")
    cursor = conn.cursor()
    # Check if column exists
    cursor.execute("PRAGMA table_info(recipes)")
    columns = [col[1] for col in cursor.fetchall()]
    if "user_id" not in columns:
        cursor.execute("ALTER TABLE recipes ADD COLUMN user_id INTEGER REFERENCES users(id)")
        conn.commit()
        print("user_id column added to recipes table.")
    else:
        print("user_id column already exists.")
    conn.close()

if __name__ == "__main__":
    migrate()
```

- [ ] **Step 4: Run migration**

Run: `cd Backend && python migrate_recipes_user.py`

---

### Task 7: Auth-Protect All Recipe Endpoints

**Files:**
- Modify: `Backend/main.py` (all /recipes/ endpoints)

- [ ] **Step 1: Update create_recipe to require auth and set user_id**

```python
@app.post("/recipes/", response_model=schemas.Recipe, tags=["Tarif İşlemleri"])
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = models.Recipe(
        title=recipe.title,
        instructions="|".join(recipe.instructions),
        servings=recipe.servings,
        user_id=current_user.id
    )
    # ... rest stays same
```

- [ ] **Step 2: Update get_recipes to filter by current user**

```python
@app.get("/recipes/", response_model=List[schemas.Recipe], tags=["Tarif İşlemleri"])
def get_recipes(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipes = db.query(models.Recipe).filter(models.Recipe.user_id == current_user.id).all()
    for r in recipes:
        r.instructions = r.instructions.split("|")
    return recipes
```

- [ ] **Step 3: Update update_recipe with auth + ownership check**

```python
@app.put("/recipes/{recipe_id}", response_model=schemas.Recipe, tags=["Tarif İşlemleri"])
def update_recipe(recipe_id: int, recipe_update: schemas.RecipeUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
    # ... rest stays same
```

- [ ] **Step 4: Update delete_recipe with auth + ownership check**

```python
@app.delete("/recipes/{recipe_id}", tags=["Tarif İşlemleri"])
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    db_recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı")
    db.delete(db_recipe)
    db.commit()
    return {"message": f"ID'si {recipe_id} olan tarif başarıyla silindi"}
```

- [ ] **Step 5: Update scale endpoint with auth**

```python
@app.get("/recipes/{recipe_id}/scale/{target_servings}", tags=["Tarif İşlemleri"])
def get_scaled_recipe(recipe_id: int, target_servings: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipe = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.user_id == current_user.id
    ).first()
    # ... rest stays same
```

- [ ] **Step 6: Update scrape endpoint with auth**

```python
@app.post("/recipes/scrape", response_model=schemas.ScrapeResponse, tags=["Scraper"])
def scrape_recipe(request: schemas.ScrapeRequest, current_user: models.User = Depends(auth.get_current_user)):
    # ... same logic
```

---

## Chunk 4: Instructions JSON, Rate Limiting, CORS

### Task 8: Convert Instructions Storage to JSON

**Files:**
- Modify: `Backend/main.py` (all instruction read/write points)
- Create: `Backend/migrate_instructions_json.py`

- [ ] **Step 1: Create migration script**

Create `Backend/migrate_instructions_json.py`:

```python
"""Convert pipe-delimited instructions to JSON format."""
import sqlite3
import json

def migrate():
    conn = sqlite3.connect("gustovify.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, instructions FROM recipes")
    rows = cursor.fetchall()
    for row_id, instructions in rows:
        if instructions and not instructions.startswith("["):
            steps = [s.strip() for s in instructions.split("|") if s.strip()]
            cursor.execute(
                "UPDATE recipes SET instructions = ? WHERE id = ?",
                (json.dumps(steps, ensure_ascii=False), row_id)
            )
    conn.commit()
    print(f"Migrated {len(rows)} recipes to JSON instructions.")
    conn.close()

if __name__ == "__main__":
    migrate()
```

- [ ] **Step 2: Run migration**

Run: `cd Backend && python migrate_instructions_json.py`

- [ ] **Step 3: Update all instruction serialization in main.py**

Replace all `"|".join(recipe.instructions)` with `json.dumps(recipe.instructions, ensure_ascii=False)`.

Replace all `.instructions.split("|")` with `json.loads(r.instructions)`.

Add `import json` at top of main.py.

Affected locations:
- `create_recipe`: line 70 (write) and line 97 (read)
- `get_recipes`: line 105 (read)
- `update_recipe`: line 185 (write) and line 210 (read)
- `suggest_recipes`: line 392 (read)

---

### Task 9: Add Rate Limiting

**Files:**
- Modify: `Backend/main.py`

- [ ] **Step 1: Add rate limiter setup to main.py**

Add at top of main.py after imports:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

- [ ] **Step 2: Apply rate limits to sensitive endpoints**

Add `@limiter.limit("5/minute")` to:
- `/auth/login`
- `/auth/register`
- `/auth/refresh`

Add `@limiter.limit("10/minute")` to:
- `/recipes/scrape`

Note: These decorators go AFTER the `@app.post()` decorator, and the endpoint function must accept a `request: Request` parameter. Import `from fastapi import Request`.

Example:
```python
@app.post("/auth/login", response_model=schemas.TokenResponse, tags=["Kimlik Doğrulama"])
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ...
```

---

### Task 10: Configure CORS Properly

**Files:**
- Modify: `Backend/main.py`

- [ ] **Step 1: Replace wildcard CORS with config-based origins**

```python
import config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Chunk 5: Mobile App Updates

### Task 11: Update Mobile Auth to Support Refresh Tokens

**Files:**
- Modify: `Mobile/services/auth.ts`
- Modify: `Mobile/services/api.ts`
- Modify: `Mobile/types/index.ts`

- [ ] **Step 1: Update auth.ts to store refresh token**

```typescript
export const authService = {
    login: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString(),
        });

        if (!response.ok) throw new Error('Giriş başarısız');

        const data = await response.json();
        await Storage.setItem('token', data.access_token);
        await Storage.setItem('refreshToken', data.refresh_token);
        return data;
    },

    register: async (email: string, password: string) => {
        return api.post('/auth/register', { email, password });
    },

    logout: async () => {
        const refreshToken = await Storage.getItem('refreshToken');
        if (refreshToken) {
            try {
                await api.post('/auth/logout', { refresh_token: refreshToken });
            } catch (_) { /* ignore logout errors */ }
        }
        await Storage.deleteItem('token');
        await Storage.deleteItem('refreshToken');
    },

    refreshToken: async (): Promise<string | null> => {
        const refreshToken = await Storage.getItem('refreshToken');
        if (!refreshToken) return null;

        try {
            const response = await fetch(`${API_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });
            if (!response.ok) return null;

            const data = await response.json();
            await Storage.setItem('token', data.access_token);
            await Storage.setItem('refreshToken', data.refresh_token);
            return data.access_token;
        } catch {
            return null;
        }
    }
};
```

- [ ] **Step 2: Update api.ts to auto-refresh on 401**

```typescript
async function handleResponse(response: Response) {
    if (response.status === 401) {
        // Try to refresh the token
        const { authService } = await import('./auth');
        const newToken = await authService.refreshToken();
        if (newToken) {
            // Retry the original request with the new token
            const retryResponse = await fetch(response.url, {
                method: response.type,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${newToken}`,
                },
            });
            if (retryResponse.ok) return retryResponse.json();
        }
        // If refresh fails, throw auth error
        throw new Error('Oturum süresi doldu, lütfen tekrar giriş yapın');
    }
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Bir hata oluştu');
    }
    return response.json();
}
```

- [ ] **Step 3: Add user_id to Recipe type in types/index.ts**

```typescript
export interface Recipe {
    id: number;
    title: string;
    instructions: string[];
    servings: number;
    ingredients: RecipeIngredient[];
    user_id?: number;
}
```

---

## Execution Order

1. Task 1 (Environment config) — foundation for everything else
2. Task 2 (Fix duplicate column) — critical bug
3. Task 3 (Fix duplicate endpoint) — critical bug
4. Task 4 (Auth hardening) — depends on Task 1
5. Task 5 (Login/refresh endpoints) — depends on Task 4
6. Task 6 (Recipe user_id) — depends on Task 1
7. Task 7 (Auth-protect recipes) — depends on Task 4 + 6
8. Task 8 (JSON instructions) — independent, can run after Task 1
9. Task 9 (Rate limiting) — depends on Task 1
10. Task 10 (CORS config) — depends on Task 1
11. Task 11 (Mobile updates) — depends on Task 5
