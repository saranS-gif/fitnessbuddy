import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def cleanup():
    old_app = ROOT / "app"
    if old_app.exists():
        print(f"Removing old app folder: {old_app}")
        shutil.rmtree(old_app)

    migrate_script = ROOT / "migrate.py"
    if migrate_script.exists():
        print(f"Removing migrate script: {migrate_script}")
        migrate_script.unlink()

    print("Cleanup completed successfully.")

if __name__ == "__main__":
    cleanup()
