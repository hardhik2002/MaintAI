from __future__ import annotations

import logging
from functools import lru_cache

import joblib
from maintai_ml.artifact import ModelArtifact

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_model() -> ModelArtifact:
    path = get_settings().model_path
    if not path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Run the training command first."
        )
    artifact: ModelArtifact = joblib.load(path)
    logger.info("model_loaded", extra={"model_version": artifact.metadata["model_version"]})
    return artifact
