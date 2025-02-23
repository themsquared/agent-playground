# LLM Playground

A full-stack application for evaluating and comparing different Language Model providers (OpenAI, Anthropic, Ollama) through a unified interface. Features include interactive chat, model evaluation, cost tracking, and performance analysis.

## Features

- 🤖 Support for multiple LLM providers:
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Ollama (local models)
- 📊 Model evaluation and comparison
- 💰 Cost tracking and analysis
- 📈 Performance visualization
- 🎯 Action system for structured outputs
- 🌡️ Weather integration demo
- 🌓 Dark/Light theme support

## Prerequisites

- Python 3.11+
- Node.js 16+
- PostgreSQL 13+
- [Ollama](https://ollama.ai/) for local model support

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RevMgmt
   ```

2. **Set up Python environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   ```bash
   # Using Docker (recommended)
   docker run --name postgres -e POSTGRES_PASSWORD=mlfuntimes -e POSTGRES_USER=postgres -p 5432:5432 -d postgres
   
   # Create the evaluation database
   docker exec -it postgres psql -U postgres -c "CREATE DATABASE evaluation;"
   ```

4. **Install and configure Ollama**
   - Install Ollama from [ollama.ai](https://ollama.ai/)
   - Pull desired models:
     ```bash
     ollama pull mistral
     ollama pull llama2
     ollama pull codellama
     # Add other models as needed
     ```

5. **Set up environment variables**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your API keys and configuration
   # Required for full functionality:
   # - OPENAI_API_KEY
   # - ANTHROPIC_API_KEY
   # - OPENWEATHER_API_KEY (for weather demo)
   ```

6. **Set up frontend**
   ```bash
   cd Playground/frontend
   npm install
   ```

## Running the Application

1. **Start the backend**
   ```bash
   # From the root directory
   python run.py
   ```

2. **Start the frontend**
   ```bash
   # In a new terminal, from Playground/frontend
   npm start
   ```

3. **Access the application**
   - Open [http://localhost:3000](http://localhost:3000) in your browser
   - Backend API will be available at [http://localhost:5000](http://localhost:5000)

## Usage

1. **Playground Tab**
   - Interactive chat interface
   - Select different models
   - Execute structured actions
   - Track token usage and costs

2. **Evaluation Tab**
   - Compare multiple models
   - Create evaluation test sets
   - Rank responses
   - View performance metrics and cost analysis

3. **Settings Tab**
   - Configure API keys
   - Toggle theme
   - Manage application settings

## Project Structure

```
RevMgmt/
├── Playground/
│   ├── frontend/          # React frontend
│   ├── llm_providers/     # LLM provider implementations
│   ├── actions/           # Action system
│   └── routes/            # API routes
├── requirements.txt       # Python dependencies
└── run.py                # Application entry point
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 