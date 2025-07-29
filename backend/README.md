# SeatSync Backend

## Developer Quickstart

### Dependency Management
- Use Poetry for all dependencies:
  - `poetry install` to install
  - `poetry add <package>` to add
  - `poetry export -f requirements.txt --output requirements.txt` if you need a requirements.txt

### Database Migrations
- Use Alembic for migrations:
  - `poetry run alembic revision --autogenerate -m "message"` to create a migration
  - `poetry run alembic upgrade head` to apply migrations

### Testing
- Use pytest:
  - `poetry run pytest`

### Developer Mode
- If `DEV_MODE` env var is set, authentication is bypassed and you are always superuser.

### Environment Variables
- Use `.env` for local development. In production, set variables in Railway.

---

(Existing README content below...) 