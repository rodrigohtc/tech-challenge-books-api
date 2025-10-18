from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from api.services.ml_data import (
    prepare_feature_matrix,
    prepare_training_dataset,
    summarize_predictions,
)

router = APIRouter(prefix="/ml", tags=["ml"])


class PredictionItem(BaseModel):
    book_id: Optional[int] = Field(None, description="Identificador interno do livro")
    model: Optional[str] = Field(None, description="Nome ou versão do modelo que gerou a predição")
    score: Optional[float] = Field(None, description="Score numérico da predição")
    label: Optional[str] = Field(None, description="Classe prevista (se aplicável)")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Metadados adicionais fornecidos pelo modelo"
    )


class PredictionPayload(BaseModel):
    predictions: List[PredictionItem]


@router.get("/features")
def ml_features() -> List[Dict[str, Any]]:
    dataset = prepare_feature_matrix()
    return dataset


@router.get("/training-data")
def ml_training_data() -> Dict[str, Any]:
    dataset = prepare_training_dataset()
    return dataset


@router.post("/predictions")
def ml_predictions(payload: PredictionPayload) -> Dict[str, Any]:
    if not payload.predictions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Predictions payload is empty.",
        )
    summary = summarize_predictions([prediction.model_dump() for prediction in payload.predictions])
    return {"status": "accepted", "summary": summary}
