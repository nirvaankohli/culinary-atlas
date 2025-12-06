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

app = Flask(__name__)

# Store results temporarily (in production, use a database or session)
results_store = {}


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

    return render_template("query.html", query=food)


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

        # Store results for the results page
        results_store[food] = {
            "dishes": diversification_result,
            "recipes": recipes_result,
        }

        yield json.dumps({"status": "done"}) + "\n"

    return Response(stream_with_context(generate()), mimetype="application/json")


@app.route("/load_results/", methods=["GET"])
def load_results():
    params = request.args
    food = params.get("query", "")

    # Get stored results
    data = results_store.get(food, {"dishes": "[]", "recipes": "{}"})

    # Parse dishes
    try:
        dishes = (
            json.loads(data["dishes"])
            if isinstance(data["dishes"], str)
            else data["dishes"]
        )
    except:
        dishes = []

    return render_template("results.html", query=food, dishes=dishes)


if __name__ == "__main__":

    app.run(debug=True)
