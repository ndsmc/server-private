import shutil
import argparse
import re
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def write_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)


def handle_error(message):
    logger.error(message)
    raise ValueError(message)


def parse_mc_env(env_file):
    path_variables = {}
    with open(env_file, "r") as f:
        current_path = None
        for line in f:
            if line.startswith("mc-path"):
                path_key, path_value = line.strip().split("=", 1)
                current_path = path_value.strip()
                path_variables[current_path] = []
            elif line.startswith("mc-") and current_path is not None:
                var_key, var_value = line.strip().split("=", 1)
                path_variables[current_path].append(
                    (var_key.strip(), var_value.strip())
                )
    return path_variables


def remove_backticks(value):
    return re.sub(r"`([^`]*)`", r"\1", value)


def replace_values_in_files(path_variables, reverse=False):
    for path, variables in path_variables.items():
        path = Path(path)
        if not path.exists():
            handle_error(f"File {path} does not exist.")
        content = read_file(path)
        for var_key, var_value in variables:
            placeholder = f"${{{var_key}}}"
            if reverse:
                content = re.sub(
                    re.escape(remove_backticks(var_value)), placeholder, content
                )
            else:
                content = re.sub(
                    re.escape(placeholder), remove_backticks(var_value), content
                )
        write_file(path, content)
        action = "Restored" if reverse else "Replaced"
        logger.info(f"{action} values in file {path}.")


def initialize_env(env_file):
    env_file = Path(env_file)
    if env_file.exists():
        handle_error(
            f"File {env_file} already exists. Use another file or delete the existing one."
        )
    with open(env_file, "w") as f:
        f.write("# Path settings for Minecraft\n")
        f.write("mc-path=file_path\n")
        f.write("# Example variables for replacement\n")
        f.write("# mc-variable=value\n")
    logger.info("Initialized .env file.")


def create_temp_env(env_file):
    env_file_path = Path(env_file)
    temp_env_file = env_file_path.with_name(f".tmp{env_file_path.name}")
    shutil.copyfile(env_file_path, temp_env_file)
    logger.info(f"Temporary file created: {temp_env_file}")
    return temp_env_file


def rename_temp_env(temp_env_file):
    temp_env_file_path = Path(temp_env_file)
    if temp_env_file_path.exists():
        new_path = temp_env_file_path.with_suffix(".env.bak")
        temp_env_file_path.rename(new_path)
        logger.info(f"Temporary file {temp_env_file_path} renamed to {new_path}.")
        return new_path
    else:
        logger.error(f"Temporary file {temp_env_file_path} not found.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Replace values in target files with values from the .env file."
    )
    parser.add_argument("env_file", help="Path to the .env file")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize the .env file with example variables",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Reverse the replacement (restore original values)",
    )
    args = parser.parse_args()

    if args.init:
        initialize_env(args.env_file)
    elif args.reverse:
        env_file_path = Path(args.env_file)
        temp_env_file = env_file_path.with_name(f".tmp{env_file_path.name}")
        try:
            reverse_path_variables = parse_mc_env(temp_env_file)
            replace_values_in_files(reverse_path_variables, reverse=True)
        except Exception as e:
            logger.exception(f"Error during reverse replacement: {e}")
        finally:
            rename_temp_env(temp_env_file)
    else:
        temp_env_file = create_temp_env(args.env_file)
        try:
            path_variables = parse_mc_env(temp_env_file)
            replace_values_in_files(path_variables)
        except Exception as e:
            logger.exception(f"Error during value replacement: {e}")


if __name__ == "__main__":
    main()
