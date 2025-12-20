import sys
from pathlib import Path
from pathvalidate import sanitize_filename

BASE_DB_PATH = Path(
    "c:/Users/nirva/OneDrive/Projects/culinary-atlas/culinary-atlas/data/db"
)
RECIPES_DB_PATH = BASE_DB_PATH / "recipes"


def clean_filename(name: str) -> str:
    return sanitize_filename(name.replace(" ", "_").lower())


dish_name = "jollof-rice"
cleaned = clean_filename(dish_name)
path = RECIPES_DB_PATH / cleaned
print(f"Dish Name: {dish_name}")
print(f"Cleaned: {cleaned}")
print(f"Path: {path}")
print(f"Exists: {path.exists()}")

dish_name_underscores = dish_name.replace("-", "_")
cleaned_u = clean_filename(dish_name_underscores)
path_u = RECIPES_DB_PATH / cleaned_u
print(f"With Underscores: {dish_name_underscores}")
print(f"Cleaned U: {cleaned_u}")
print(f"Path U: {path_u}")
print(f"Exists U: {path_u.exists()}")
