import os
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()

class InterviewerAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key not found. Please set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=api_key)
        self.model = None

        # 1. Back to the model we KNOW works for you
        possible_models = [
            'gemini-2.5-flash',      # It connected before, so let's use it
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-pro'
        ]
        
        print(f"{Fore.CYAN}Configuring AI Model...{Style.RESET_ALL}")
        
        for model_name in possible_models:
            try:
                print(f"Testing {model_name}...", end=" ")
                temp_model = genai.GenerativeModel(
                    model_name,
                    # 2. Maximize tokens to delay the cutoff as much as possible
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7, 
                        max_output_tokens=8000 
                    )
                )
                temp_model.generate_content("Test")
                self.model = temp_model
                print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
                break 
            except Exception:
                print(f"{Fore.RED}Failed.{Style.RESET_ALL}")
                continue
        
        if not self.model:
            raise ValueError("CRITICAL: No working Gemini models found.")

        self.chat_session = None

    def start_interview(self, job_description, resume_text, self_intro):
        """
        Initializes the interview.
        """
        clean_jd = job_description.strip()
        # Truncate resume slightly to save context window space
        clean_resume = resume_text[:10000].strip() 
        clean_intro = self_intro.strip()

        system_prompt = f"""
        You are an expert Technical Interviewer.
        
        CONTEXT:
        1. JD: "{clean_jd}"
        2. RESUME: "{clean_resume}"
        3. INTRO: "{clean_intro}"

        YOUR INTERVIEW PLAN (9 Questions Total):
        - Questions 1-4: Ask strictly about the projects, experience, and gaps in the RESUME.
        - Questions 5-9: Ask strictly about the technical skills required in the JOB DESCRIPTION.
        
        CURRENT STEP:
        The candidate has just given their self-introduction.
        Acknowledge it briefly, then ASK QUESTION #1 (Resume Focus).
        """
        
        self.chat_session = self.model.start_chat(history=[])
        response = self.chat_session.send_message(system_prompt)
        return self._safe_get_text(response)

    def analyze_response_and_ask_next(self, candidate_response, current_question_index):
        """
        Decides the topic based on the question index.
        """
        next_q_num = current_question_index + 2

        instruction = ""
        if next_q_num <= 4:
            instruction = f"User just answered Q{next_q_num-1}. Now ask Question #{next_q_num} focusing on RESUME/PROJECTS."
        elif next_q_num <= 9:
            instruction = f"User just answered Q{next_q_num-1}. Now ask Question #{next_q_num} focusing on TECHNICAL JD SKILLS."
        else:
            instruction = "The interview is complete. Thank the candidate and say you will generate the report."

        prompt = f"""
        Candidate Answer: "{candidate_response}"
        
        SYSTEM INSTRUCTION: {instruction}
        Keep the question concise (1-2 sentences).
        """
        
        response = self.chat_session.send_message(prompt)
        return self._safe_get_text(response)

    def generate_final_feedback(self):
        """
        Generates the detailed final report with Yes/No verdict.
        """
        prompt = """
        SYSTEM INSTRUCTION: STOP roleplaying. 
        TASK: Generate a rigorous Hiring Evaluation Report based on the entire session.
        
        FORMAT REQUIRED:
        
        1. 📄 RESUME & INTRO ANALYSIS
           - Did the intro cover key highlights?
           - Are the resume projects legitimate based on their answers?
           
        2. 🧠 TECHNICAL KNOWLEDGE EVALUATION
           - Python/Coding Skills: [Weak/Average/Strong]
           - Theoretical Knowledge: [Weak/Average/Strong]
           (Cite specific examples from the interview)
           
        3. 🏆 FINAL VERDICT
           - Hiring Recommendation: [YES / NO]
           
        4. ⭐ OVERALL RATING
           - [ X / 10 ]
        """
        response = self.chat_session.send_message(prompt)
        return self._safe_get_text(response)

    def _safe_get_text(self, response):
        """
        CRASH PROTECTION: This is the critical fix.
        Even if the model stops early (finish_reason=2), this extracts whatever text exists.
        """
        try:
            return response.text
        except Exception:
            # If standard access fails, try to dig into the candidates list manually
            try:
                if response.candidates and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text
            except:
                pass
            return "Error: AI response was blocked or empty. (But the app didn't crash!)"