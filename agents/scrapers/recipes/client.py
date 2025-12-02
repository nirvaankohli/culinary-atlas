import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

ROOT_PATH = Path(__file__).parent.parent.parent.parent
SETTING_PATH = ROOT_PATH / "agents" / "common_settings.json"
EXAMPLE_PATH = ROOT_PATH / "agents" / "examples"
EXAMPLE_OUTPUT_PATH = EXAMPLE_PATH / "scrapers_recipes_output.json"
INPUT_PATH = EXAMPLE_PATH / "diversifier_output.json"
ENV_PATH = json.loads(open(SETTING_PATH, "r", encoding="utf-8").read())["env"]["path"]
KEY_PATH = Path(__file__).parent / "current_key_num.json"
NUM_API_KEYS = 2

load_dotenv(ENV_PATH)


def clear_of_junk(text: str) -> str:

    return (
        text.replace("\n", "")
        .replace("`", "")
        .replace("how to cook ", "")
        .replace("how to ", "")
        .replace("recipe", "")
    )


def get_current_key_num() -> int:

    with open(KEY_PATH, "r", encoding="utf-8") as f:

        key_data = json.load(f)

    return key_data.get("current_key_num", 0)


def cycle_key(num_keys: int = NUM_API_KEYS) -> None:

    current_key_num = get_current_key_num()

    new_key_num = (current_key_num + 1) % num_keys
    with open(KEY_PATH, "w", encoding="utf-8") as f:

        json.dump({"current_key_num": new_key_num}, f)


def process(
    search_term: str, other_params: dict = {}, recursion_depth: int = 0
) -> dict:

    search_term = clear_of_junk(search_term)

    params = other_params.copy()
    params["query"] = search_term

    current_key_num = get_current_key_num()

    API_KEY = os.getenv(f"RECIPE_API_KEY_{current_key_num}")
    params["apiKey"] = API_KEY

    url = "https://api.spoonacular.com/recipes/complexSearch"

    results = requests.get(
        url,
        params=params,
    )

    if results.status_code == 429 and recursion_depth < NUM_API_KEYS - 1:

        cycle_key()

    elif results.status_code != 200:

        return {"status_code": results.status_code}

    return results.json()


if __name__ == "__main__":

    with open(INPUT_PATH, "r", encoding="utf-8") as f:

        input_data = json.load(f)

    response = {}
    for i in range(len(input_data)):

        response[clear_of_junk(input_data[i]["recipe_search_prompt"])] = process(
            input_data[i]["recipe_search_prompt"]
        )

    with open(EXAMPLE_OUTPUT_PATH, "w", encoding="utf-8") as f:

        f.write(json.dumps(response, indent=2))
