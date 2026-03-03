import argparse
import os

try:
    from .agent import run
except Exception:
    from agent import run


def main():
    parser = argparse.ArgumentParser(prog="bjtupubclaw")
    parser.add_argument("--config", dest="config", default=None)
    parser.add_argument("--env", dest="env_file", default=None, help="Path to .env file")
    args = parser.parse_args()
    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file
    run(config_path=args.config)


if __name__ == "__main__":
    main()
