from anthropic import AI_PROMPT, HUMAN_PROMPT, AsyncAnthropic

from config import claude_api


class Claude:
    def __init__(self):
        self.model = "claude-3-sonnet-20240229"
        self.temperature = 0.7
        self.cutoff = 50
        self.client = AsyncAnthropic(api_key=claude_api)
        self.prompt = ""
        self.initial_prompt = {"role": "user", "content": "You are a dog. Pretend to be one."}  # Add this line to store the system prompt
        self.chat_history = []  # Add this line to store the chat history

    
    def reset(self):
        self.prompt = ""
        self.chat_history = []  # Add this line to store the chat history


    def revert(self):
        self.prompt = self.prompt[: self.prompt.rfind(HUMAN_PROMPT)]

    def change_model(self, model):
        valid_models = {"claude-3-opus-20240229","claude-3-sonnet-20240229", "claude-2", "claude-instant-1"}
        if model in valid_models:
            self.model = model
            return True
        return False

    def change_temperature(self, temperature):
        try:
            temperature = float(temperature)
        except ValueError:
            return False
        if 0 <= temperature <= 1:
            self.temperature = temperature
            return True
        return False

    def change_cutoff(self, cutoff):
        try:
            cutoff = int(cutoff)
        except ValueError:
            return False
        if cutoff > 0:
            self.cutoff = cutoff
            return True
        return False
    
    #FOXY_OLD
    # async def send_message_stream_old(self, message):
    #     self.prompt = f"{self.prompt}{HUMAN_PROMPT} {message}{AI_PROMPT}"
    #     response = await self.client.completions.create(
    #         prompt=self.prompt,
    #         model=self.model,
    #         temperature=self.temperature,
    #         stream=True,
    #         max_tokens_to_sample=100000,
    #     )
    #     answer = ""
    #     async for data in response:
    #         answer = f"{answer}{data.completion}"
    #         yield answer
    #     self.prompt = f"{self.prompt}{answer}"

    #FOXY_NEW
            # async def send_message_stream(self, message):
            #     async with self.client.messages.stream(
            #         max_tokens=1024,
            #         messages=[
            #             {
            #                 "role": "user",
            #                 "content": "Say hello there!",
            #             }
            #         ],
            #         model="claude-3-opus-20240229",
            #     ) as stream:
            #         async for text in stream.text_stream:
            #             print(text, end="", flush=True)
            #         print()
        
            #     accumulated = await stream.get_final_message()
            #     yield accumulated.model_dump_json(indent=2)
                

    async def send_message_stream(self, message):
        self.chat_history.append({"role": "user", "content": message})

        if self.initial_prompt:
            messages = self.initial_prompt + self.chat_history
        else:
            messages = self.chat_history

        async with self.client.messages.stream(
            max_tokens=1024,
            messages=messages,
            model=self.model,
            temperature=self.temperature,
        ) as stream:
            async for text in stream.text_stream:
                print(text, end="", flush=True)

            print()
            accumulated = await stream.get_final_message()
            # self.chat_history.append(accumulated.message)
            yield accumulated.model_dump_json(indent=2)
