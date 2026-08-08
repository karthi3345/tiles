import os

# Only install the PyMySQL shim when we're on MySQL (Drytis dev workspace).
# On Vercel / Neon (Postgres via DATABASE_URL), this must NOT run.
if not os.environ.get("DATABASE_URL"):
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
