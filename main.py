import os
import time
from audio_manager import AudioManager
from interviewer_agent import InterviewerAgent
from colorama import Fore, Style

def main():
    print(f"{Fore.CYAN}=== AI INTERVIEW SIMULATOR ==={Style.RESET_ALL}")
    
    # 1. Check for API Key
    if not os.getenv("GEMINI_API_KEY"):
        # You can get a key from https://aistudio.google.com/app/apikey
        print(f"{Fore.RED}Error: GEMINI_API_KEY not set.{Style.RESET_ALL}")
        print("Please create a .env file and add: GEMINI_API_KEY=your_key_here")
        return

    # 2. Initialize our Modules
    try:
        audio_bot = AudioManager()
        ai_agent = InterviewerAgent()
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    # 3. Get Job Description
    print("Please paste the Job Description (JD) you are applying for:")
    jd = input(f"{Fore.GREEN}JD > {Style.RESET_ALL}")
    
    print(f"\n{Fore.MAGENTA}Initializing Interview...{Style.RESET_ALL}")
    
    # 4. Start the Interview Loop
    # The AI generates the first question based on the JD
    ai_question = ai_agent.start_interview(jd)
    print(f"\n{Fore.BLUE}Interviewer: {ai_question}{Style.RESET_ALL}")

    questions_limit = 5  # Limit the demo to 5 questions
    count = 0

    while count < questions_limit:
        input(f"\n{Fore.YELLOW}Press Enter to start recording your answer...{Style.RESET_ALL}")
        
        # Listen to student
        user_answer = audio_bot.listen_and_transcribe()

        if not user_answer:
            print("Sorry, I didn't catch that. Let's try again.")
            continue # Skip the rest of the loop and try recording again

        # Send answer to AI and get next question
        print(f"\n{Fore.MAGENTA}Analyzing answer...{Style.RESET_ALL}")
        ai_question = ai_agent.analyze_response_and_ask_next(user_answer)
        
        print(f"\n{Fore.BLUE}Interviewer: {ai_question}{Style.RESET_ALL}")
        count += 1

    # 5. Final Evaluation
    print(f"\n{Fore.CYAN}=== INTERVIEW COMPLETE. GENERATING FEEDBACK ==={Style.RESET_ALL}")
    feedback = ai_agent.generate_final_feedback()
    
    print(f"\n{Fore.WHITE}{feedback}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()