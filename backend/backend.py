import ollama
from groq import Groq
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
OLLAMA_MODEL = "gemma3:4b"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
# Increased temperature for more creativity
DEFAULT_TEMPERATURE = 0.75

# Base template that can be used without personalization
BASE_TEMPLATE = """Hi!

I'm part of the Organizing Committee for Global Diplomatic Summit-Lucknow MUN 2025. We're inviting bright minds to be a part of our upcoming conference that focuses on global challenges and leadership development.

The conference will feature multiple specialized committees addressing pressing international issues, with opportunities for both beginners and experienced delegates.

Would you be interested in learning more about the committees, awards, and registration process? I'd be happy to provide additional information.

Looking forward to hearing from you!

Best regards,
[Your Name]
Organizing Committee
Global Diplomatic Summit-Lucknow MUN 2025"""

# Updated System Prompt for Personalization & Creativity
SYSTEM_PROMPT = """You are an assistant that personalizes invitation messages with moderate creativity.
Given a template message and specific details (like a name and other optional parameters), rewrite the message to include the details naturally.
Paraphrase the template creatively (around 50% flexibility) while maintaining the core information, key event details (Global Diplomatic Summit-Lucknow MUN 2025, focus on global challenges/leadership), and the overall purpose of the invitation.
Include any provided custom fields such as committee preferences, experience level, special invitations, deadlines, etc. naturally in the text.
Adjust the tone according to the specified preference (Formal, Semi-formal, or Conversational) if provided, otherwise use a semi-formal tone.
Do not add unrelated information. Only output the personalized message."""

def get_base_template():
    """Returns the basic template message for direct use without personalization."""
    return BASE_TEMPLATE

# --- Ollama Functions ---

def check_ollama_availability():
    """Checks if the Ollama service is running and the specified model is available."""
    try:
        client = ollama.Client()
        client.list() # Check connection
        models = client.list()['models']
        model_names = [m['name'].split(':')[0] for m in models] # Get base model names
        ollama_base_model = OLLAMA_MODEL.split(':')[0]
        if any(ollama_base_model in name for name in model_names):
             logging.info(f"Ollama is available and model '{OLLAMA_MODEL}' (or base '{ollama_base_model}') found.")
             return True
        else:
            logging.warning(f"Ollama is running, but model '{OLLAMA_MODEL}' not found. Available: {[m['name'] for m in models]}")
            return False
    except Exception as e:
        logging.warning(f"Ollama check failed: {e}. Ollama might not be running or reachable.")
        return False

def rewrite_with_ollama(details: Dict[str, Any]) -> str | None:
    """Generates a personalized message using Ollama based on the template and details."""
    try:
        client = ollama.Client()
        
        # Build customization prompt with all available details
        customization_details = "Personalize for:\n"
        for key, value in details.items():
            if key != 'tone': # Don't list tone as a detail to include
                customization_details += f"- {key}: {value}\n"
            
        # Construct the user prompt with template and details
        user_prompt = f"Template:\n{BASE_TEMPLATE}\n\n{customization_details}\n\nRewrite the template including these details naturally, using the specified tone if provided."

        # Adjust temperature based on tone preference, otherwise use default
        temperature = DEFAULT_TEMPERATURE
        if "tone" in details:
            if details["tone"] == "Formal":
                temperature = 0.4  # Lower for formal
            elif details["tone"] == "Conversational":
                temperature = 0.8  # Higher for conversational

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt},
            ],
            options={'temperature': temperature}
        )
        rewritten_text = response['message']['content']
        logging.info("Message personalized using Ollama.")
        
        # Basic check to ensure name is included (can be improved)
        if 'name' in details and details['name'].lower() not in rewritten_text.lower():
            logging.warning(f"Ollama output might be missing the name: {details['name']}")
            # Prepend name if missing
            rewritten_text = f"Hi {details['name']},\n\n{rewritten_text}"
        return rewritten_text.strip()
    except Exception as e:
        logging.error(f"Error during Ollama personalization: {e}")
        return None

# --- Groq Functions ---

