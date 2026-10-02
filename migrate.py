import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    print(f"Starting directory migration in {ROOT}...")

    # 1. Target directories
    frontend_dir = ROOT / "frontend"
    frontend_static = frontend_dir / "static"
    frontend_templates = frontend_dir / "templates"

    backend_dir = ROOT / "backend"
    backend_app = backend_dir / "app"

    config_dir = ROOT / "config"
    docs_dir = ROOT / "docs"

    for d in [frontend_static, frontend_templates, backend_app, config_dir, docs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Backend package init
    backend_init = backend_dir / "__init__.py"
    if not backend_init.exists():
        backend_init.write_text('"""FitBuddy Backend Package."""\n', encoding="utf-8")

    config_init = config_dir / "__init__.py"
    if not config_init.exists():
        config_init.write_text('"""FitBuddy Configuration Package."""\n', encoding="utf-8")

    src_app = ROOT / "app"

    # 2. Copy static and templates to frontend
    src_static = src_app / "static"
    if src_static.exists():
        print("Copying static files to frontend/static...")
        shutil.copytree(src_static, frontend_static, dirs_exist_ok=True)

    src_templates = src_app / "templates"
    if src_templates.exists():
        print("Copying template files to frontend/templates...")
        shutil.copytree(src_templates, frontend_templates, dirs_exist_ok=True)

    # 3. Copy backend modules to backend/app
    backend_items = [
        "ai", "database", "models", "routes", "schemas", "services", "utils",
        "__init__.py", "config.py", "database.py", "dependencies.py", "main.py",
        "models.py", "schemas.py"
    ]

    for item in backend_items:
        src_item = src_app / item
        dst_item = backend_app / item
        if src_item.is_dir():
            print(f"Copying directory {item} to backend/app/{item}...")
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        elif src_item.is_file():
            print(f"Copying file {item} to backend/app/{item}...")
            shutil.copy2(src_item, dst_item)

    # 4. Copy .env.example to config/.env.example
    env_example = ROOT / ".env.example"
    if env_example.exists():
        shutil.copy2(env_example, config_dir / ".env.example")

    print("Migration copy phase complete!")

if __name__ == "__main__":
    main()
