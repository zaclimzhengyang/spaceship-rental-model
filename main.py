from typing import Any

from flask import Flask, Response, request, jsonify

from models.contract import Contract
from models.slim_solution import SlimSolution
from resolvers.resolvers import resolve_optimize_contracts

app: Flask = Flask(__name__)

@app.route("/spaceship/optimize", methods=["POST"])
def spaceship_optimize() -> Response:
    raw_input_data: list[dict[str, Any]] = request.get_json()
    contracts: list[Contract] = [
        contract
        for contract in map(
            lambda contract_dict: Contract.parse_obj(contract_dict), raw_input_data
        )
    ]
    solution: SlimSolution = resolve_optimize_contracts(contracts=contracts)
    serialized_solution: Response = jsonify(solution.dict())
    return serialized_solution


if __name__ == "__main__":
    """
    spin up the service on host = "0.0.0.0", port 5000

    bind to all network interfaces (0.0.0.0) instead of just localhost,
    allowing it to accept connection from outside the Docker container, if spun up with docker
    """
    app.run(host="0.0.0.0", port=5050)