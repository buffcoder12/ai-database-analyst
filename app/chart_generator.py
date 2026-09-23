from app.gemini_client import generate_with_fallback
from app.visualization import VisualizationResponse


def is_numeric(value):
    """
    Check whether value is numeric.
    """
    return isinstance(value, (int, float))


def generate_visualization(
    question: str,
    results: list
):
    """
    Select the most appropriate visualization for the query results.
    """

    if not results:

        return VisualizationResponse(
            chart_type="table",
            x_column=None,
            y_column=None,
            title="No Results",
            reason="There is no data to visualize."
        )

    columns = list(results[0].keys())

    # SIMPLE CASE: single result

    if len(results) == 1:

        numeric_columns = [
            column
            for column in columns
            if is_numeric(results[0][column])
        ]

        if len(numeric_columns) == 1:

            return VisualizationResponse(
                chart_type="metric",
                x_column=None,
                y_column=numeric_columns[0],
                title=question,
                reason=(
                    "A single numeric result is "
                    "best displayed as a metric."
                )
            )

    # SIMPLE CASE: category + numeric

    if len(columns) == 2:

        numeric_columns = []

        non_numeric_columns = []

        for column in columns:

            values = [
                row[column]
                for row in results
                if row[column] is not None
            ]

            if values and all(
                is_numeric(value)
                for value in values
            ):
                numeric_columns.append(
                    column
                )

            else:

                non_numeric_columns.append(
                    column
                )

        if (
            len(numeric_columns) == 1
            and len(non_numeric_columns) == 1
        ):

            return VisualizationResponse(
                chart_type="bar",
                x_column=non_numeric_columns[0],
                y_column=numeric_columns[0],
                title=question,
                reason=(
                    "A bar chart is appropriate for "
                    "comparing categories."
                )
            )


    # Detect date/time columns
    
    date_columns = []

    numeric_columns = []

    for column in columns:

        values = [
            row[column]
            for row in results
            if row[column] is not None
        ]

        if not values:
            continue

        if all(
            is_numeric(value)
            for value in values
        ):

            numeric_columns.append(
                column
            )

        elif all(
            hasattr(value, "year")
            for value in values
        ):

            date_columns.append(
                column
            )

   
    # Date + numeric → line chart
    
    if (
        len(date_columns) == 1
        and len(numeric_columns) >= 1
    ):

        return VisualizationResponse(
            chart_type="line",
            x_column=date_columns[0],
            y_column=numeric_columns[0],
            title=question,
            reason=(
                "A line chart is appropriate "
                "for showing change over time."
            )
        )

    # Fall back to Gemini only when necessary

    prompt = f"""
You are an expert data visualization analyst.

Choose the BEST visualization for the user's
question and the database results.

USER QUESTION:
{question}

AVAILABLE COLUMNS:
{columns}

DATABASE RESULTS:
{results}

AVAILABLE TYPES:

bar
line
pie
metric
table

RULES:

1. Only use existing columns.
2. Never invent column names.
3. Use line for trends over time.
4. Use bar for category comparisons.
5. Use pie only when the results represent meaningful parts of a whole.
6. Use metric for one important number.
7. Use table when visualization is not useful.
8. Return only one visualization choice.
9. Use x_column and y_column only when required by the selected chart.
10. Keep the title short and meaningful.
"""

    response = generate_with_fallback(
        prompt,
        config={
            "temperature": 0.1,
            "response_mime_type": "application/json",
            "response_schema": VisualizationResponse,
            "tools": []
        }
    )

    if response.text is None:
        raise RuntimeError(
            "Gemini returned an empty response "
            "while generating visualization"
        )

    return VisualizationResponse.model_validate_json(
        response.text   
    )