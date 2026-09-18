# Imports #


from pathlib import Path
import re as regex
from zipfile import ZipFile, ZIP_DEFLATED

# Functions #


def handle_function(function):
    """
    This function safely calls and handles the provided `function` from `KeyboardInterrupt` errors.
    """
    try:
        function()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")


def custom_input(input_type=None):
    """
    This function returns an input with an optional `input_type` parameter.

    `input_type`: What characters are available to input. The following options are available:
    - `"custom"`
    - `"confirmation"`
    - `None`
    """
    if input_type and input_type != None:
        valid_input = False

        while not valid_input:
            user_input = input("> ")

            if (
                input_type == "custom"
                and len(user_input) <= 10
                and regex.match(
                    "([0-9]+)\\.([0-9]+?)\\.([0-9]+?)|([0-9]+)\\.([0-9]+?)", user_input
                )
            ):
                valid_input = True
            elif input_type == "confirmation" and user_input.lower() in [
                "y",
                "yes",
                "n",
                "no",
            ]:
                valid_input = True
    else:
        user_input = input("> ")
    if user_input and not user_input.isspace():
        return user_input


def ask(question, confirm=False, input_type=None):
    """
    This function asks the user a `question` with optional `confirm` and `input_type` parameters and returns the following:
    - `valid_input` (boolean)
    - `input_value` (input)

    `input_type`: What characters are available to input. The following options are available:
    - `"custom"`
    - `"confirmation"`
    - `None`
    """
    valid_input = False

    while not valid_input:
        print(question)

        input_value = custom_input((input_type or None))

        if confirm:
            valid_answer = False

            while not valid_answer:
                print(f"\nYou entered '{input_value}'. Is that correct? (Y/N)")

                confirm_input = custom_input("confirmation").lower()

                if confirm_input in ["y", "yes"]:
                    valid_answer = True
                    valid_input = True
                elif confirm_input in ["n", "no"]:
                    valid_answer = True
                    valid_input = False
        else:
            valid_input = True
    return valid_input, input_value


def list_directory(directory, filtered=False):
    """
    This function lists the files in the provided `directory` parameter with an optional `filtered` parameter.
    """
    listed_files = []

    if any(directory.iterdir()):
        for file in directory.iterdir():
            insensitive_file = file.name.lower()

            if file.name.startswith("."):
                continue
            if filtered:
                if file.is_file() and not insensitive_file.endswith(".md"):
                    listed_files.append(file.name)
                elif file.is_dir() and not insensitive_file in ["images", "projects"]:
                    listed_files.append(file.name)
            else:
                if file.is_dir():
                    listed_files.append(file.name)
    return listed_files


def filter_directory(directory):
    """
    This function filters out unnecessary files in the provided `directory` parameter.
    """
    filtered_files = []

    if any(directory.iterdir()):
        for file in directory.iterdir():
            insensitive_file = file.name.lower()

            if file.is_dir() and not insensitive_file in ["images", "projects"]:
                filtered_files.extend(filter_directory(file))
            elif file.is_file() and not insensitive_file.endswith(".md"):
                filtered_files.append(file)
    return filtered_files


def main():
    current_directory = Path(__file__).parent
    parent_directory = current_directory.parent

    if any(current_directory.iterdir()):
        addon_directories = list_directory(current_directory)

        for addon in addon_directories:
            addon_path = current_directory / addon

            print(f"├ Add-on found: {addon}")

            resolution_directories = list_directory(addon_path)

            for index, resolution in enumerate(resolution_directories):
                resolution_path = addon_path / resolution

                resolution_message = f"Resolution found: {resolution}"
                files_message = (
                    f"Files included: {list_directory(resolution_path, True)}"
                )

                if len(resolution_directories) == 1:
                    print(f"└─┬ {resolution_message}")
                    print(f"  └── {files_message}\n")
                elif index == 0:
                    print(f"└─┬ {resolution_message}")
                    print(f"  ├── {files_message}")
                elif index >= 1 and index < (len(resolution_directories) - 1):
                    print(f"  ├ {resolution_message}")
                    print(f"  ├── {files_message}")
                else:
                    print(f"  ├ {resolution_message}")
                    print(f"  └── {files_message}\n")
        valid_version, version_input = ask(
            "Enter the Minecraft version to package", True, "custom"
        )

        if valid_version:
            packaged_directory = parent_directory / "packaged_files"
            packaged_directory.mkdir(exist_ok=True)

            print("\nPackaging add-ons...\n")

            for addon_directory in addon_directories:
                addon_path = current_directory / addon_directory

                resolution_directories = list_directory(addon_path)

                for resolution_directory in resolution_directories:
                    resolution_path = addon_path / resolution_directory

                    filtered_files = filter_directory(resolution_path)

                    package_name = (
                        f"{addon_directory}_{resolution_directory}_{version_input}.zip"
                    )

                    package_path = packaged_directory / package_name

                    relative_path = Path("..") / package_path.relative_to(
                        parent_directory
                    )

                    with ZipFile(
                        package_path, "w", ZIP_DEFLATED, strict_timestamps=False
                    ) as new_package:
                        for file in filtered_files:
                            archive_name = file.relative_to(resolution_path)

                            new_package.write(file, archive_name, ZIP_DEFLATED)
                    print(f"Packaged '{relative_path}'")
    else:
        print("No add-ons found!")
    input("\nPress any key to exit...")


# Main #


if __name__ == "__main__":
    handle_function(main)
