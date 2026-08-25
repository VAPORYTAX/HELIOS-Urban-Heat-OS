from app.config import Settings


def test_railway_postgresql_url_uses_psycopg3():
    settings = Settings(database_url="postgresql://user:pass@db.internal:5432/helios")

    assert settings.database_url == "postgresql+psycopg://user:pass@db.internal:5432/helios"


def test_explicit_psycopg_url_is_unchanged():
    url = "postgresql+psycopg://user:pass@db.internal:5432/helios"

    assert Settings(database_url=url).database_url == url
