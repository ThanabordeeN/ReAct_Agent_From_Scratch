# ReAct Agent - AI Assistant with Tool Usage

A Python-based AI assistant that implements the ReAct (Reasoning and Acting) pattern, allowing it to use tools and reason about their usage while answering questions.

## Features

- Uses OpenAI's GPT models for natural language processing
- Implements ReAct pattern (Reasoning, Acting, Observing)
- Supports custom tool registration
- Handles multi-turn conversations
- Parses and executes actions with arguments

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/react-agent.git
cd react-agent
```

2. Install dependencies:
```bash
pip install openai python-dotenv
```

3. Set up environment variables:
Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Example

```python
from main import AIAgent

# Create and configure agent
agent = AIAgent()

# Register tools
def search_price(brand: str) -> str:
    return f"Price of {brand} is $400"

def search_reviews(brand: str) -> str:
    return f"Reviews of {brand} are good"

agent.register_tool("search_price", search_price)
agent.register_tool("search_reviews", search_reviews)

# Run a query
question = "How much does a Lenovo Laptop costs and what are the reviews?"
answer = agent.query(question)
print(f"Answer: {answer}")
```

### Configuration Options

- `model`: Specify the OpenAI model (default: "gpt-4-mini")
- `temperature`: Set response creativity (default: 0)
- `max_turns`: Maximum conversation turns (default: 10)

## Adding Custom Tools

You can extend the agent's capabilities by registering custom tools:

```python
def custom_tool(param: str) -> str:
    """Tool description"""
    return f"Result for {param}"

agent.register_tool("custom_tool", custom_tool)
```

## Architecture

The agent operates in a loop of:
1. Thought - Reasoning about the question
2. Action - Executing a tool
3. Observation - Processing tool results
4. Answer - Providing final response

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License

MIT License - See LICENSE file for details