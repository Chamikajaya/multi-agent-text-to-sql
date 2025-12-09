# Agentic Text-to-SQL

A production-ready multi-agent system that converts natural language questions into SQL queries, executes them against an e-commerce database, and presents results with optional visualizations.

<div align="center">
  <video src="demo.mp4" controls muted autoplay loop style="max-width: 100%; height: auto;"></video>
</div>


## 🌟 Features

- **Natural Language to SQL**: Ask questions in plain English, get SQL automatically
- **Multi-Agent Architecture**: Specialized agents for validation, generation, execution, error correction, and analysis
- **Automatic Error Correction**: Self-healing with retry logic when SQL errors occur
- **Intelligent Visualizations**: Automatically generates charts when data would benefit from visualization
- **Interactive Chat Interface**: Built with Chainlit for a seamless user experience
- **Production-Ready Code**: Modular, well-documented, and maintainable

## 🏗️ Architecture

The system uses a **LangGraph** multi-agent workflow with seven specialized agents:

1. **Guardrails Agent**: Validates input and filters out-of-scope questions
2. **SQL Generator Agent**: Converts natural language to SQLite queries
3. **SQL Executor Agent**: Executes queries and formats results
4. **Error Corrector Agent**: Automatically fixes SQL errors with retry logic
5. **Analysis Agent**: Converts query results to natural language answers
6. **Visualization Decision Agent**: Determines if charts would help
7. **Visualizer Agent**: Generates Plotly charts when appropriate

![Architecture Diagram](./text2sql_workflow.png)


## 📋 Requirements

- Python 3.10 or higher
- Google AI API key (for Gemini model)
- CSV data files in the `data/` directory. You can download the data from the Looker e-commerce database - https://www.kaggle.com/datasets/mustafakeser4/looker-ecommerce-bigquery-dataset

## 🚀 Quick Start

### 1. Clone the Repository

```bash
cd agentic-text-to-sql
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Google AI API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 5. Initialize Database

The database will be automatically created on first run, but you can initialize it manually:

```bash
python -m src.database.db_manager
```

### 6. Run the Application

```bash
chainlit run app.py
```

The Chainlit interface will open in your browser at `http://localhost:8000`

## 💬 Example Questions

Try asking questions like:

**📊 Analytics**
- What are the top 10 selling products?
- Show me monthly revenue trends for 2023
- What is the total revenue by product category?

**👥 Customer Analysis**
- How many users are from Atlanta?
- Show me the distribution of users by traffic source

**📦 Product Queries**
- Which brands have the highest sales?
- What are the most popular product categories?
- Show me products with the highest profit margin

**📈 Trends**
- How has revenue changed over time?
- Show me seasonal patterns in sales


## 🗄️ Database Schema

The e-commerce database contains 7 tables:

- **products**: Product catalog with pricing and categories
- **users**: Customer demographics and registration data
- **orders**: Order transactions and status tracking
- **order_items**: Individual items within orders (for revenue)
- **inventory_items**: Warehouse stock tracking
- **distribution_centers**: Warehouse locations
- **events**: Web analytics and user behavior

## 🔧 Configuration

### LLM Settings

Edit `src/config.py` to customize:

- Model selection (default: `gemini-2.5-flash`)
- Temperature (default: `0` for deterministic responses)
- Retry attempts (default: `3` for error correction)

### Database Settings

- Default database location: `db_data/ecommerce.db`
- CSV data source: `data/*.csv`

### Chainlit UI

Customize the interface in `.chainlit/config.toml`:

- Theme settings
- Session timeout
- UI layout options


## 🤝 Contributing

This is a production-ready codebase designed for:

- Easy maintenance and debugging
- Clear separation of concerns
- Extensibility for new features
- Comprehensive error handling

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

Built with:

- **LangChain & LangGraph**: Multi-agent orchestration
- **Google Gemini**: Language model
- **Chainlit**: Chat interface
- **Plotly**: Data visualizations
- **Pandas**: Data processing

---

**Built by Chamika Jayasinghe ❤️**
