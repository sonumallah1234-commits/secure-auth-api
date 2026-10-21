# FastAPI JWT MySQL

A local-only FastAPI project that uses SQLAlchemy, Alembic, and MySQL to build authentication and user management features.

## Documentation

Detailed project documentation is maintained under [`docs/`](docs/):

- [Project Overview](docs/PROJECT.md) — what the project is, why it exists, goals, and scope.
- [Architecture](docs/ARCHITECTURE.md) — application structure and authentication flow.
- [Features](docs/FEATURES.md) — current application capabilities.
- [API Reference](docs/API.md) — endpoint overview and API documentation.
- [Database](docs/DATABASE.md) — MySQL, SQLAlchemy, and Alembic guidance.
- [Development Guide](docs/DEVELOPMENT.md) — branches, Pull Requests, testing, and development rules.
- [Changelog](docs/CHANGELOG.md) — tracked project changes and automated PR documentation.

## What is included

- FastAPI application
- MySQL connection through SQLAlchemy
- Alembic migrations
- User registration
- Login with JWT access tokens
- Protected profile endpoint
- Forgot password and reset password flow
- User CRUD with role-based authorization
- Automated tests

## Project structure

```text
fastapi-jwt-mysql/
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── database.py
│   └── main.py
├── alembic/
├── docs/
├── tests/
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python
- MySQL Server
- MySQL Workbench, optional
- A virtual environment named `venv`

## 1. Create and activate the virtual environment

From the project root on Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

If your project already has `venv`, just activate it.

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure environment variables

Create a `.env` file in the project root if it does not already exist.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fastapi_auth
DB_USER=root
DB_PASSWORD=your_password
JWT_SECRET=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
RESET_TOKEN_EXPIRE_MINUTES=15
```

You can copy `.env.example` and fill in your own values.

## 4. Create the MySQL database

Create a database in MySQL first:

```sql
CREATE DATABASE fastapi_auth;
```

Make sure the name matches `DB_NAME` in `.env`.

## 5. Run Alembic migrations

The database schema is managed through Alembic.

Generate a migration if the model changes:

```powershell
alembic revision --autogenerate -m "message here"
```

Apply migrations:

```powershell
alembic upgrade head
```

Check migration history:

```powershell
alembic current
alembic history
```

## 6. Start the API server

Run the app with Uvicorn:

```powershell
uvicorn app.main:app --reload
```

Open these in your browser:

- API docs: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Root check: http://127.0.0.1:8000/
- Database test: http://127.0.0.1:8000/db-test

## 7. How to use the API

## Password security

Passwords are never stored directly in MySQL.

Flow:

```text
User password
  ↓
bcrypt hash
  ↓
MySQL
```

The app uses `passlib[bcrypt]` through `app/core/security.py`.

### Register a user

POST `/api/auth/register`

Example body:

```json
{
  "username": "vaibhav",
  "email": "vaibhav@example.com",
  "password": "Password@123"
}
```

### Login

POST `/api/auth/login`

Example body:

```json
{
  "username_or_email": "vaibhav",
  "password": "Password@123"
}
```

Response includes an access token:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Use the token

You have two options:

1. Use the JSON login endpoint above, copy the token, then click Authorize in Swagger and paste:

```text
Bearer your_access_token
```

2. Or use Swagger's built-in OAuth2 login:

  - Open `/docs`
  - Click `Authorize`
  - Enter your username and password
  - Swagger will call `POST /api/auth/token` automatically

### Get current user

GET `/api/auth/me`

Requires a valid JWT token.

### Forgot password

POST `/api/auth/forgot-password`

Example body:

```json
{
  "email": "vaibhav@example.com"
}
```

### Reset password

POST `/api/auth/reset-password`

Example body:

```json
{
  "token": "reset-token-here",
  "new_password": "NewPassword@123"
}
```

### User CRUD

- GET `/api/users`
- POST `/api/users`
- GET `/api/users/{user_id}`
- PUT `/api/users/{user_id}`
- DELETE `/api/users/{user_id}`

Admin access is required for listing all users and creating users through the user router.

## 8. Run tests

```powershell
pytest -q
```

The test suite uses an isolated SQLite test database.

## 9. Common workflow

1. Update the SQLAlchemy model in `app/models/user.py`
2. Generate a migration with Alembic
3. Apply the migration
4. Update schemas or routes if needed
5. Run tests

## 10. Git workflow

The `main` branch is the protected production branch. **Do not make changes directly on `main`.**

Every feature or fix should be developed in its own branch and merged through a Pull Request.

### Create a feature branch

First make sure your local `main` is up to date:

```powershell
git checkout main
git pull origin main
```

Create a feature branch:

```powershell
git checkout -b feature/<short-description>
```

Examples:

```powershell
git checkout -b feature/logout
```

```powershell
git checkout -b feature/password-validation
```

### Make your changes

Implement the task and test it locally.

Check your changes:

```powershell
git status
git diff
```

Run tests:

```powershell
pytest -q
```

### Commit your changes

Use a clear commit message:

```powershell
git add .
git commit -m "feat: add logout"
```

### Push the feature branch

```powershell
git push -u origin feature/logout
```

### Create a Pull Request

After pushing the branch:

1. Open the GitHub repository.
2. GitHub will show an option to create a Pull Request for the pushed branch.
3. Set the base branch to `main`.
4. Add a clear PR title and description.
5. Link the related GitHub issue, for example `Closes #14`.
6. Submit the Pull Request.

Example PR title:

```text
feat: add logout and token invalidation
```

### Pull Request checklist

Before merging, verify:

- [ ] Code is complete
- [ ] Tests pass
- [ ] No `.env` or secrets are committed
- [ ] Alembic migration is included if the database changed
- [ ] PR description explains the change
- [ ] Related issue is linked

### Merge the Pull Request

Only merge the PR into `main` after the changes have been reviewed and checks have passed.

After merging:

```powershell
git checkout main
git pull origin main
git branch -d feature/logout
```

The feature branch can also be deleted from GitHub after the PR is merged.

### Branch workflow

```text
main
 │
 ├── feature/logout
 │       │
 │       ├── code changes
 │       ├── tests
 │       └── push
 │              │
 │              ▼
 │         Pull Request
 │              │
 │         review + checks
 │              │
 │              ▼
 │            main
```

### Recommended branch names

Use a small, descriptive prefix:

```text
feature/<name>     # New functionality
fix/<name>         # Bug fix
refactor/<name>    # Code refactoring
test/<name>        # Tests
chore/<name>       # Maintenance/documentation
```

Examples:

```text
feature/logout
feature/refresh-token
fix/login-validation
refactor/auth-service
test/authentication
chore/update-readme
```

## 11. Notes

- Do not edit the database schema manually.
- Use Alembic for every schema change.
- The project currently runs on the existing Python environment in `venv`.

## Useful commands

```powershell
venv\Scripts\activate
pip install -r requirements.txt
alembic revision --autogenerate -m "create users table"
alembic upgrade head
uvicorn app.main:app --reload
pytest -q
```

## Current status

- FastAPI project setup: done
- MySQL connection: done
- Environment config: done
- Database dependency: done
- User model: done
- Alembic setup: done
- First migration: done
- Schemas, auth, JWT, CRUD, roles, and tests: done


