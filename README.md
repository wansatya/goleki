# 🔍 Goleki - DIY Search Engine with Groq LLM

A powerful, Perplexity-like search engine built with FastAPI and Groq's LLM API. Get real-time, AI-powered search results with source attribution.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)
![Groq](https://img.shields.io/badge/Groq-0.3.1-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- 🌐 Real-time web search with source attribution
- 🤖 AI-powered answer generation using Groq's hosted LLM
- ⚡ Asynchronous processing for fast responses
- 📊 Background task management and monitoring
- 🛡️ Robust error handling and logging
- 📄 Auto-generated API documentation
- 🧪 Testing utilities included

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/wansatya/goleki.git
cd goleki
```

2. Create and activate virtual environment:
```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # Unix/MacOS
# or
.venv\Scripts\activate     # Windows

# Or using standard venv
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
# Using UV (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🔑 Configuration

Required environment variables:
```env
GROQ_API_KEY=your-groq-api-key-here
SERPER_API_KEY=your-serper-api-key-here
```

## 🚀 Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the API:
- API documentation: http://localhost:8000/docs
- ReDoc interface: http://localhost:8000/redoc

## 📡 API Endpoints

### POST `/query`
Submit a new search query:
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "what is quantum computing?", "num_results": 3}'
```

### GET `/query/{query_id}`
Get results for a specific query:
```bash
curl "http://localhost:8000/query/your-query-id"
```

### GET `/status`
Check system status:
```bash
curl "http://localhost:8000/status"
```

### GET `/health`
Check API health:
```bash
curl "http://localhost:8000/health"
```

## 💡 Example Response

```json
{
  "query_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "query": "what is quantum computing?",
  "answer": "Comprehensive answer from Groq LLM...",
  "sources": [
    {
      "url": "https://example.com",
      "title": "Source Title",
      "snippet": "Source snippet..."
    }
  ],
  "created_at": "2024-11-01T07:08:21.376599",
  "processing_time": 2.45
}
```

## ⚙️ Advanced Configuration

Customize the application by modifying these parameters:
- `MAX_TOKENS`: Maximum tokens for LLM response (default: 2000)
- `TEMPERATURE`: LLM temperature setting (default: 0.3)
- `NUM_RESULTS`: Number of search results to process (default: 3)

## 📈 Performance Optimization

- Uses async processing for concurrent operations
- Implements efficient task management
- Includes request timing middleware
- Optimizes content extraction and processing

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/awesome-feature`
3. Commit your changes: `git commit -m 'Add awesome feature'`
4. Push to the branch: `git push origin feature/awesome-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for their amazing LLM API
- [FastAPI](https://fastapi.tiangolo.com/) for the awesome framework
- [Serper](https://serper.dev/) for search API capabilities

## 📞 Support

- Create an issue for bug reports or feature requests
- Star the repo if you find it useful
- Follow for updates and more projects

---

Built with ❤️ by WanSatya Foundation