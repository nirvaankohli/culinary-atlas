import json
from pathlib import Path
import time

ROOT_PATH = Path(__file__).parent.parent.parent
SETTING_PATH = ROOT_PATH / "agents" / "common_settings.json"
EXAMPLE_PATH = ROOT_PATH / "agents" / "examples"
EXAMPLE_OUTPUT_PATH = EXAMPLE_PATH / "recipes_output.json"


class common_settings:

    def __init__(self, agent_name: str, log: bool = False):

        import json
        from pathlib import Path

        self.debug = log

        self.module_name = self.__class__.__name__

        try:

            self.root_path = ROOT_PATH

        except Exception as e:

            self.root_path = Path(__file__).parent.parent.parent
            self.warn(e, "Failed to set ROOT_PATH; assuming path")

        try:

            self.settings_path = SETTING_PATH

        except Exception as e:

            self.settings_path = (
                Path(__file__).parent.parent.parent / "agents" / "common_settings.json"
            )
            self.warn(e, "Failed to set SETTING_PATH; assuming path")

        try:

            with open(self.settings_path, "r") as f:

                self.settings = json.load(f)

        except Exception as e:

            self.settings = {}
            self.warn(e, "Failed to load settings; using empty settings")

        self.agent_name = agent_name

        try:

            agent_in_list = self.settings["agents"]["available_agents"]

        except Exception as e:

            agent_in_list = []
            self.warn(e, "Failed to get available_agents; using empty list")

        if self.agent_name not in agent_in_list:

            self.warn(
                Exception("Agent not in available_agents"),
                f"Agent '{self.agent_name}' not found in available_agents",
            )

            raise Exception(f"Agent '{self.agent_name}' not found in available_agents")

        try:

            self.env_path = self.root_path / self.settings["env"]["path"]

        except Exception as e:

            self.env_path = self.root_path / "env"
            self.warn(e, "Failed to set ENV_PATH; assuming path")

        self.load_env()
        self.load_env_available_keys()

    def replace_prompts_in_body_with_custom(
        self, body, user: str, system=None, assistant=None
    ):

        if "messages" in body:

            for message in body["messages"]:

                if message["role"] == "user" and user is not None:

                    message["content"] = user

                if message["role"] == "system" and system is not None:

                    message["content"] = system

                if message["role"] == "assistant" and assistant is not None:

                    message["content"] = assistant

        return body

    def get_headers(self, api_key="use_env", key_name="AI_API_KEY"):

        if api_key == "use_env":

            try:

                if key_name in self.env_available_keys:

                    pass

                else:

                    self.warn(
                        Exception("Key not in available_keys"),
                        f"Key '{key_name}' not found in available_keys; will use first available key",
                    )

                    key_name = self.env_available_keys[0]

            except Exception as e:

                self.warn(
                    e,
                    "Failed to check if key_name is in env_available_keys; assuming not in list",
                )

            try:

                api_key = self.env.get(f"{key_name}")

            except Exception as e:
                api_key = ""
                self.warn(
                    e,
                    f"Failed to get API key from env for key_name '{key_name}'; using empty string",
                )

        try:

            self.default_headers = self.settings["ai_api"]["default_headers"]

        except Exception as e:

            self.default_headers = {}
            self.warn(e, "Failed to get default_headers; using empty dict")

        headers = self.default_headers.copy()

        for header_key, header_value in headers.items():

            if "{AI_API_KEY}" in header_value:

                headers[header_key] = header_value.replace("{AI_API_KEY}", api_key)

        return headers

    def load_env_available_keys(self):

        try:

            self.env_available_keys = self.settings["env"]["available_keys"]

        except Exception as e:

            self.env_available_keys = []
            self.warn(e, "Failed to get available_keys; using empty list")

    def load_env(self):

        import os

        try:

            from dotenv import load_dotenv

        except Exception as e:

            self.warn(
                e,
                "Failed to load .env file(You may not have dotenv installed) | Do it by 'pip install python-dotenv'",
            )

        try:

            load_dotenv(self.env_path)

        except Exception as e:

            self.warn(e, "Failed to load .env file from ENV_PATH; skipping")

        self.env = os.environ

    def get_body(self):

        self.default_body = self.settings["ai_api"]["body"]["default"]
        self.specific = self.settings["ai_api"]["body"]["specific"][self.agent_name]
        self.body = self.default_body.copy()
        self.specific_body = self.specific["raw"]
        self.specific_roles = self.specific.get("roles", {})

        for key, value in self.specific_body.items():

            self.body[key] = value

        already_present_roles = []

        for message in self.body["messages"]:

            already_present_roles.append(message["role"])

        for message in self.specific_roles:

            if message not in already_present_roles:

                self.body["messages"].append({"role": message, "content": ""})

        return self.body

    def warn(self, e: Exception, extra: str = ""):

        print(f"| FROM {self.module_name} | WARNING: {e} | {extra}")

    def get_chat_completion_url(self):

        try:

            url = (
                self.settings["ai_api"]["urls"]["base_api_url"]
                + self.settings["ai_api"]["urls"]["chat_completion_endpoint"]
            )

        except Exception as e:

            self.warn(e, "Failed to get chat_completion_url; returning empty string")
            url = ""

        return url

    def log(self, message: str):

        if self.log:

            print(f"| FROM {self.module_name} | LOG: {message}")


