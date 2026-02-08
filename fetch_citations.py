import requests
import bibtexparser
import time
import urllib.parse
import json

def load_api_key(filepath="api key.txt"):
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Proceeding without API key (rate limits may apply).")
        return None

def load_papers_from_bib(bib_path="my.bib"):
    with open(bib_path, "r", encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return bib_database.entries

def fetch_citations(doi, api_key=None):
    if not doi:
        return []
        
    paper_id = "DOI:" + urllib.parse.quote(doi)
    base = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
    
    # Try fetching with detailed author fields first (including affiliations)
    # Using explicit citingPaper prefix for clarity
    detailed_fields = "citingPaper.title,citingPaper.year,citingPaper.venue,citingPaper.abstract,isInfluential,intents,contexts,citingPaper.authors.authorId,citingPaper.authors.name,citingPaper.authors.affiliations"
    # Fallback fields if the detailed fetch fails (e.g. 400 Bad Request)
    simple_fields = "title,authors,year,venue,abstract,isInfluential,intents,contexts"
    
    current_fields = detailed_fields
    limit = 1000
    offset = 0
    
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key
        
    all_citations = []
    
    while True:
        params = {"fields": current_fields, "limit": limit, "offset": offset}
        try:
            r = requests.get(base, params=params, headers=headers, timeout=60)
            
            # If we get a 400 with detailed fields, try falling back to simple fields
            if r.status_code == 400 and current_fields == detailed_fields:
                print(f"  Warning: 400 Bad Request with detailed fields for DOI {doi}. Retrying with simple fields...")
                current_fields = simple_fields
                continue
                
            if r.status_code == 404:
                print(f"Paper with DOI {doi} not found in Semantic Scholar.")
                break
                
            r.raise_for_status()
            payload = r.json()
            
            data = payload.get("data", [])
            all_citations.extend(data)
            
            nxt = payload.get("next")
            if not nxt:
                break
            offset = nxt
            
            # Enforce rate limit of 1 query per second
            time.sleep(1.1) 
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching citations for DOI {doi}: {e}")
            # If we failed with detailed fields, try once with simple fields unless we already did
            if current_fields == detailed_fields:
                 print("  Retrying with simple fields due to error...")
                 current_fields = simple_fields
                 time.sleep(1.1)
                 continue
            break
            
    return all_citations

def main():
    api_key = load_api_key()
    papers = load_papers_from_bib()
    
    total_papers = len(papers)
    print(f"Found {total_papers} papers in bib file.")
    
    all_papers_data = []
    
    for i, paper in enumerate(papers):
        doi = paper.get("doi")
        title = paper.get("title", "Unknown Title")
        
        print(f"\nProcessing {i+1}/{total_papers}: {title}")
        if not doi:
            print("  Skipping: No DOI found.")
            continue
            
        print(f"  DOI: {doi}")
        citations = fetch_citations(doi, api_key)
        print(f"  Total citations fetched: {len(citations)}")
        
        paper_data = {
            "my_paper": paper,
            "citations": citations
        }
        all_papers_data.append(paper_data)
        
        # Save intermediate results
        with open("citations.json", "w", encoding="utf-8") as f:
            json.dump(all_papers_data, f, indent=2)
            
        if citations:
            titles = [
                c.get("citingPaper", {}).get("title", "Unknown Title")
                for c in citations
                if c.get("citingPaper")
            ]
            print(f"  First 5 citing titles: {titles[:5]}")
        
        # Add a delay between papers to respect rate limits
        time.sleep(1.1)

    print(f"\nSaved citation data for {len(all_papers_data)} papers to citations.json")

if __name__ == "__main__":
    main()
