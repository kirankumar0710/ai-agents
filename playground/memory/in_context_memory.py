# in_context_memory.py
import anthropic

client = anthropic.Anthropic()


class InContextAgent:
    def __init__(self):
        self.messages = []  # This IS the memory
        self.system = (
            "You are a helpful assistant. Remember everything the user tells you."
        )

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=self.system,
            messages=self.messages,
        )

        assistant_msg = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_msg})
        return assistant_msg

    def show_memory_size(self):
        total_chars = sum(len(m["content"]) for m in self.messages)
        print(f"Memory: {len(self.messages)} messages, ~{total_chars} chars")


# Test it
agent = InContextAgent()
print(agent.chat("My name is XYZ and I'm from Bangalore."))
print(agent.chat("I'm building AI agents for a startup."))
print(agent.chat("What do you remember about me?"))  # Should recall both facts

# chat() #1  → user msg + assistant msg  = 2
# chat() #2  → user msg + assistant msg  = 4
# chat() #3  → user msg + assistant msg  = 6

agent.show_memory_size()
