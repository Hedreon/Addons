# Imports #


import json
from pathlib import Path
from urllib.request import Request, urlopen

# Variables #


BLOCKS = {
    "ORE_BORDERS": {
        "64X": {
            "ORES": [
                "ancient_debris_side",
                "ancient_debris_top",
                "coal_ore",
                "copper_ore",
                "deepslate_coal_ore",
                "deepslate_copper_ore",
                "deepslate_diamond_ore",
                "deepslate_emerald_ore",
                "deepslate_gold_ore",
                "deepslate_iron_ore",
                "deepslate_lapis_ore",
                "deepslate_redstone_ore",
                "diamond_ore",
                "emerald_ore",
                "gilded_blackstone",
                "gold_ore",
                "iron_ore",
                "lapis_ore",
                "nether_gold_ore",
                "nether_quartz_ore",
                "redstone_ore",
            ],
            "BORDERS": [
                "lava_still",
                "coal_block",
                "raw_copper_block",
                "diamond_block",
                "emerald_block",
                "raw_gold_block",
                "raw_iron_block",
                "lapis_block",
                "redstone_block",
                "quartz_block_side",
            ],
        }
    },
    "STATIC_SEA_LANTERNS": {"32X": ["sea_lantern"], "64X": ["sea_lantern"]},
}

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
    - `"confirmation"`
    - `None`
    """
    if input_type and input_type != None:
        valid_input = False

        while not valid_input:
            user_input = input("> ")

            if input_type == "confirmation" and user_input.lower() in [
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


def clean_url(url):
    """
    This function cleans the provided `url` parameter by removing:
    - trailing and leading whitespaces
    - protocols
    - leading slashes
    """
    protocol_separator = "://"

    url = url.strip()

    if protocol_separator in url:
        url = url.split(protocol_separator, 1)[1]
    return url.removesuffix("/")


def format_pascal(format_value):
    """
    This function converts the provided `format_value` parameter from snake_case to PascalCase.
    """
    return "".join(word.capitalize() for word in format_value.split("_"))


def get_texture_ids(textures_url, textures_list):
    results = []
    found_ids = set()

    for texture in textures_list:
        metadata_url = f"{textures_url}/{texture}"

        metadata_request = Request(
            metadata_url,
            headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"},
        )

        with urlopen(metadata_request, timeout=5) as metadata_response:
            texture_metadata = json.load(metadata_response)

        texture_id = texture_metadata[0]["id"]

        if texture_id not in found_ids:
            found_ids.add(texture_id)

            results.append({"name": texture, "id": texture_id})
    return results


def download_textures(
    textures_url,
    textures_list,
    resource_pack,
    addon_name,
    output_path,
    category_name=None,
):
    pack_directory = output_path / resource_pack
    pack_directory.mkdir(exist_ok=True)

    addon_directory = pack_directory / addon_name
    addon_directory.mkdir(exist_ok=True)

    category_directory = None

    if category_name != None:
        category_directory = addon_directory / category_name
        category_directory.mkdir(exist_ok=True)

    for texture in textures_list:
        texture_name = texture["name"]
        texture_id = texture["id"]

        download_path = None

        if category_name != None:
            download_path = category_directory / f"{texture_name}.png"
        else:
            download_path = addon_directory / f"{texture_name}.png"

        download_url = f"{textures_url}/{texture_id}/url/{resource_pack}/java-latest"

        download_request = Request(
            download_url, headers={"Accept": "image/png", "User-Agent": "Mozilla/5.0"}
        )

        with urlopen(download_request, timeout=5) as download_response:
            texture_data = download_response.read()

        with download_path.open("wb") as new_texture:
            new_texture.write(texture_data)

        relative_path = Path("..") / download_path.relative_to(output_path.parent)

        print(f"Downloaded '{relative_path}'")


def main():
    textures_url = "https://api.faithfulpack.net/v2/textures"

    current_directory = Path(__file__).parent
    parent_directory = current_directory.parent

    print(f"The following will be downloaded from")
    print(f"'{clean_url(textures_url)}' once confirmed:\n")

    for addon_name, addon_content in BLOCKS.items():
        print(f"├ Add-on: {format_pascal(addon_name)}")

        for index, (resolution, block_data) in enumerate(addon_content.items()):
            collected_files = []

            if isinstance(block_data, list):
                collected_files = [f"{block}.png" for block in block_data]
            else:
                for _, block_list in block_data.items():
                    collected_files.extend([f"{block}.png" for block in block_list])

            resolution_message = f"Resolution: {resolution.lower()}"
            files_message = f"Files to download: {collected_files}"

            if len(addon_content) == 1:
                print(f"└─┬ {resolution_message}")
                print(f"  └── {files_message}\n")
            elif index == 0:
                print(f"└─┬ {resolution_message}")
                print(f"  ├── {files_message}")
            elif index >= 1 and index < (len(addon_content) - 1):
                print(f"  ├ {resolution_message}")
                print(f"  ├── {files_message}")
            else:
                print(f"  ├ {resolution_message}")
                print(f"  └── {files_message}\n")
    print("Do you want to continue? (Y/N)")

    confirmation_input = custom_input("confirmation").lower()

    if confirmation_input in ["y", "yes"]:
        downloaded_directory = parent_directory / "downloaded_files"
        downloaded_directory.mkdir(exist_ok=True)

        print("\nDownloading files...\n")

        for addon_name, addon_content in BLOCKS.items():
            for resolution, block_data in addon_content.items():
                resource_pack = f"faithful_{resolution.lower()}"

                if isinstance(block_data, list):
                    texture_ids = get_texture_ids(textures_url, block_data)

                    download_textures(
                        textures_url,
                        texture_ids,
                        resource_pack,
                        addon_name.lower(),
                        downloaded_directory,
                    )
                else:
                    for category_name, block_list in block_data.items():
                        texture_ids = get_texture_ids(textures_url, block_list)

                        download_textures(
                            textures_url,
                            texture_ids,
                            resource_pack,
                            addon_name.lower(),
                            downloaded_directory,
                            category_name.lower(),
                        )
    input("\nPress any key to exit...")


# Main #

if __name__ == "__main__":
    handle_function(main)
