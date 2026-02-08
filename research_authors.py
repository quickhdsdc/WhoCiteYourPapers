import csv
import json
import re
import time
import os


def load_unique_authors(filepath, limit=None):
    """
    Reads the CSV and extracts unique authors based on name/profile.
    Returns a dictionary of author_key -> {name, profile, details...}
    """
    unique_authors = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                profile = row.get("Citing Author Profile", "")
                name = row.get("Citing Author Name", "")
                
                # Create a unique key
                key = profile if profile else name
                if not key: continue
                
                if key not in unique_authors:
                    unique_authors[key] = {
                        "name": name,
                        "profile": profile,
                        "original_affiliation": row.get("Citing Author Affiliation", ""),
                        "citations": row.get("Citing Author Total Citations", "0"),
                        "h_index": row.get("Citing Author h-index", "0"),
                        "sample_citing_paper": row.get("Citing Paper Title", "")
                    }
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return {}

    authors_list = list(unique_authors.values())
    
    # Sort by citations desc just in case
    authors_list.sort(key=lambda x: int(x["citations"]) if x["citations"].isdigit() else 0, reverse=True)
    
    if limit:
        return authors_list[:limit]
    return authors_list

def extract_tag(text, tag):
    """Extracts content between [TAG] and [/TAG]"""
    pattern = f"\\[{tag}\\](.*?)\\[/{tag}\\]"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def research_author_google(client, model, author_data):
    name = author_data["name"]
    affiliation = author_data["original_affiliation"]
    sample_paper = author_data["sample_citing_paper"]
    profile_link = author_data["profile"]
    
    prompt = f"""
    Please research the following academic author:
    Name: {name}
    Profile Link: {profile_link}
    Known Affiliation (from paper): {affiliation}
    Representative Citing Paper: {sample_paper}

    Use Google Search to find their current details. 
    I need:
    1. Full Name
    2. Current Affiliation (Institution)
    3. Academic Title (e.g., Professor, Associate Professor, Researcher, PhD Candidate)
    4. A direct link to their faculty page, lab page, or Google Scholar profile (if different from the input).

    Output the result STRICTLY in the following format with tags:
    [Name] Full Name [/Name]
    [Affiliation] Current Institution Name [/Affiliation]
    [Title] Academic Title [/Title]
    [LINK] URL to profile [/LINK]
    """
    
    try:
        from google import genai
        from google.genai import types
        
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            temperature=1.0
        )
        
        print(f"  Searching for {name} using Google GenAI...")
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        
        # Extract text from candidates
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            parts = response.candidates[0].content.parts
            text_parts = [p.text for p in parts if p.text]
            return "".join(text_parts)
            
        return ""

    except Exception as e:
        print(f"  Error researching {name}: {e}")
        return ""

def main():
    input_file = "high_impact_citing_authors.csv"
    output_file = "high_impact_authors_enriched.csv"
    
    import sys
    limit = None
    if "--limit" in sys.argv:
        try:
            limit = int(sys.argv[sys.argv.index("--limit")+1])
        except:
            pass

    authors = load_unique_authors(input_file, limit)
    print(f"Loaded {len(authors)} authors to research.")
    
    # Initialize Google Client
    try:
        from google import genai
        # Try to load API key from config.toml manually or just rely on Env
        # Let's try to find it in config.toml for convenience
        import toml
        api_key = os.environ.get("GOOGLE_API_KEY")
        model = "gemini-2.0-flash-exp" # Default fallback
        
        try:
            with open("config/config.toml", "r") as f:
                cfg = toml.load(f)
                gemini_cfg = cfg.get("llm", {}).get("gemini", {})
                if gemini_cfg.get("api_key"):
                    api_key = gemini_cfg.get("api_key")
                if gemini_cfg.get("model"):
                    model = gemini_cfg.get("model")
        except:
            pass
            
        if not api_key:
             print("Warning: GOOGLE_API_KEY not found in env or config/config.toml. Client init might fail.")
             
        client = genai.Client(api_key=api_key)
        print(f"Initialized Google GenAI Client with model: {model}")
        
    except ImportError:
        print("Error: google-genai package not installed.")
        return
    except Exception as e:
        print(f"Failed to initialize Google client: {e}")
        return

    enriched_data = []
    
    for i, author in enumerate(authors):
        print(f"[{i+1}/{len(authors)}] Researching {author['name']}...")
        
        raw_response = research_author_google(client, model, author)
        
        # Parse tags
        extracted_name = extract_tag(raw_response, "Name")
        extracted_aff = extract_tag(raw_response, "Affiliation")
        extracted_title = extract_tag(raw_response, "Title")
        extracted_link = extract_tag(raw_response, "LINK")
        
        # Fallback to original if extraction fails or returns empty
        final_name = extracted_name if extracted_name else author["name"]
        final_aff = extracted_aff if extracted_aff else author["original_affiliation"]
        
        enriched_record = author.copy()
        enriched_record["Researched Name"] = final_name
        enriched_record["Researched Affiliation"] = final_aff
        enriched_record["Researched Title"] = extracted_title
        enriched_record["Researched Link"] = extracted_link
        enriched_record["Raw LLM Response"] = raw_response
        
        enriched_data.append(enriched_record)
        
        # Intermediate save
        if i % 5 == 0:
             save_csv(enriched_data, output_file)
             
        # Be polite to rate limits
        time.sleep(2) # Slightly longer sleep for GenAI just in case

    # Final save
    save_csv(enriched_data, output_file)
    print(f"Completed research. Saved to {output_file}")

def save_csv(data, filename):
    if not data: return
    keys = list(data[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    main()
