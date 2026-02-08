import json
import requests
import time

def load_citations(filepath="citations.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def load_api_key(filepath="api key.txt"):
    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def fetch_authors_batch(author_ids, api_key=None):
    url = "https://api.semanticscholar.org/graph/v1/author/batch"
    fields = "name,affiliations,hIndex,citationCount,url,externalIds"
    
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    # Semantic Scholar Batch API typically accepts up to 1000 IDs, but let's be safe with 100 or 50
    batch_size = 50
    all_authors = []
    
    total = len(author_ids)
    print(f"Fetching details for {total} authors in batches of {batch_size}...")

    for i in range(0, total, batch_size):
        batch_ids = author_ids[i:i+batch_size]
        payload = {"ids": batch_ids}
        params = {"fields": fields}
        
        try:
            r = requests.post(url, json=payload, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            batch_data = r.json()
            
            # The batch API returns a list of author objects, might include None if not found
            valid_authors = [a for a in batch_data if a]
            all_authors.extend(valid_authors)
            
            print(f"  Processed {min(i+batch_size, total)}/{total}")
            
            # Rate limit sleep
            time.sleep(1.1) 
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching batch {i}: {e}")
            
    return all_authors

def main():
    api_key = load_api_key()
    data = load_citations()
    
    # Extract unique author IDs
    unique_author_ids = set()
    for entry in data:
        citations = entry.get("citations", [])
        for citation in citations:
            citing_paper = citation.get("citingPaper")
            if citing_paper and "authors" in citing_paper:
                for author in citing_paper["authors"]:
                    if author.get("authorId"):
                        unique_author_ids.add(author["authorId"])
    
    sorted_ids = sorted(list(unique_author_ids))
    print(f"Found {len(sorted_ids)} unique authors.")
    
    if not sorted_ids:
        print("No authors found to fetch.")
        return

    author_details_list = fetch_authors_batch(sorted_ids, api_key)
    
    # Convert list to dict for easier lookup
    author_map = {a["authorId"]: a for a in author_details_list if a and "authorId" in a}
    
    print(f"Successfully fetched details for {len(author_map)} authors.")
    
    # Save to file
    with open("authors.json", "w", encoding="utf-8") as f:
        json.dump(author_map, f, indent=2)
    print("Saved author details to authors.json")

if __name__ == "__main__":
    main()
