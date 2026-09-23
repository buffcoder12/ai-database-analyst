# AI Database Analyst

### Natural Language to SQL with Gemini, PostgreSQL & Streamlit

An AI-powered database analyst that allows users to interact with a PostgreSQL database using natural-language questions.

The application uses Google's Gemini API to understand user questions, retrieve the relevant database schema, generate structured SQL queries, validate them for safety, execute them against PostgreSQL, automatically correct failed queries, and return natural-language answers with suitable data visualizations.

---

## 🚀 Project Overview

Traditional database analysis often requires users to know SQL before they can retrieve information from a database.

This project provides a natural-language interface over a relational database.

Instead of writing:

```sql
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 3;
```

a user can simply ask:

> Show the top 3 products by revenue.

The system understands the question, identifies the relevant database tables, generates the SQL query, validates it, executes it, and presents the result in an understandable format.

---

# ✨ Features

- Natural-language to SQL generation
- PostgreSQL database integration
- Gemini-powered SQL generation
- Schema-aware query generation
- Question-specific schema retrieval
- Database schema introspection
- Pydantic structured outputs
- Read-only SQL validation
- Protection against destructive SQL operations
- Automatic SQL correction after execution errors
- Natural-language answer generation
- Automatic visualization selection
- Interactive Streamlit interface
- Query result caching
- Cache expiration
- Query history during the session
- Performance monitoring
- Detailed execution metrics
- Automated testing with pytest

---

# 🏗️ System Architecture

```mermaid
flowchart TD

    A[User Question] --> B[Streamlit UI]

    B --> C[Query Engine]

    C --> D[Database Schema]

    D --> E[Schema Retriever]

    E --> F[Gemini SQL Generator]

    F --> G[Pydantic Structured Output]

    G --> H[SQL Validator]

    H -->|Valid SQL| I[PostgreSQL]

    H -->|Invalid SQL| J[Reject Query]

    I --> K[Query Results]

    K --> L[Answer Generator]

    K --> M[Visualization Generator]

    L --> N[Streamlit Response]

    M --> N

    I --> O[Performance Monitoring]

    F --> O

    C --> P[Query Cache]

    P --> B

    I -->|Execution Error| Q[SQL Corrector]

    Q --> H
```

---

# 🔄 Application Workflow

The application follows this pipeline:

```text
User Question
      ↓
Streamlit Interface
      ↓
Query Engine
      ↓
Database Schema Retrieval
      ↓
Relevant Schema Retrieval
      ↓
Gemini SQL Generation
      ↓
Pydantic Structured Output
      ↓
SQL Validation
      ↓
PostgreSQL Execution
      ↓
Query Results
      ↓
 ┌───────────────────────┐
 │                       │
 ↓                       ↓
Answer Generation    Visualization
 │                       │
 └───────────┬───────────┘
             ↓
       Streamlit Output
```

If the generated SQL fails during execution:

```text
SQL Execution Error
        ↓
SQL Corrector
        ↓
Corrected SQL
        ↓
SQL Validator
        ↓
PostgreSQL
```

---

# 🧠 Schema-Aware SQL Generation

One of the important parts of the application is the schema retrieval system.

Instead of unnecessarily providing the entire database schema to the LLM for every question, the application identifies the database tables that are relevant to the user's question.

For example:

### Question

```text
What is the total revenue?
```

Relevant schema:

```text
order_items
```

---

### Question

```text
Which customers have placed orders?
```

Relevant schema:

```text
customers
orders
```

---

### Question

```text
Show the top 3 products by revenue.
```

Relevant schema:

```text
products
order_items
```

This makes the SQL generation process more focused and reduces unnecessary schema information in the prompt.

---

# 🤖 Gemini SQL Generation

The application uses Google's Gemini API through the `google-genai` Python SDK.

The SQL generation process uses structured output with Pydantic.

The generated response follows a structured format:

```text
SQL
+
Explanation
```

Example:

```json
{
    "sql": "SELECT SUM(quantity * unit_price) AS total_revenue FROM order_items;",
    "explaination": "Calculates the total revenue from all order items."
}
```

The generated SQL is then passed to the SQL validation layer before it can reach the database.

---

# 🛡️ SQL Safety

The application is designed as a read-only database analyst.

Only the following SQL statement types are allowed:

```text
SELECT
WITH
```

