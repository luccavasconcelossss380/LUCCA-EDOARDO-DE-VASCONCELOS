def main():
    """Atalho opcional: uv run python main.py."""
    from pathlib import Path
    from streamlit.web import cli
    import sys
    sys.argv = ["streamlit", "run", str(Path(__file__).with_name("app.py")), "--server.address", "127.0.0.1"]
    cli.main()


if __name__ == "__main__":
    main()
