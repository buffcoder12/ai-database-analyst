import streamlit as st
import pandas as pd 
import plotly.express as px

from app.query_engine import ask_database


st.set_page_config(
    page_title="AI Database Analyst",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Database Analyst")
st.write(
    "Ask questions about your database "
    "using natural language."
)


question = st.text_input(
    "Ask your database a question",
    placeholder="e.g Who are my top 5 customers by spending?"
)


if st.button("Ask AI", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Analyzing your database...."):

            try:
                response = ask_database(question)

                #Answer
                st.subheader("💡 Answer")

                st.write(response["answer"])

                #Visualization
                visualization = response["visualization"]

                st.subheader("📊 Visualization")

                if visualization.chart_type == "metric":

                    if response["results"] and visualization.y_column is not None:

                        value = response["results"][0][
                            visualization.y_column
                        ]

                        st.metric(
                            label=visualization.title,
                            value=value
                        )
                
                elif visualization.chart_type == "bar":

                    df = pd.DataFrame(
                        response["results"]
                    )

                    fig = px.bar(
                        df,
                        x=visualization.x_column,
                        y=visualization.y_column,
                        title=visualization.title
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )
                
                elif visualization.chart_type == "line":

                    df = pd.DataFrame(
                        response["results"]
                    )

                    fig = px.line(
                        df,
                        x=visualization.x_column,
                        y=visualization.y_column,
                        title=visualization.title,
                        markers=True 
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )
                
                elif visualization.chart_type == "pie":

                    df = pd.DataFrame(
                        response["results"]
                    )

                    fig = px.pie(
                        df,
                        names=visualization.x_column,
                        values=visualization.y_column,
                        title=visualization.title
                    )

                    st.plotly_chart(
                        fig,
                        width="stretch"
                    )
                else:
                    st.info(
                        "A table is the most appropriate visualization "
                        "for this result."
                    )


                #Results
                st.subheader("📊 Results")

                if response["results"]:

                    dataframe = pd.DataFrame(
                        response["results"]
                    )

                    st.dataframe(
                        dataframe,
                        width="stretch"
                    )

                else:
                    st.info(
                        "No matching records were found."
                    )

                #SQL 
                with st.expander(
                    "🔍 View generated SQL"
                ):

                    st.code(
                        response["sql"],
                        language="sql"
                    )

                #Explaination
                with st.expander(
                    "ℹ️ SQL explaination"
                ):

                    st.write(
                        response["explaination"]
                    )

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )

                with st.expander("🔧 Technical details"):

                    st.exception(e)
