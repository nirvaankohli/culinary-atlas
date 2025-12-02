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


@app.route("/", methods=["GET"])
def home():

    return render_template("index.html")


@app.route("/status", methods=["GET"])
def status():

    return jsonify({"status": "ok"}), 200


@app.route("/api/query", methods=["GET", "POST"])
def ai_query():

    params = request.args
    food = params.get("food")

    def generate():

        yield json.dumps({"status": "start", "stage": "initialization"}) + "\n"

        import agents.diversifier.client as diversifier_client

        result = diversifier_client.process_diversification(food)

        yield json.dumps(
            {"status": "complete", "stage": "diversification", "result": result}
        ) + "\n"

        import agents.recipes.client as recipes_client

        result = recipes_client.process_list(result)

        yield json.dumps(
            {"status": "complete", "stage": "recipes", "result": result}
        ) + "\n"

        yield json.dumps({"status": "done"}) + "\n"

    return Response(stream_with_context(generate()), mimetype="application/json")



if __name__ == "__main__":

    app.run(debug=True)
