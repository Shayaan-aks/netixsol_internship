import sys
from colorama import init, Fore, Style
from langgraph.checkpoint.memory import MemorySaver
from chains.chat_chain import builder
from config import OPENAI_API_KEY

init(autoreset=True)

def main():
    print(Fore.GREEN + Style.BRIGHT + "========================================")
    print(Fore.GREEN + Style.BRIGHT + "  AFL Conversational AI Assistant")
    print(Fore.GREEN + Style.BRIGHT + "========================================")
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print(Fore.RED + "Error: OPENAI_API_KEY is not set in .env")
        sys.exit(1)
        
    memory = MemorySaver()
    agent = builder.compile(checkpointer=memory)
    
    config = {"configurable": {"thread_id": "1"}}
    
    print(Fore.YELLOW + "Type 'quit' or 'exit' to end the conversation.\n")
    
    while True:
        try:
            user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL)
            if user_input.lower() in ["quit", "exit"]:
                break
                
            print(Fore.MAGENTA + "Agent thinking..." + Style.RESET_ALL)
            
            events = agent.stream(
                {"messages": [("user", user_input)]}, 
                config,
                stream_mode="values"
            )
            
            final_message = None
            for event in events:
                final_message = event["messages"][-1]
            
            if final_message and hasattr(final_message, "content"):
                print(Fore.GREEN + "AFL Agent: " + Style.RESET_ALL + final_message.content + "\n")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}")

if __name__ == "__main__":
    main()