The validator rejects potentially destructive operations such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
EXEC
EXECUTE
```

Multiple SQL statements are also rejected.

For example, a query such as:

```sql
SELECT * FROM customers;
DROP TABLE customers;
```

will not be accepted because the application allows only one SQL statement.

This provides an additional safety layer between the LLM and the database.

> The application should still use a database user with appropriate read-only permissions in a production environment.

---

# 🔧 Automatic SQL Correction

LLM-generated SQL can occasionally fail because of:

- Incorrect column names
- Incorrect joins
- SQL syntax errors
- Incorrect assumptions about the schema

When SQL execution fails, the application sends the original question, generated SQL, database error, and schema information to the SQL correction component.

The correction flow is:

```text
Generated SQL
      ↓
SQL Validation
      ↓
PostgreSQL
      ↓
Execution Error
      ↓
SQL Corrector
      ↓
Corrected SQL
      ↓
SQL Validation
      ↓
PostgreSQL
```

The corrected query is validated again before execution.

---

# 🗄️ Database

The project uses PostgreSQL.

Database name:

```text
ai_sql_db
```

## Database Schema

### Customers

```text
customers
├── customer_id
├── name
├── email
├── city
└── created_at
```

### Products

```text
products
├── product_id
├── name
├── category
├── price
└── stock
```

### Orders

```text
orders
├── order_id
├── customer_id
├── order_date
└── status
```

### Order Items

```text
order_items
├── order_item_id
├── order_id
├── product_id
├── quantity
└── unit_price
```

## Relationships

```text
customers
    │
    │ customer_id
    ↓
orders
    │
    │ order_id
    ↓
order_items
    │
    │ product_id
    ↓
products
```

The application automatically reads table, column, primary-key, and foreign-key information from PostgreSQL's `information_schema`.

---

# 📊 Visualization

After executing a query, the application determines an appropriate visualization based on the returned data.

Supported visualization types include:

- Metric
- Bar Chart
- Line Chart
- Pie Chart
- Table

Examples:

### Single numeric result

```text
What is the total revenue?
```

The application can display the result as a metric.

### Category + numeric result

```text
Show revenue by product.
```

The application can display the result as a bar chart.

### Date + numeric result

```text
Show revenue over time.
```

The application can display the result as a line chart.

---

# ⚡ Query Caching

The application includes an in-memory query cache.

Cache characteristics:

```text
Maximum cache entries: 50
Cache expiration: 1 hour
```

The cache key takes the following into account:

- Normalized user question
- Relevant tables
- Relevant columns
- Column data types
- Primary keys
- Foreign keys

This helps prevent unnecessary repeated SQL generation and database execution for the same question and schema context.

The Streamlit interface also provides an option to clear the cache.

---

# 📈 Performance Monitoring

The application tracks execution time across different stages of the pipeline.

Tracked operations include:

```text
Schema retrieval
Schema relevance retrieval
Cache lookup
SQL generation
SQL validation
Database execution
Answer generation
Visualization generation
SQL correction
Total execution time
```

The Streamlit interface provides:

- Total execution time
- SQL generation time
- Database execution time
- Detailed performance information

Example:

```text
Total Time       0.842s
SQL Generation   0.391s
Database         0.018s
```

The actual values depend on the query, API response time, database performance, and system resources.

---

# 🧪 Testing

The project includes automated tests using `pytest`.

Testing covers components such as:

- SQL validation
- Query caching
- Schema retrieval
- LLM integration

Run the test suite with:

```bash
pytest -v
```

---

# 🛠️ Tech Stack

## Programming Language

- Python

## AI / LLM

- Google Gemini API
- `google-genai`
- Pydantic

## Database

- PostgreSQL
- `psycopg`

## Application

- Streamlit

## Data Processing

- Pandas

## Visualization

- Plotly

## SQL Processing

- SQLParse

## Testing

- pytest

## Configuration

- python-dotenv

---

# 📁 Project Structure

```text
ai-text-to-sql/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── schema.py
│   ├── llm.py
│   ├── sql_generator.py
│   ├── sql_validator.py
│   ├── sql_corrector.py
│   ├── query_engine.py
│   ├── answer_generator.py
│   ├── gemini_client.py
│   ├── visualization.py
│   ├── chart_generator.py
│   ├── query_cache.py
│   ├── schema_retriever.py
│   ├── observability.py
│   ├── ui.py
│   └── main.py
│
├── database/
│   └── init.sql
│
├── tests/
│   ├── __init__.py
│   ├── test_llm.py
│   ├── test_query_cache.py
│   ├── test_schema_retriever.py
│   └── test_sql_validator.py
│
├── test_gemini.py
├── test_schema.py
├── test_schema_retriever.py
├── run.py
│
├── .env.example
├── .gitignore
├── pyrefly.toml
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-database-analyst.git
```

Move into the project directory:

```bash
cd ai-database-analyst
```

---

## 2. Create a virtual environment

On Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as a reference.

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ai_sql_db
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Important

Never commit your real `.env` file.

The project `.gitignore` already excludes:

```text
.env
```

---

# 🗄️ PostgreSQL Setup

Make sure PostgreSQL is installed and running.

Create a database named:

```text
ai_sql_db
```

Then execute the SQL initialization script:

```text
database/init.sql
```

The script creates the required tables and inserts sample data.

Your PostgreSQL connection should match the `DATABASE_URL` in your `.env` file.

---

# ▶️ Running the Application

Start the Streamlit application with:

```bash
python -m streamlit run app/main.py
```

The application will open in your browser.

---

# 💬 Example Questions

Once the application is running, try questions such as:

```text
What is the total revenue?
```

```text
Which customers have placed orders?
```

```text
Show the top 3 products by revenue.
```

```text
How many completed orders are there?
```

```text
Show revenue by product.
```

```text
What products are currently in stock?
```

```text
Show the number of orders for each customer.
```

---

# 💡 Example End-to-End Query

### User Question

```text
Show the top 3 products by revenue.
```

### Generated SQL

```sql
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 3;
```

### Processing

```text
User Question
      ↓
