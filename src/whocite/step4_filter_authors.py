import csv

from .config import config

def main():
    input_file = config.OUTPUT_DIR / "citations_analysis.csv"
    output_file = config.OUTPUT_DIR / "high_impact_citing_authors.csv"
    top_n = 30
    
    print(f"Reading from {input_file}...")
    
    all_rows = []
    author_citations = {} # Map unique identifier (Profile URL + Name) -> citation count
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            for row in reader:
                all_rows.append(row)
                
                # Identify author uniquely
                profile = row.get("Citing Author Profile", "")
                name = row.get("Citing Author Name", "")
                unique_key = profile if profile else name
                
                try:
                    count_str = row.get("Citing Author Total Citations", "0")
                    if not count_str: count_str = "0"
                    count = int(count_str)
                except ValueError:
                    count = 0
                
                # Store the citation count (assuming consistent across rows for same author)
                if unique_key:
                    author_citations[unique_key] = max(author_citations.get(unique_key, 0), count)
                    
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run analyze_results.py first.")
        return

    # Sort authors by citation count descending
    sorted_authors = sorted(author_citations.items(), key=lambda x: x[1], reverse=True)
    
    # Take top N
    top_authors = sorted_authors[:top_n]
    top_keys = set(k for k, v in top_authors)
    
    if not top_authors:
        print("No authors found.")
        return

    print(f"Found {len(author_citations)} unique authors.")
    print(f"Selected top {len(top_keys)} authors.")
    print(f"  Highest citation count: {top_authors[0][1]}")
    print(f"  Lowest citation count in top {top_n}: {top_authors[-1][1]}")
    
    # Filter rows that belong to these authors
    filtered_rows = []
    for row in all_rows:
        profile = row.get("Citing Author Profile", "")
        name = row.get("Citing Author Name", "")
        key = profile if profile else name
        
        if key in top_keys:
            filtered_rows.append(row)
            
    # Sort the output rows by citation count descending for readability
    filtered_rows.sort(key=lambda x: int(x.get("Citing Author Total Citations", 0) or 0), reverse=True)

    if filtered_rows:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(filtered_rows)
        print(f"Saved {len(filtered_rows)} rows associated with the top {len(top_keys)} authors to {output_file}")
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()
