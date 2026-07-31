import sys
from colorama import init, Fore, Style
from langgraph.checkpoint.memory import MemorySaver
from graph.graph import graph_builder
from config import GOOGLE_API_KEY
import warnings

warnings.filterwarnings('ignore')
init(autoreset=True)

def main():
    print(Fore.GREEN + Style.BRIGHT + "========================================")
    print(Fore.GREEN + Style.BRIGHT + "  AFL AI System (Week 6 Day 4)")
    print(Fore.GREEN + Style.BRIGHT + "========================================")
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_openai_api_key_here":
        print(Fore.RED + "Error: GOOGLE_API_KEY is not set in .env")
        sys.exit(1)
        
    memory = MemorySaver()
    agent = graph_builder.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "main_thread"}}
    print(Fore.YELLOW + "Type 'quit' or 'exit' to end the conversation.\n")
    
    while True:
        try:
            user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL)
            if user_input.lower() in ["quit", "exit"]:
                break
                
            print(Fore.MAGENTA + "Routing & processing..." + Style.RESET_ALL)
            
            response = agent.invoke({"messages": [("user", user_input)]}, config)
            final_msg = response.get("final_response")
            
            if not final_msg:
                final_msg = response["messages"][-1].content
                
            print(Fore.GREEN + "AFL Agent: " + Style.RESET_ALL + final_msg + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"System Error: {str(e)}")

if __name__ == "__main__":
    main()