Schema Retriever
      ↓
Gemini
      ↓
SQL
      ↓
SQL Validator
      ↓
PostgreSQL
      ↓
Results
      ↓
Answer Generator
      ↓
Visualization
      ↓
Streamlit
```

---

# 🖥️ Application Interface

The Streamlit application provides:

- Natural-language question input
- Query execution
- Generated SQL
- SQL explanation
- Natural-language answer
- Database results
- Automatic visualization
- Performance metrics
- Query history
- Cache information
- Cache clearing

---

# 🔒 Security Considerations

This project is designed for controlled, read-only database analysis.

Security-related measures include:

- Read-only SQL statement validation
- Blocking destructive SQL keywords
- Rejecting multiple SQL statements
- Environment-variable-based credential management
- `.env` excluded from Git
- SQL validation before database execution

For production deployment, additional controls should be implemented, including:

- Dedicated read-only database credentials
- Authentication
- Authorization
- Rate limiting
- Query timeouts
- Database connection restrictions
- Monitoring and logging

---

# ⚠️ Limitations

The current implementation has several limitations:

- SQL generation depends on the selected LLM.
- Gemini API access requires an API key.
- The current implementation is designed around PostgreSQL.
- Query cache is stored in memory.
- Cache data is lost when the application restarts.
- Complex database questions may still require additional prompt or schema improvements.
- AI-generated SQL should be tested carefully before connecting the application to production databases.

---

# 🔮 Future Improvements

Potential future improvements include:

- Multi-database support
- MySQL and SQLite support
- Persistent query caching
- Database connection pooling
- Query execution timeout
- Query cost estimation
- Advanced schema retrieval
- Conversation memory
- User authentication
- Role-based database access
- Query feedback and correction from users
- More advanced visualization recommendations
- Docker deployment
- Cloud deployment
- Production monitoring
- Improved evaluation framework for generated SQL

---

# 🎯 Project Goals

The main goal of this project is to explore how modern LLMs can be integrated with relational databases to create an AI-powered database analyst.

The project combines:

```text
Natural Language Processing
        +
Large Language Models
        +
Schema Retrieval
        +
Structured Outputs
        +
SQL Generation
        +
SQL Validation
        +
PostgreSQL
        +
Automatic Error Correction
        +
Data Visualization
        +
Observability
```

into a single practical AI engineering application.

---

# 📚 Key AI Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

- LLM integration
- Prompt engineering
- Structured LLM outputs
- Pydantic validation
- Schema-aware generation
- Retrieval-based context selection
- SQL generation
- SQL safety validation
- Error correction loops
- Caching
- Observability
- Data visualization
- Automated testing
- Streamlit application development
- PostgreSQL integration

---



