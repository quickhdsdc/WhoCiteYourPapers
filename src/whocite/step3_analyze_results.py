import json
import csv

from .config import config

def load_json(filename):
    filepath = config.PROJECT_ROOT / filename
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def main():
    citations_data = load_json("citations.json")
    # authors_json is a dict mapping authorId -> details
    authors_map = load_json("authors.json")
    
    analysis_results = []
    
    for entry in citations_data:
        my_paper = entry.get("my_paper", {})
        my_title = my_paper.get("title", "Unknown Title")
        my_doi = my_paper.get("doi", "")
        
        citations = entry.get("citations", [])
        
        for citation in citations:
            citing_paper = citation.get("citingPaper", {})
            if not citing_paper:
                continue
                
            cit_title = citing_paper.get("title", "Unknown Title")
            cit_year = citing_paper.get("year", "")
            cit_venue = citing_paper.get("venue", "")
            cit_url = citing_paper.get("url", "") # often not directly available in this obj structure but useful if present
            
            # Author processing
            # In detailed fetch, authors structure is list of dicts with 'authorId', 'name', 'affiliations'
            # In simple fetch, it's list of dicts with 'authorId', 'name'
            cit_authors = citing_paper.get("authors", [])
            
            author_details_list = []
            
            for author in cit_authors:
                a_id = author.get("authorId")
                name = author.get("name")
                
                # Get affiliation from citation context (paper metadata)
                paper_affiliations = author.get("affiliations", [])
                
                # Get details from author profile fetch
                profile_details = authors_map.get(a_id, {}) if a_id else {}
                
                profile_affiliations = profile_details.get("affiliations", [])
                h_index = profile_details.get("hIndex", "")
                citation_count = profile_details.get("citationCount", "")
                profile_url = profile_details.get("url", "")
                
                # Merge affiliations
                # Prefer paper affiliations as they are contemporary to the citation
                # But sometimes profile affiliations are cleaner
                final_affiliations = paper_affiliations if paper_affiliations else profile_affiliations
                # Convert list to string
                affiliation_str = "; ".join(final_affiliations) if final_affiliations else ""
                
                author_info = {
                    "name": name,
                    "id": a_id,
                    "affiliation": affiliation_str,
                    "h_index": h_index,
                    "total_citations": citation_count,
                    "profile_url": profile_url
                }
                author_details_list.append(author_info)
            
            # Create a row for each author? Or one row per citation with concatenated authors?
            # User wants "authors of each citation". 
            # A flattened CSV where each row is a Citation-Author pair might be best 
            # OR a Citation row with all authors in one cell.
            # "I need the author information of each citation... for each author, need her or his info"
            # So likely one row per author is most detailed.
            
            for a_info in author_details_list:
                row = {
                    "My Paper DOI": my_doi,
                    "My Paper Title": my_title,
                    "Citing Paper Title": cit_title,
                    "Citing Paper Year": cit_year,
                    "Citing Paper Venue": cit_venue,
                    "Citing Author Name": a_info["name"],
                    "Citing Author Affiliation": a_info["affiliation"],
                    "Citing Author h-index": a_info["h_index"],
                    "Citing Author Total Citations": a_info["total_citations"],
                    "Citing Author Profile": a_info["profile_url"]
                }
                analysis_results.append(row)

    # Save to JSON
    json_out = config.PROJECT_ROOT / "citations_analysis.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)
        
    # Save to CSV
    if analysis_results:
        headers = list(analysis_results[0].keys())
        csv_out = config.PROJECT_ROOT / "citations_analysis.csv"
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(analysis_results)
            
    print(f"Analysis complete. Processed {len(analysis_results)} author-citation records.")
    print("Saved to citations_analysis.json and citations_analysis.csv")

if __name__ == "__main__":
    main()
