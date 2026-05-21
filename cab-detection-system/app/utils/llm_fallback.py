import logging
import os
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
# pyrefly: ignore [missing-import]
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

class SafeChatOpenAI:
    """Wrapper around ChatOpenAI that falls back to rule-based parsing if the API call fails or is unauthorized."""
    
    def __init__(self, model: str = "gpt-4o", api_key: str = None, **kwargs):
        self.model_name = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.kwargs = kwargs
        self.real_model = None
        
        # Only try to instantiate real model if we have a key that looks like it could be valid
        if self.api_key and "your_openai" not in self.api_key:
            try:
                self.real_model = ChatOpenAI(model=self.model_name, api_key=self.api_key, **self.kwargs)
            except Exception as e:
                logger.warning("Failed to initialize ChatOpenAI: %s. Using local fallback.", e)

    def invoke(self, messages, *args, **kwargs):
        if not self.real_model:
            logger.info("OpenAI API key not set or invalid. Using local rule-based LLM fallback.")
            return self._mock_invoke(messages)
            
        try:
            return self.real_model.invoke(messages, *args, **kwargs)
        except Exception as e:
            # Check if it looks like an auth/401 error or quota issue
            err_msg = str(e)
            if "401" in err_msg or "invalid_api_key" in err_msg or "auth" in err_msg.lower():
                logger.warning("OpenAI API key is invalid/unauthorized (401). Falling back to rule-based parser.")
            else:
                logger.warning("OpenAI LLM invocation failed: %s. Falling back to rule-based parser.", e)
            return self._mock_invoke(messages)

    def _mock_invoke(self, messages):
        system_content = ""
        user_messages = []
        
        for msg in messages:
            # Accessing message types by class name or 'type' attribute
            msg_type = msg.__class__.__name__
            msg_content = getattr(msg, "content", str(msg))
            
            if msg_type == "SystemMessage":
                system_content = msg_content
            elif msg_type == "HumanMessage":
                user_messages.append(msg_content)
            elif msg_type == "AIMessage":
                pass
            else:
                role = getattr(msg, "type", "")
                if role == "system":
                    system_content = msg_content
                elif role == "human":
                    user_messages.append(msg_content)

        # 1. Check if this is the destination collection node
        if "extract the DESTINATION address" in system_content:
            last_msg = user_messages[-1].strip() if user_messages else ""
            dest = last_msg
            
            # Clean common formats
            if dest.lower().startswith("destination:"):
                dest = dest[len("destination:"):].strip()
            elif "to " in dest.lower():
                idx = dest.lower().rfind("to ")
                dest = dest[idx + 3:].strip()
                
            logger.info("Local LLM Mock extracted destination: '%s' (from raw input: '%s')", dest, last_msg)
            return AIMessage(content=dest)

        # 2. Check if this is the confirm ride node
        elif "confirm the ride" in system_content:
            last_msg = user_messages[-1].strip().lower() if user_messages else ""
            
            # Keyword matching
            if any(word in last_msg for word in ["yes", "confirm", "ok", "y", "sure", "correct", "accept", "proceed"]):
                logger.info("Local LLM Mock matched confirmation: YES ('%s')", last_msg)
                return AIMessage(content="CONFIRMED")
            elif any(word in last_msg for word in ["no", "cancel", "decline", "n", "stop"]):
                logger.info("Local LLM Mock matched confirmation: NO ('%s')", last_msg)
                return AIMessage(content="CANCELLED")
            else:
                # If neither, return confirmation query
                logger.info("Local LLM Mock asking for confirmation (input was: '%s')", last_msg)
                return AIMessage(content="Would you like to confirm this ride? (yes/no)")

        # Default fallback
        logger.info("Local LLM Mock default fallback response")
        return AIMessage(content="I'm here to help you book your cab.")