def rewrite_with_groq(details: Dict[str, Any]) -> str | None:
    """Generates a personalized message using Groq based on the template and details."""
    # Check if the key was loaded successfully by dotenv
    if not os.getenv("GROQ_API_KEY"):
        logging.error("GROQ_API_KEY not found in environment variables or .env file.")
        return None
    try:
        client = Groq() # Assumes GROQ_API_KEY is loaded into env by load_dotenv()
        
        # Build customization prompt with all available details
        customization_details = "Personalize for:\n"
        for key, value in details.items():
            if key != 'tone': # Don't list tone as a detail to include
                customization_details += f"- {key}: {value}\n"
            
        # Construct the user prompt with template and details
        user_prompt = f"Template:\n{BASE_TEMPLATE}\n\n{customization_details}\n\nRewrite the template including these details naturally, using the specified tone if provided."

        # Adjust temperature based on tone preference, otherwise use default
        temperature = DEFAULT_TEMPERATURE
        if "tone" in details:
            if details["tone"] == "Formal":
                temperature = 0.4  # Lower for formal
            elif details["tone"] == "Conversational":
                temperature = 0.8  # Higher for conversational

        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=512,  # Increased max tokens for more detailed responses
            top_p=1,
            stream=False,
            stop=None,
        )
        rewritten_text = completion.choices[0].message.content
        logging.info("Message personalized using Groq.")
        
        # Basic check to ensure name is included (can be improved)
        if 'name' in details and details['name'].lower() not in rewritten_text.lower():
            logging.warning(f"Groq output might be missing the name: {details['name']}")
            # Optionally, prepend the name if missing, or handle differently
            # rewritten_text = f"Hi {details['name']}, {rewritten_text}"
        return rewritten_text.strip()
    except Exception as e:
        logging.error(f"Error during Groq personalization: {e}")
        return None

# --- Main Rewriting Logic ---

def generate_personalized_message(details: Dict[str, Any]) -> str | None:
    """
    Generates a personalized message using Ollama if available, otherwise falls back to Groq.

    Args:
        details: A dictionary containing personalization details (e.g., {'name': 'Alex'}).

    Returns:
        The personalized message, or None if both services fail.
    """
    if not details or 'name' not in details:
        logging.error("Details dictionary must include at least a 'name'.")
        return None

    logging.info(f"Attempting to generate personalized message for: {details['name']}...")

    use_ollama = check_ollama_availability()

    personalized_message = None
    if use_ollama:
        logging.info("Using Ollama for personalization.")
        personalized_message = rewrite_with_ollama(details)

    if personalized_message is None: # If Ollama failed or wasn't available
        logging.info("Ollama failed or unavailable. Trying Groq.")
        # No need to check os.environ here, rewrite_with_groq handles it after load_dotenv
        personalized_message = rewrite_with_groq(details)

    if personalized_message:
        logging.info("Personalization successful.")
        return personalized_message
    else:
        logging.error("Failed to personalize message using both Ollama and Groq.")
        return None

# --- Example Usage (Optional - can be removed or called from app.py) ---
if __name__ == '__main__':
    # Make sure Ollama is running in the background if you want to test it:
    # ollama serve &
    # Ensure you have the Groq API key set in your .env file

    # Example of using the basic template
    print("\n=== Basic Template ===")
    print(get_base_template())

    # Example of personalization with minimal details
    person_details = {"name": "Alex"}
    print(f"\n=== Generating message for: {person_details['name']} ===")
    personalized_msg = generate_personalized_message(person_details)

    if personalized_msg:
        print(f"\nPersonalized Message:\n{personalized_msg}")
    else:
        print("\nMessage generation failed.")

    # Example with more customization details
    person_details_2 = {
        "name": "Priya Sharma",
        "institution": "Delhi University",
        "committee": "UNSC",
        "experience_level": "Advanced",
        "special_invite": "Based on your outstanding performance at JNUMUN",
        "tone": "Formal"
    }
    print(f"\n=== Generating message with custom fields for: {person_details_2['name']} ===")
    personalized_msg_2 = generate_personalized_message(person_details_2)
    if personalized_msg_2:
        print(f"\nPersonalized Message:\n{personalized_msg_2}")
    else:
        print("\nMessage generation failed.")

