from pydantic import BaseModel, Field
from typing import Literal


class VisualizationResponse(BaseModel):

    chart_type: Literal[
        "bar",
        "line",
        "pie",
        "metric",
        "table",
    ]

    x_column: str | None =None

    y_column: str | None =None

    title: str = Field(
        description="Short title for the visualization chart"
    )

    reason: str = Field(
        description="Why this visualization is appropriate"
    )