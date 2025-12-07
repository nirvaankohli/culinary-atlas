from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    stream_with_context,
    Response,
    url_for,
)
import json
from pathlib import Path
from pathvalidate import sanitize_filename

app = Flask(__name__)

BASE_DB_PATH = Path(__file__).parent / "data" / "db"
RECIPES_DB_PATH = BASE_DB_PATH / "recipes"
RESULTS_DB_PATH = BASE_DB_PATH / "results"

def clean_filename(name: str) -> str:
    return sanitize_filename(name.replace(" ", "_").lower())

@app.route("/", methods=["GET"])
def home():

    import random

    phrases = [
        "see how the world eats.",
        "one dish. every culture.",
        "map the menu.",
        "eat everywhere.",
        "the geography of flavor.",
        "global roots. local tastes.",
        "savor the world's flavors.",
        "culinary journeys await.",
        "flavorful adventures start here.",
    ]

    return render_template("index.html", phrase=random.choice(phrases))


@app.route("/status", methods=["GET"])
def status():

    return jsonify({"status": "ok"}), 200


@app.route("/query/load/", methods=["GET"])
def load_query():

    params = request.args
    food = params.get("food", "")

    already_exists = False

    cleaned_food = clean_filename(food)

    if (RESULTS_DB_PATH / f"{cleaned_food}.json").exists():
        already_exists = True

    return render_template("query.html", query=food, already_exists=already_exists)


@app.route("/api/query/", methods=["GET", "POST"])
def ai_query():

    params = request.args
    food = params.get("food")

    def generate():

        yield json.dumps({"status": "start", "stage": "initialization"}) + "\n"

        import agents.diversifier.client as diversifier_client

        diversification_result = diversifier_client.process_diversification(food)

        yield json.dumps(
            {
                "status": "complete",
                "stage": "diversification",
                "result": diversification_result,
            }
        ) + "\n"

        import agents.recipes.client as recipes_client

        recipes_result = recipes_client.process_list(diversification_result)

        yield json.dumps(
            {"status": "complete", "stage": "recipes", "result": recipes_result}
        ) + "\n"

        cleaned_food = clean_filename(food)

        with open(RESULTS_DB_PATH / f"{cleaned_food}.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "dishes": json.dumps(diversification_result),
                    "recipes": json.dumps(recipes_result),
                },
                f,
                ensure_ascii=False,
                indent=4,
            )



        yield json.dumps({"status": "done"}) + "\n"

    return Response(stream_with_context(generate()), mimetype="application/json")


@app.route("/load_results/", methods=["GET"])
def load_results():

    params = request.args
    food = params.get("query", "")

    cleaned_food = clean_filename(food)
    try:

        with open(RESULTS_DB_PATH / f"{cleaned_food}.json", "r", encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:

        return render_template("results.html", query=food, dishes=[], recipe_dishes=[], non_recipe_dishes=[])


    try:
        dishes = (
            json.loads(data["dishes"])
            if isinstance(data["dishes"], str)
            else data["dishes"]
        )

        recipes = (
            json.loads(data["recipes"])
            if isinstance(data["recipes"], str)
            else data["recipes"]
        )

    except:
        dishes = []
        recipes = []


    dishes_not_with_recipes = []
    recipe_dishes = []

    for i in recipes:

        dishes_not_with_recipes.append(i["dish_name"])
        recipe_dishes.append(i)

    non_recipe_dishes = []

    for dish in dishes:

        if dish in dishes_not_with_recipes:

            non_recipe_dishes.append(dish)



    return render_template("results.html", query=food, dishes=dishes, recipe_dishes=recipe_dishes, non_recipe_dishes=non_recipe_dishes)


if __name__ == "__main__":

    app.run(debug=True)
