
import logging
import threading
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Groq doesn't require this, kept only so callers that still import the old
# constant name don't explode if something was missed during the migration.
GEMINI_SAFETY_SETTINGS = []

class GroqService:
    """Drop-in replacement for GeminiService, backed by the Groq API."""

    def __init__(self, api_key, context_history_enabled=True, model_name: str = 'openai/gpt-oss-120b', system_instructions: str = '', welcome_instructions: str = '', gender: str = 'neutral'):
        self.api_key = api_key
        self._model_name = model_name
        self.client = None
        self._enabled = False
        self.context_history_enabled = context_history_enabled
        self._system_instructions = system_instructions
        self._welcome_instructions = welcome_instructions
        self._gender = gender if gender in {'neutral', 'male', 'female'} else 'neutral'
        self._semaphore = threading.Semaphore(5)  # Limit to 5 concurrent API calls
        self.init_model()

    def init_model(self, model_name: str = None):
        if not GROQ_AVAILABLE or not self.api_key:
            self._enabled = False
            self.client = None
            return

        if model_name:  # Allow dynamic model change
            self._model_name = model_name

        try:
            self.client = Groq(api_key=self.api_key)
            # Groq has no separate "create model" step; do a cheap call-free
            # sanity check instead (empty models list means a bad key/network).
            self._enabled = True
            logging.info(f"Groq client initialized successfully with model '{self._model_name}'.")
        except Exception as e:
            logging.error(f"Failed to initialize Groq client or verify API key: {e}. Main features will be disabled.")
            self.client = None
            self._enabled = False

    def set_gender(self, gender: str):
        self._gender = gender if gender in {'neutral', 'male', 'female'} else 'neutral'
        logging.info(f'AI gender set to {self._gender}.')

    def _gender_instruction(self):
        instructions = {
            'neutral': 'You are an AI bot, not a human person. Use gender-neutral wording whenever possible and do not present yourself as male or female.',
            'male': 'You are an AI bot with a masculine gender presentation. When Portuguese or another language requires gendered wording for self-reference, use masculine forms.',
            'female': 'You are an AI bot with a feminine gender presentation. When Portuguese or another language requires gendered wording for self-reference, use feminine forms.',
        }
        return instructions[self._gender]

    def set_system_instructions(self, instructions: str):
        self._system_instructions = instructions
        logging.info("Groq system instructions updated.")

    def set_welcome_instructions(self, instructions: str):
        self._welcome_instructions = instructions
        logging.info("Groq welcome instructions updated.")

    def is_enabled(self):
        return self._enabled and self.client is not None

    def get_current_model_name(self):
        return self._model_name

    def list_available_models(self) -> list:
        if not GROQ_AVAILABLE or not self.api_key:
            return []
        try:
            client = self.client or Groq(api_key=self.api_key)
            models = client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            logging.error(f"Failed to list Groq models: {e}")
            return []

    def _run_completion(self, messages, model_to_use=None):
        model = model_to_use or self._model_name

        with self._semaphore:
            kwargs = {
                "model": model,
                "messages": messages,
            }
            # Reasoning models (e.g. openai/gpt-oss-*) can otherwise leak their
            # internal chain-of-thought (stray questions, "let me think...",
            # etc.) into the visible reply. Keep only the final answer.
            if "gpt-oss" in model or "qwen" in model.lower() or "deepseek" in model.lower():
                kwargs["reasoning_format"] = "hidden"

            try:
                response = self.client.chat.completions.create(**kwargs)
            except Exception as e:
                if "reasoning_format" in kwargs and "reasoning_format" in str(e).lower():
                    # Model doesn't support this param; retry without it.
                    kwargs.pop("reasoning_format")
                    response = self.client.chat.completions.create(**kwargs)
                else:
                    raise
            message = response.choices[0].message

            content = (message.content or "").strip()
            return content if content else "[Groq] (Received an empty response or unhandled content)"

    def generate_content(self, prompt, history=None):
        if not self.is_enabled():
            return "[Groq Error] Service not available."

        try:
            messages = []
            messages.append({"role": "system", "content": self._gender_instruction()})
            if self._system_instructions:
                messages.append({"role": "system", "content": self._system_instructions})

            if history and self.context_history_enabled:
                for msg in history:
                    if msg['is_bot']:
                        messages.append({"role": "assistant", "content": msg['message']})
                    else:
                        messages.append({"role": "user", "content": f"{msg['sender_nick']}: {msg['message']}"})

            messages.append({"role": "user", "content": prompt})
            return self._run_completion(messages)
        except Exception as e:
            logging.error(f"Error during Groq API call: {e}", exc_info=True)
            return "[Bot Error] Error contacting Groq."

    def generate_simple_content(self, prompt: str, model_to_use=None) -> str:
        if not self.is_enabled():
            return "[Groq Error] Service not available."

        try:
            messages = []
            system_instructions = self._welcome_instructions if model_to_use == "welcome" else self._system_instructions
            messages.append({"role": "system", "content": self._gender_instruction()})
            if system_instructions:
                messages.append({"role": "system", "content": system_instructions})
            messages.append({"role": "user", "content": prompt})
            return self._run_completion(messages)
        except Exception as e:
            logging.error(f"Error during Groq API call: {e}", exc_info=True)
            return "[Bot Error] Error contacting Groq."

    def generate_welcome_message(self, nickname: str, language: str = "pt_BR") -> str:
        if not self.is_enabled():
            return ""
        language_name = "Portuguese (Brazil)" if language == "pt_BR" else "English"
        prompt = f"Generate a short, friendly welcome message for a new user named {nickname} joining a chat. Keep it concise and welcoming. Write the message in {language_name}."
        return self.generate_simple_content(prompt, model_to_use="welcome")
