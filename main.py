import os
from audio_manager import AudioManager
from interviewer_agent import InterviewerAgent
from resume_parser import ResumeParser
from colorama import Fore, Style

def main():
    print(f"{Fore.CYAN}=== AI INTERVIEW SIMULATOR (FULL CYCLE) ==={Style.RESET_ALL}")
    
    # 1. Initialize
    try:
        audio_bot = AudioManager()
        ai_agent = InterviewerAgent()
    except Exception as e:
        print(f"Init Error: {e}")
        return

    # 2. Inputs
    print("\n--- STEP 1: CONTEXT SETUP ---")
    jd = input(f"{Fore.GREEN}Paste Job Description > {Style.RESET_ALL}")
    
    resume_path = input(f"{Fore.GREEN}Resume File Path > {Style.RESET_ALL}").strip('\"')
    resume_text = ResumeParser.extract_text(resume_path)
    if not resume_text: return

    # 3. Self Intro
    print("\n--- STEP 2: SELF INTRODUCTION ---")
    print("Interviewer: Tell me about yourself.")
    input(f"{Fore.YELLOW}Press Enter to record Intro...{Style.RESET_ALL}")
    
    self_intro = audio_bot.listen_and_transcribe()
    if not self_intro or len(self_intro) < 5: 
        self_intro = "Candidate provided a brief introduction."

    # 4. Start Interview (Generates Question 1)
    print(f"\n{Fore.MAGENTA}AI is analyzing Resume & Intro...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}PHASE 1: RESUME & PROJECT SCREENING (4 Questions){Style.RESET_ALL}")
    
    ai_question = ai_agent.start_interview(jd, resume_text, self_intro)
    print(f"\n{Fore.BLUE}Interviewer (Q1): {ai_question}{Style.RESET_ALL}")

    # 5. Q&A Loop (We need 8 more questions to reach 9 total)
    # The loop handles processing the answer to Q1...Q8 and generating Q2...Q9
    total_questions = 9
    
    for i in range(total_questions - 1):
        # Record Answer
        input(f"\n{Fore.YELLOW}Press Enter to answer...{Style.RESET_ALL}")
        user_answer = audio_bot.listen_and_transcribe()
        
        if not user_answer or len(user_answer) < 2:
            print("Silence detected. Moving on...")
            user_answer = "I am not sure."

        print(f"{Fore.MAGENTA}Thinking...{Style.RESET_ALL}")
        
        # Generate Next Question
        # 'i' represents the index of the answer we just gave.
        ai_question = ai_agent.analyze_response_and_ask_next(user_answer, i)
        
        # Visual Helper to show Phase Switch
        question_number = i + 2
        if question_number == 5:
            print(f"\n{Fore.CYAN}PHASE 2: TECHNICAL ASSESSMENT (5 Questions){Style.RESET_ALL}")

        print(f"\n{Fore.BLUE}Interviewer (Q{question_number}): {ai_question}{Style.RESET_ALL}")

    # 6. Final Answer (Answer to Q9)
    input(f"\n{Fore.YELLOW}Press Enter to answer the final question...{Style.RESET_ALL}")
    final_answer = audio_bot.listen_and_transcribe()
    
    # We send this final answer to the AI so it's included in the history, 
    # but we don't need a new question back.
    if final_answer:
        print(f"{Fore.MAGENTA}Submitting final answer...{Style.RESET_ALL}")
        ai_agent.chat_session.send_message(f"Candidate Answer to Final Question: {final_answer}")

    # 7. Feedback Report
    print(f"\n{Fore.CYAN}=== INTERVIEW COMPLETE. GENERATING HIRING DECISION ==={Style.RESET_ALL}")
    try:
        report = ai_agent.generate_final_feedback()
        print(f"\n{Fore.WHITE}{report}{Style.RESET_ALL}")
    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    main()