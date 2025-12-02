from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent
SETTING_PATH = ROOT_PATH / "agents" / "common_settings.json"

class common_settings:

    def __init__(self):

        import json

        try:


