import ollama
from rich.console import Console
from core.tools import search_web, scrape_web
from core.debug import log_debug

console = Console()

import datetime

current_date = datetime.date.today().strftime("%Y-%m-%d")

SYSTEM_PROMPT = f"""You are a smart Terminal Assistant with Internet Access.
Current Date: {current_date}
Knowledge Cutoff: 2023

CRITICAL: You DO NOT know real-time facts (Sports stats, Prices, Weather, News).
If a user asks about anything that changes over time (like "how many goals", "price of", "who is"), you MUST SEARCH.

FORCE SEARCHING:
If you are unsure, SEARCH. Do not guess.

To search, reply with ONLY this format:
SEARCH: <exact query>

To read a specific link (deep dive), reply with:
read: <url>

Examples:
User: "Price of Bitcoin?"
You: SEARCH: current price of bitcoin

User: "Ronaldo goals?"
You: SEARCH: Cristiano Ronaldo total goals stats

User: "Who won the super bowl?"
You: SEARCH: Super Bowl winner 2025

Keep queries SIMPLE and KEYWORD-BASED. Avoid long sentences.
"""

def think(history):
    """
    Sends chat history to Ollama. Handles autonomous tool usage.
    """
    try:
        # 0. Prepare Messages with System Prompt
        # We don't want to duplicate the system prompt in the perm history if possible,
        # but we need it for the AI to know it can search.
        # Let's prepend it for this inference session.
        working_memory = [{'role': 'system', 'content': SYSTEM_PROMPT}] + history
        
        # 1. Manual User Overrides (search: / read:)
        last_user_msg = history[-1]['content']
        
        if last_user_msg.lower().startswith("search:"):
            query = last_user_msg[7:].strip()
            result = search_web(query)
            working_memory.append({'role': 'system', 'content': f"Search Result: {result}"})
            
        elif last_user_msg.lower().startswith("read:"):
            url = last_user_msg[5:].strip()
            result = scrape_web(url)
            working_memory.append({'role': 'system', 'content': f"Page Content: {result}"})
            
        # 1.5 Temporal/Fact Helper
        # Small models (phi4) sometimes forget to search. We force them if we detect keywords.
        # 1.5 Temporal/Fact Helper
        triggers = ["today", "now", "current", "latest", "price", "score", "goals", "weather", "news", "who is", "exact", "number", "how many", "give me", "time"]
        
        # SPECIAL LOGIC: Time queries need Deep Reading because snippets often lack the clock.
        if "time" in last_user_msg.lower():
             working_memory.append({'role': 'system', 'content': "System Hint: For TIME queries, search snippets are often empty. You MUST reply with 'read: <url>' after searching if the snippet doesn't show the exact time."})
        elif any(t in last_user_msg.lower() for t in triggers):
             working_memory.append({'role': 'system', 'content': "System Hint: The user is asking for real-time info. You MUST output 'SEARCH: <query>' to find the answer. Do not answer from memory."})

        # 2. First Pass (AI Decides)
        response = ollama.chat(model='phi4', messages=working_memory)
        content = response['message']['content']
        
        # 3. Check for Autonomous Search Command
        if "SEARCH:" in content:
            # Extract query (simple parsing)
            try:
                query = content.split("SEARCH:")[1].split("\n")[0].strip()
                console.print(f"[bold magenta]Auto-Searching:[/bold magenta] {query}")
                
                # Run Tool
                search_result = search_web(query)
                
                # Feed result back with EXTREME PREJUDICE/FORCE
                working_memory.append({'role': 'assistant', 'content': content})
                system_injection = f"""
CRITICAL UPDATE:
Search Tool Result: "{search_result}"

INSTRUCTION:
1. ANSWER DIRECTLY. Do NOT say "I cannot provide real-time info" or "I recommend checking".
2. The Search Result below IS the real-time info. USE IT.
3. If the snippet says "960 goals", your answer is "He has 960 goals".
4. If the snippet says "12:00 PM", your answer is "It is 12:00 PM".
5. Cite the source (e.g., "[Source: TimeAndDate]").

If the snippet does NOT contain the answer (e.g., just says "Current local time..."), then reply with:
read: <url_from_snippet>
"""
                working_memory.append({'role': 'system', 'content': system_injection})
                
                # LOGGING
                log_debug("BRAIN INPUT (Auto-Search)", f"System Injection:\n{system_injection}")
                
                # Second Pass (Final Answer)
                final_response = ollama.chat(model='phi4', messages=working_memory)
                final_content = final_response['message']['content']
                
                # RECURSION CHECK: Did the second pass ask to READ?
                if "read:" in final_content.lower():
                    # Recursive call to handle the read command immediately
                    # We append the assistant's request to "read" to history? 
                    # Actually, we can just process it here.
                    import re
                    url_match = re.search(r"read:\s*(https?://\S+)", final_content, re.IGNORECASE)
                    if url_match:
                        url = url_match.group(1).strip(")") # Strip trailing parenthesis if present
                        console.print(f"[bold magenta]Auto-Reading (Deep Dive):[/bold magenta] {url}")
                        page_content = scrape_web(url)
                        
                        working_memory.append({'role': 'assistant', 'content': final_content})
                        working_memory.append({'role': 'system', 'content': f"Page Content: {page_content[:2000]}...\n\nAnswer the user now."})
                        
                        pass3 = ollama.chat(model='phi4', messages=working_memory)
                        return pass3['message']['content']

                log_debug("BRAIN OUTPUT", final_content)
                return final_content
                
            except Exception as e:
                log_debug("ERROR", f"Auto-Search failed: {e}")
                return f"Error in Auto-Search: {e}"
                
        # 3. Check for Autonomous Search OR Read Command
        if "SEARCH:" in content:
            # ... (Existing Search Logic) ...
            pass # (I will keep existing search logic here, but wrapped in a check)
            
        # 4. Check for Autonomous READ Command (New)
        if "read:" in content.lower():
            try:
                # Extract URL (simple parsing)
                # It might look like "Please read: https://..." or just "read: https://..."
                import re
                url_match = re.search(r"read:\s*(https?://\S+)", content, re.IGNORECASE)
                
                if url_match:
                    url = url_match.group(1)
                    console.print(f"[bold magenta]Auto-Reading:[/bold magenta] {url}")
                    
                    # Run Tool
                    page_content = scrape_web(url)
                    
                    # Feed result back using the "Force" template
                    working_memory.append({'role': 'assistant', 'content': content})
                    working_memory.append({'role': 'system', 'content': f"""
CRITICAL UPDATE:
Page Content: "{page_content[:2000]}..."

INSTRUCTION:
The answer is in the content above.
Extract the exact time/number/fact and answer the user directly.
"""})
                    # Second Pass (Final Answer)
                    final_response = ollama.chat(model='phi4', messages=working_memory)
                    final_content = final_response['message']['content']
                    
                    log_debug("BRAIN OUTPUT (Auto-Read)", final_content)
                    return final_content
            except Exception as e:
                log_debug("ERROR", f"Auto-Read failed: {e}")
                
        return content

    except Exception as e:
        return f"Error connecting to Brain: {e}"
