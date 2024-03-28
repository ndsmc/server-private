import os
import argparse
import re


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
                print(var_key, var_value)
                path_variables[current_path].append(
                    (var_key.strip(), var_value.strip())
                )
    return path_variables


def remove_backticks(value):
    return re.sub(r"`([^`]*)`", r"\1", value)


def replace_values_in_files(path_variables, reverse=False):
    for path, variables in path_variables.items():
        if os.path.exists(path):
            with open(path, "r") as file:
                content = file.read()
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
            with open(path, "w") as file:
                file.write(content)
            print(
                f"Значения в файле {path} были успешно {'восстановлены' if reverse else 'заменены'}."
            )
        else:
            print(f"Файл {path} не существует.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Заменить значения в целевых файлах значениями из .env файла."
    )
    parser.add_argument("env_file", help="Путь к .env файлу")
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Обратить замену (восстановить оригинальные значения)",
    )
    args = parser.parse_args()

    print(f"Парсинг файла: {args.env_file}")
    path_variables = parse_mc_env(args.env_file)
    print(f"Найдены следующие пути и переменные: {path_variables}")
    replace_values_in_files(path_variables, reverse=args.reverse)
