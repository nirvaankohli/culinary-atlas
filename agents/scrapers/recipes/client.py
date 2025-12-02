import json
import requests
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent.parent
SETTING_PATH = ROOT_PATH / "agents" / "common_settings.json"
EXAMPLE_PATH = ROOT_PATH / "agents" / "examples"
EXAMPLE_OUTPUT_PATH = EXAMPLE_PATH / "scrapers_recipes_output.json"
INPUT_PATH = EXAMPLE_PATH / "diversifier_output.json"


def clear_of_junk(text: str) -> str:

    return (
        text.replace("\n", "")
        .replace("`", "")
        .replace("how to cook ", "")
        .replace("how to ", "")
        .replace("recipe", "")
    )


def process(search_term: str):

    search_term = clear_of_junk(search_term)

    print(search_term)

    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={search_term}"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    data = response.json()
    return data


if __name__ == "__main__":

    with open(INPUT_PATH, "r", encoding="utf-8") as f:

        input_data = json.load(f)

    response = process(input_data[0]["recipe_search_prompt"])

    with open(EXAMPLE_OUTPUT_PATH, "w", encoding="utf-8") as f:

        f.write(json.dumps(response, indent=2))
