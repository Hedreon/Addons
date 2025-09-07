# Imports #


from pathlib import Path
import re as regex
from zipfile import ZipFile, ZIP_DEFLATED

# Functions #


def handle_function(function):
    "This function safely calls and handles the provided function from KeyboardInterrupt errors."
    try:
        function()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")


def custom_input(input_type=None):
    """
    This function returns an input function with an optional input_type parameter.

    input_type: What characters are available to input. Available are the following options:

        "custom"
        "confirmation"
        None
    """
    if input_type and input_type != None:
        valid_input = False

        while not valid_input:
            user_input = input("> ")

            if (
                input_type == "custom"
                and len(user_input) <= 10
                and regex.match("([0-9]+?).([0-9]+?).([0-9]+)", user_input)
            ):
                valid_input = True
            elif input_type == "confirmation" and user_input.lower() in [
                "y",
                "yes",
                "n",
                "no"
            ]:
                valid_input = True
    else:
        user_input = input("> ")
    if user_input and not user_input.isspace():
        return user_input


def ask(question, confirm=False, input_type=None):
    """
    This function asks the user a question with optional confirm and input_type parameters and returns the following:

        valid_input (bool)
        input_value (input)

    input_type: What characters are available to input. Available are the following options:

        "custom"
        "confirmation"
        None
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
    "This function lists the nodes in the provided directory parameter with an optional filtered parameter."
    listed_nodes = []

    if any(directory.iterdir()):
        for node in directory.iterdir():
            insensitive_node = node.name.lower()

            if node.name.startswith("."):
                continue
            if filtered:
                if node.is_file() and not insensitive_node.endswith(".md"):
                    listed_nodes.append(node.name)
                elif node.is_dir() and not insensitive_node in ["images", "projects"]:
                    listed_nodes.append(node.name)
            else:
                if node.is_dir():
                    listed_nodes.append(node.name)
    return listed_nodes


def filter_directory(directory):
    "This function filters out unnecessary files in the provided directory parameter."
    filtered_nodes = []

    if any(directory.iterdir()):
        for node in directory.iterdir():
            insensitive_node = node.name.lower()

            if node.is_dir() and not insensitive_node in ["images", "projects"]:
                filtered_nodes.extend(filter_directory(node))
            elif node.is_file() and not insensitive_node.endswith(".md"):
                filtered_nodes.append(node)
    return filtered_nodes


def main():
    working_directory = Path.cwd()

    if any(working_directory.iterdir()):
        addon_directories = list_directory(working_directory)

        for addon in addon_directories:
            addon_path = Path(f"{working_directory}\\{addon}")

            print(f"Add-on found: {addon}")

            resolution_directories = list_directory(addon_path)

            for resolution in resolution_directories:
                resolution_path = Path(f"{addon_path}\\{resolution}")

                print(f"\tResolution found: {resolution}")
                print(f"\tFiles included: {list_directory(resolution_path, True)}\n")
        valid_version, version_input = ask(
            "Which Minecraft version do you want to pack?", True, "custom"
        )

        if valid_version:
            print("\nPacking add-ons...\n")

            for addon_directory in addon_directories:
                addon_path = Path(f"{working_directory}\\{addon_directory}")

                resolution_directories = list_directory(addon_path)

                for resolution_directory in resolution_directories:
                    resolution_path = Path(f"{addon_path}\\{resolution_directory}")

                    filtered_files = filter_directory(resolution_path)

                    pack_name = (
                        f"{addon_directory}-{resolution_directory}-{version_input}.zip"
                    )

                    with ZipFile(
                        pack_name, "w", ZIP_DEFLATED, strict_timestamps=False
                    ) as new_pack:
                        for file in filtered_files:
                            archive_name = file.relative_to(resolution_path)

                            new_pack.write(file, archive_name, ZIP_DEFLATED)
                    print(f"Packed {pack_name}!")
    else:
        print("No add-ons found!")
    input("\nPress any key to exit...")


# Main #


if __name__ == "__main__":
    handle_function(main)
