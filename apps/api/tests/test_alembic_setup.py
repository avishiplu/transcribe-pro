from pathlib import Path

from alembic.config import Config


def test_alembic_files_exist():
    root = Path(__file__).resolve().parents[1]

    assert (root / "alembic.ini").exists()
    assert (root / "alembic" / "env.py").exists()
    assert (root / "alembic" / "script.py.mako").exists()
    assert (root / "alembic" / "versions").exists()


def test_alembic_config_points_to_alembic_folder():
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "alembic.ini"))

    assert config.get_main_option("script_location") == "alembic"
