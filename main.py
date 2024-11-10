import re
from dotenv import load_dotenv
from openai import OpenAI
import inspect
from typing import List, Optional, Callable, Dict
import csv
from io import StringIO

class AIAgent:
    """An AI agent that can use tools to answer questions through a chat interface."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize the AI agent with tools and OpenAI configuration.
        
        Args:
            model: The OpenAI model to use
            temperature: The sampling temperature for responses
        """
        _ = load_dotenv()
        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.tools: Dict[str, Callable] = {}
        self.messages = []
        self.action_re = re.compile(r'Action:\s*(\w+)\s*\((.*?)\)')
        
    def register_tool(self, name: str, func: Callable) -> None:
        """Register a tool that the agent can use."""
        self.tools[name] = func
        
    def _function_to_string(self, func: Callable) -> str:
        """Convert a function to its source code string."""
        return inspect.getsource(func)
        
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse comma-separated arguments handling quoted strings."""
        reader = csv.reader(StringIO(args_str))
        args = next(reader)
        return [arg.strip().strip('"\'') for arg in args]

    def setup_system_prompt(self) -> None:
        """Set up the system prompt with available tools."""
        prompt = """
        You run in a loop of Thought, Suggestions, Action, PAUSE, Observation.
        At the end of the loop you output an Answer
        Use Thought to describe your thoughts about the question you have been asked.
        Use Action to run one of the suitable actions available to you - then return 
        PAUSE.
        Observation will be the result of running those actions.

        Your available actions are:
        {}

        Example session:

        [Question: How much does a Lenovo Laptop costs?
        Thought: I should look the Laptop price using get_average_price
                        
        Action: get_average_price("Lenovo")
        PAUSE

        You will be called again with this:

        Observation: A lenovo laptop average price is $400

        You then output:

        Answer: A lenovo laptop costs $400
        ,
        Result: Thought: I need to find out both the price and the reviews for a Lenovo laptop. I will first search for the price and then look for the reviews.

        Action: search_price("Lenovo")
        PAUSE
        -- running search_price ['Lenovo']
        Observation: Price of Lenovo is $400
        Result: Action: search_reviews("Lenovo")
        PAUSE
        -- running search_reviews ['Lenovo']
        Observation: Reviews of Lenovo are good
        Result: Answer: A Lenovo laptop costs $400 and the reviews are good.
        Final answer: A Lenovo laptop costs $400 and the reviews are good.]

        """.strip()
        
        actions_str = [self._function_to_string(func) for func in self.tools.values()]
        system = prompt.format(actions_str)
        self.messages = [{"role": "system", "content": system}]

    def query(self, question: str, max_turns: int = 10) -> Optional[str]:
        """
        Process a question through multiple turns until getting final answer.
        
        Args:
            question: The input question to process
            max_turns: Maximum number of turns before timing out
            
        Returns:
            Optional[str]: The final answer or None if no answer found
        """
        self.setup_system_prompt()
        next_prompt = question
        
        try:
            for i in range(max_turns):
                self.messages.append({"role": "user", "content": next_prompt})
                result = self._execute()
                self.messages.append({"role": "assistant", "content": result})
                print(f"Result: {result}")
                
                if result.lower().startswith('answer:'):
                    return result.split('Answer:', 1)[1].strip()
                
                actions = [
                    self.action_re.match(a) for a in result.split('\n') 
                    if self.action_re.match(a)
                ]
                
                if actions:
                    action, args_str = actions[0].groups()
                    action_inputs = self._parse_arguments(args_str)
                    
                    tool = self.tools.get(action)
                    if not tool:
                        raise Exception(f"Unknown action: {action}")
                    
                    print(f" Calling Function {action} with {action_inputs}")
                    observation = tool(*action_inputs)
                    print(f"Observation: {observation}")
                    next_prompt = f"Observation: {observation}"
                else:
                    return None
                    
        except Exception as e:
            print(f"Error during query processing: {str(e)}")
            return None
        
        return None

    def _execute(self) -> str:
        """Execute a chat completion request."""
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=self.messages
        )
        return completion.choices[0].message.content

# Example usage:
if __name__ == "__main__":
    def search_price(brand: str) -> str:
        """Search for the price of a product."""
        return f"Price of {brand} is $400"
    
    def search_reviews(brand: str) -> str:
        """Search for the reviews of a product."""
        return f"Reviews of {brand} are good"


    # Create and configure agent
    agent = AIAgent()
    agent.register_tool("search_price", search_price)
    agent.register_tool("search_reviews", search_reviews)

    # Run a query
    question = "How much does a Lenovo Laptop costs and what are the reviews?"
    answer = agent.query(question)
    if answer:
        print(f"Final answer: {answer}")
    else:
        print("Could not find an answer")