from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent
SETTING_PATH = ROOT_PATH / "agents" / "common_settings.json"


class common_settings:

    def __init__(self, agent_name: str):

        import json
        from pathlib import Path

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


class agent_name_replace:

    def __init__(self):

        common_settings_instance = common_settings(agent_name="agent_name_replace")


if __name__ == "__main__":

    instance = agent_name_replace()
