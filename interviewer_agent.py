import os
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables
load_dotenv()

class InterviewerAgent:
    def __init__(self):
        """
        Initializes the AI model with Auto-Discovery logic.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print(f"{Fore.RED}DEBUG: No API Key found in environment variables!{Style.RESET_ALL}")
            raise ValueError("API Key not found.")
        else:
            masked_key = api_key[:4] + "..." + api_key[-4:]
            print(f"{Fore.YELLOW}DEBUG: API Key loaded: {masked_key}{Style.RESET_ALL}")

        genai.configure(api_key=api_key)
        self.model = None

        # Strategy 1: Try specific, fast models first
        preferred_models = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-001',
            'gemini-pro',
            'gemini-1.0-pro'
        ]

        print(f"{Fore.CYAN}Configuring AI Model...{Style.RESET_ALL}")

        # 1. Try Hardcoded names
        for model_name in preferred_models:
            try:
                print(f"Strategy 1: Testing {model_name}...", end=" ")
                temp_model = genai.GenerativeModel(model_name)
                temp_model.generate_content("Test")
                self.model = temp_model
                print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
                break 
            except Exception:
                print(f"{Fore.RED}Failed.{Style.RESET_ALL}")
                continue
        
        # 2. Auto-Discovery (If Strategy 1 failed)
        if self.model is None:
            print(f"\n{Fore.YELLOW}Strategy 2: Auto-detecting available models for your key...{Style.RESET_ALL}")
            try:
                for m in genai.list_models():
                    # We only want text generation models
                    if 'generateContent' in m.supported_generation_methods:
                        print(f"Found available model: {m.name}...", end=" ")
                        try:
                            temp_model = genai.GenerativeModel(m.name)
                            temp_model.generate_content("Test")
                            self.model = temp_model
                            print(f"{Fore.GREEN}Connected!{Style.RESET_ALL}")
                            break
                        except Exception as e:
                            print(f"{Fore.RED}Access Denied ({e}){Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Could not list models: {e}{Style.RESET_ALL}")

        # 3. Final Check
        if self.model is None:
            print(f"\n{Fore.RED}CRITICAL ERROR: Your API Key is valid, but has no access to ANY text generation models.{Style.RESET_ALL}")
            print("Possible causes:")
            print("1. You need to enable 'Generative Language API' in Google Cloud Console.")
            print("2. Your billing project is frozen.")
            print("3. You are in a region where Gemini is not yet supported.")
            raise ValueError("No working models found.")

        self.history = []

    def start_interview(self, job_description):
        initial_prompt = f"""
        You are an expert technical interviewer. 
        Here is the Job Description (JD) for the role: 
        "{job_description}"
        
        Your goal is to interview a candidate. 
        1. Ask relevant questions based on the JD.
        2. Keep questions concise (1-2 sentences max).
        3. Do not give feedback yet, just ask the first question.
        """
        
        self.chat_session = self.model.start_chat(history=[])
        response = self.chat_session.send_message(initial_prompt)
        return response.text

    def analyze_response_and_ask_next(self, candidate_response):
        prompt = f"""
        The candidate answered: "{candidate_response}"
        
        1. Briefly acknowledge the answer.
        2. Ask the next relevant question based on the JD and their previous answer.
        3. If the answer was too vague, ask a follow-up clarifying question.
        """
        
        response = self.chat_session.send_message(prompt)
        return response.text

    def generate_final_feedback(self):
        prompt = """
        The interview is over. Please provide a detailed evaluation report of the candidate.
        Include:
        1. Strengths shown.
        2. Weaknesses/Areas for improvement.
        3. Rating out of 10 for the specific role in the JD.
        4. Final Hiring Recommendation (Yes/No).
        """
        
        response = self.chat_session.send_message(prompt)
        return response.text