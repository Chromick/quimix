from app.infrastructure.database import _turso_sqlalchemy_url


def test_libsql_url_becomes_sqlalchemy_dialect():
    url = _turso_sqlalchemy_url("libsql://quimix-auth-org.turso.io")
    assert url == "sqlite+libsql://quimix-auth-org.turso.io?secure=true"


def test_https_url_becomes_libsql_dialect():
    url = _turso_sqlalchemy_url("https://quimix-auth-org.turso.io")
    assert url == "sqlite+libsql://quimix-auth-org.turso.io?secure=true"


def test_secure_flag_is_not_duplicated():
    url = _turso_sqlalchemy_url("libsql://quimix-auth-org.turso.io?secure=true")
    assert url.count("secure=") == 1
