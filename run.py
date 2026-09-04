from app.utils.logger import setup_logging


def main() -> None:
    setup_logging()

    print("=" * 60)
    print("ADK-Ollama-AgentHub")
    print("=" * 60)
    print("Environment initialized successfully.")
    print("Use 'adk web' to start the ADK development UI.")
    print("=" * 60)


if __name__ == "__main__":
    main()