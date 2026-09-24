from fastapi.testclient import TestClient

VALID = {
    "machine_id": "MACHINE-TEST",
    "type": "M",
    "air_temperature": 300,
    "process_temperature": 310,
    "rotational_speed": 1500,
    "torque": 40,
    "tool_wear": 80,
}


def test_health_and_readiness(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_prediction_is_persisted(client: TestClient) -> None:
    response = client.post("/api/v1/predict", json=VALID)
    assert response.status_code == 201
    body = response.json()
    assert body["machine_id"] == "MACHINE-TEST"
    assert 0 <= body["failure_probability"] <= 1
    assert client.get("/api/v1/machines").json()[0]["machine_id"] == "MACHINE-TEST"
    assert len(client.get("/api/v1/machines/MACHINE-TEST/history").json()) == 1


def test_invalid_physical_values_return_422(client: TestClient) -> None:
    invalid = {**VALID, "rotational_speed": -10}
    assert client.post("/api/v1/predict", json=invalid).status_code == 422


def test_model_metrics_are_real_artifact_values(client: TestClient) -> None:
    response = client.get("/api/v1/model/metrics")
    assert response.status_code == 200
    assert response.json()["test_metrics"]["pr_auc"] > 0
