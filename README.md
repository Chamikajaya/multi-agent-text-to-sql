# Agentic Text-to-SQL

A production-ready multi-agent system that converts natural language questions into SQL queries, executes them against an e-commerce database, and presents results with optional visualizations.

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

```
User Query → Guardrails → SQL Gen → Execute → Analysis → Viz Decision → Visualizer
                   ↓                      ↓
              (invalid)           (error → Correction → retry)
                   ↓                      
                  END
```

## 📋 Requirements

- Python 3.10 or higher
- Google AI API key (for Gemini model)
- CSV data files in the `data/` directory

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
- How many users are from California?
- What is the average age of customers by state?
- Show me the distribution of users by traffic source

**📦 Product Queries**
- Which brands have the highest sales?
- What are the most popular product categories?
- Show me products with the highest profit margin

**📈 Trends**
- What are the daily order trends for last month?
- How has revenue changed over time?
- Show me seasonal patterns in sales

## 📁 Project Structure

```
agentic-text-to-sql/
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configuration and settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py           # Database initialization
│   │   └── schema.py               # Schema definitions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── state.py                # Graph state definition
│   │   └── responses.py            # Pydantic response models
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── guardrails.py           # Input validation
│   │   ├── sql_generator.py        # SQL generation
│   │   ├── sql_executor.py         # Query execution
│   │   ├── error_corrector.py      # Error fixing
│   │   ├── analyzer.py             # Result analysis
│   │   ├── viz_decision.py         # Visualization decision
│   │   └── visualizer.py           # Chart generation
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── workflow.py             # LangGraph workflow
│   │   ├── helpers.py              # Routing functions
│   │   └── streaming.py            # Async streaming
│   └── utils/
│       ├── __init__.py
│       └── llm.py                  # LLM initialization
├── data/                            # CSV data files
├── db_data/                         # SQLite database (auto-created)
├── .chainlit/
│   └── config.toml                 # Chainlit configuration
├── app.py                          # Main Chainlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

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

## 🧪 Testing

Test individual components:

```bash
# Test database initialization
python -m src.database.db_manager

# Test LLM connection
python -c "from src.utils.llm import get_llm; llm = get_llm(); print('✓ LLM initialized')"

# Test graph creation
python -c "from src.graph.workflow import create_text2sql_graph; g = create_text2sql_graph(); print('✓ Graph created')"
```

## 🐛 Troubleshooting

### Database Not Found

If you see database errors, initialize it manually:

```bash
python -m src.database.db_manager
```

### API Key Issues

Ensure your `.env` file exists and contains a valid `GOOGLE_API_KEY`:

```bash
# Check if .env exists
cat .env  # Linux/Mac
type .env  # Windows
```

### Import Errors

Make sure you're in the virtual environment and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is busy, specify a different port:

```bash
chainlit run app.py --port 8001
```

## 📝 Code Comments

The codebase includes comprehensive inline comments explaining:

- **Function purposes**: What each function does
- **Parameter descriptions**: Input and output specifications
- **Complex logic**: Step-by-step explanations of algorithms
- **Design decisions**: Why certain approaches were chosen

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

**Ready to explore your data? Start the app and ask away! 🚀**