common_settings_instance = common_settings(agent_name="recipes", log=False)


def process_list(input_data: list, at_a_time=5, max_num=10) -> str:

    t0 = time.perf_counter()

    recursion_needed = False
    input_data.sort(reverse=True, key=lambda x: x.get("similarity_score", 0))

    common_settings_instance.log(f"Running process_list on {len(input_data)} items")

    if len(input_data) > at_a_time:

        recursion_needed = True
        recursion_list = input_data[at_a_time:max_num]

    input_data = input_data[:at_a_time]

    results = []
    list_of_inputs = []

    for i in input_data:

        dish_name = i.get("dish_name", "")
        local_name = i.get("local_name", "")
        recipe_search_prompt = i.get("recipe_search_prompt", "")

        list_of_inputs.append(
            {
                "dish_name": dish_name,
                "local_name": local_name,
                "recipe_search_prompt": recipe_search_prompt,
            }
        )

    input_into = json.dumps(list_of_inputs)

    common_settings_instance.log(f"Input JSON for API(length): {len(input_into)}")
    SYSTEM_PROMPT = """You are a recipe retrieval and structuring assistant.
Given a dish name, local name, and a recipe search prompt (used against a database like Spoonacular),
you return a clean, structured recipe object.

Rules:
- Use the given dish/local name as the identity of the dish.
- Assume the search prompt already matched a real recipe; do NOT invent obviously fake ingredients.
- Be concise and practical: focus on what a cook needs (ingredients, equipment, steps, time).
- Return ONLY valid JSON (no extra text, no markdown).
- There should only be ONE recipe per list item in the input.

Output schema (single JSON object):
[
{
"matched_recipe_title": string,
"summary": string,
"servings": int,
"total_time_minutes": int,
"materials": {
    "ingredients": [
    {
        "name": string,
        "quantity": string,   # e.g. "2", "1/2", "to taste"
        "unit": string,       # e.g. "tbsp", "g", "cup", "" if none
        "notes": string       # optional prep notes, can be ""
    }
    ],
    "equipment": [string]     # e.g. ["wok", "large pot", "baking tray"]
},
"steps": [string],          # ordered, clear, numbered implicitly
"image_url": string,        # direct URL to a representative image - Make sure this is an image URL. It should exist and be accessible. Double check the link to see if the image exists, reachable, and has meaningful content. Make sure it is the actual dish.
"source_url": string,       # canonical recipe/source URL if available, else ""
"source": string            # e.g. "spoonacular"
}
]"""

    USER_PROMPT = f"""Build a structured recipe for the following dish(es) using my recipe database result.

    Input:
    {input_into}

    Tasks:
    - Use the best-matching recipe from the database result for this search prompt.
    - Normalize and clean up ingredient quantities and units.
    - Extract a reasonable total_time_minutes (estimate if only prep/cook times are given).
    - Write clear, step-by-step cooking instructions in "steps".
    - Fill in image_url and source_url from the recipe data if available.

    Use exactly the schema and field names defined in the system prompt."""

    body = common_settings_instance.get_body()
    body = common_settings_instance.replace_prompts_in_body_with_custom(
        body, user=USER_PROMPT, system=SYSTEM_PROMPT
    )
    header = common_settings_instance.get_headers()

    url = common_settings_instance.get_chat_completion_url()

    import requests

    response = requests.post(url, headers=header, json=body)

    results = []

    if response.status_code == 200:

        common_settings_instance.log("API request successful")

        try:

            ayy = json.loads(
                response.json()["choices"][0]["message"]["content"]
                .replace("`json", "")
                .replace("\n", "")
                .replace("`", "")
            )

            common_settings_instance.log(f"Received {len(ayy)} results from API")

            for res in range(len(ayy)):

                addition = ayy[res]

                for key, value in input_data[res].items():

                    addition[key] = value

                results.append(addition)

            if recursion_needed:

                results += process_list(
                    recursion_list, at_a_time=at_a_time, max_num=max_num
                )

                common_settings_instance.log(
                    f"Recursion needed; total results now {len(results)} after processing remaining items"
                )

        except Exception as e:

            with open(
                EXAMPLE_PATH / "recipes_debug_response.txt", "w", encoding="utf-8"
            ) as f:

                f.write(response.json()["choices"][0]["message"]["content"])

                results = []

    else:

        common_settings_instance.warn(
            Exception(f"API request failed with status code {response.status_code}"),
            f"Response: {response.text}",
        )

    common_settings_instance.log(
        f"process_list completed with {len(results)} total results"
    )

    elapsed = time.perf_counter() - t0
    common_settings_instance.log(f"Elapsed time for process_list: {elapsed:.2f}")

    return results


if __name__ == "__main__":

    import time

    t = time.perf_counter()

    with open(EXAMPLE_PATH / "diversifier_output.json", "r", encoding="utf-8") as f:

        diversifier_output = json.load(f)

    with open(EXAMPLE_OUTPUT_PATH, "w", encoding="utf-8") as f:

        response = process_list(diversifier_output)
        f.write(json.dumps(response, indent=2))

    elapsed = time.perf_counter() - t
    print(f"Elapsed time: {elapsed:.2f} seconds")
