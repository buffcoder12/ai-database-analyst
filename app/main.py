import streamlit as st
import pandas as pd
import plotly.express as px

from app.query_engine import ask_database
from app.query_cache import(
    clear_cache,
    get_cache_size
)


if "query_history" not in st.session_state:
    st.session_state.query_history = []


st.set_page_config(
    page_title="AI Database Analyst",
    page_icon="🤖",
    layout="wide"
)

with st.sidebar:
    st.header("🕘 Query History")
    
    if st.session_state.query_history:

        for item in reversed(
            st.session_state.query_history
        ):

            st.write(
                f"• {item}"
            )
    
    else:
        st.info(
            "No queries yet."
        )
    
    st.divider()

    st.metric(
        "Cached Queries",
        get_cache_size()
    )

    if st.button("🗑️ Clear Cache"):

        clear_cache()

        st.success(
            "Cache cleared."
        )
        
        st.rerun()

st.title("🤖 AI Database Analyst")

st.markdown(
    """
    Ask questions about your PostgreSQL database
    using natural language.
    """
)

st.info(
    "Example: What are the top 3 products by revenue?"
)


question = st.text_input(
    "Ask your database a question:",
    placeholder="Example: What is the total revenue?"
)


if st.button("Run Query", type="primary"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Analyzing your question..."):

            try:

                response = ask_database(question)

                if question not in st.session_state.query_history:

                    st.session_state.query_history.append(
                        question
                    )

                    # Keep only the latest 10 queries

                    st.session_state.query_history = (
                        st.session_state.query_history[-10:]
                    )

                st.success(
                    "Query completed successfully!"
                )

                if response.get("from_cache"):
                    st.info(
                        "⚡Result Loaded from cache — "
                        "now new Gemini request was required. "
                    )
                else:
                    st.info(
                        "🤖 New AI analysis generated."
                    )

                
                # ANSWER
                
                st.subheader("💡 Answer")
                st.write(response["answer"])

                st.subheader("⚡ Performance")

                performance = response.get(
                    "performance",
                     {}
                )

                if performance:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Total Time", 
                            f"{performance.get('total_time', 0):.3f}s"
                        )

                    with col2:
                        st.metric(
                            "SQL Generation",
                            f"{performance.get('sql_generation_time', 0):.3f}s"
                        )

                    with col3:
                        st.metric(
                            "Database",
                            f"{performance.get('database_execution_time', 0):.3f}s"
                        )
                    
                    with st.expander(
                        "Detailed Performance"
                    ):

                        st.json(performance)
                            


                # GENERATED SQL

                st.subheader("🧠 Generated SQL")
                st.code(
                    response["sql"],
                    language="sql"
                )

                
                # EXPLANATION
               
                st.subheader("📝 Explanation")
                st.write(
                    response["explanation"]
                )

                
                # DATABASE RESULTS
                
                st.subheader(
                    "📊 Database Results"
                )

                results = response["results"]

                # Initialize dataframe so Pylance
                # knows it always exists.
                dataframe = None

                if results:

                    dataframe = pd.DataFrame(
                        results
                    )

                    st.dataframe(
                        dataframe,
                        width="stretch"
                    )

                else:

                    st.info(
                        "No matching records found."
                    )

                
                # VISUALIZATION
                
                visualization = response.get(
                    "visualization"
                )

                if visualization and dataframe is not None:

                    st.subheader(
                        "📈 Visualization"
                    )

                    chart_type = (
                         visualization.chart_type
                    )

                    
                    # METRIC
                    
                    if chart_type == "metric":

                        column = (
                            visualization.y_column
                        )

                        if (
                            column
                            and column in dataframe.columns
                        ):

                            value = dataframe.iloc[0][
                                column
                            ]

                            if isinstance(
                                value,
                                (int, float)
                            ):

                                st.metric(
                                    label=visualization.title,
                                    value=f"{value:,.2f}"
                                )

                            else:

                                st.metric(
                                    label=visualization.title,
                                    value=str(value)
                                )

                    
                    # BAR CHART
                    
                    elif chart_type == "bar":

                        x_column = (
                            visualization.x_column
                        )

                        y_column = (
                            visualization.y_column
                        )

                        if (
                            x_column
                            and y_column
                            and x_column in dataframe.columns
                            and y_column in dataframe.columns
                        ):

                            fig = px.bar(
                                dataframe,
                                x=x_column,
                                y=y_column,
                                title=visualization.title
                            )

                            fig.update_layout(
                                xaxis_title=x_column,
                                yaxis_title=y_column
                            )

                            st.plotly_chart(
                                fig,
                                width="stretch"
                            )

                    
                    # LINE CHART
                    
                    elif chart_type == "line":

                        x_column = (
                            visualization.x_column
                        )

                        y_column = (
                            visualization.y_column
                        )

                        if (
                            x_column
                            and y_column
                            and x_column in dataframe.columns
                            and y_column in dataframe.columns
                        ):

                            fig = px.line(
                                dataframe,
                                x=x_column,
                                y=y_column,
                                markers=True,
                                title=visualization.title
                            )

                            fig.update_layout(
                                xaxis_title=x_column,
                                yaxis_title=y_column
                            )

                            st.plotly_chart(
                                fig,
                                width="stretch"
                            )

                    
                    # PIE CHART
                    
                    elif chart_type == "pie":

                        x_column = (
                            visualization.x_column
                        )

                        y_column = (
                            visualization.y_column
                        )

                        if (
                            x_column
                            and y_column
                            and x_column in dataframe.columns
                            and y_column in dataframe.columns
                        ):

                            fig = px.pie(
                                dataframe,
                                names=x_column,
                                values=y_column,
                                title=visualization.title
                            )

                            st.plotly_chart(
                                fig,
                                width="stretch"
                            )

                    
                    # TABLE
            
                    elif chart_type == "table":

                        st.dataframe(
                            dataframe,
                            width="stretch"
                        )

            except Exception as error:

                st.error(
                    "Something went wrong."
                )

                st.exception(error)