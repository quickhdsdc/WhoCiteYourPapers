import csv
import shutil
import os

from .config import config

def load_enriched_data(filename):
    """
    Loads enriched author data into a dictionary keyed by Profile OR Name.
    """
    filepath = config.PROJECT_ROOT / filename
    enriched_map = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                profile = row.get("profile", "") # 'profile' from lower-cased header in enriched file
                name = row.get("name", "")
                
                # Check headers compatibility (research_author.py writes specific headers)
                # If keys differ, adjust index
                
                key = profile if profile else name
                if key:
                    enriched_map[key] = row
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return {}
    return enriched_map

def main():
    target_file = "high_impact_citing_authors.csv"
    source_file = "high_impact_authors_enriched.csv"
    output_file = "high_impact_citing_authors_merged.csv" # Temporary output
    
    print(f"Loading enriched data from {source_file}...")
    enriched_map = load_enriched_data(source_file)
    print(f"Loaded details for {len(enriched_map)} authors.")
    
    if not enriched_map:
        print("No enriched data found. Aborting merge.")
        return

    print(f"Processing {target_file}...")
    
    target_path = config.PROJECT_ROOT / target_file
    output_path = config.PROJECT_ROOT / output_file
    
    merged_rows = []
    fieldnames = []
    
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            
            # Add new columns if not present
            new_cols = ["Researched Name", "Researched Affiliation", "Researched Title", "Researched Link"]
            for col in new_cols:
                if col not in fieldnames:
                    fieldnames.append(col)
            
            for row in reader:
                profile = row.get("Citing Author Profile", "")
                name = row.get("Citing Author Name", "")
                key = profile if profile else name
                
                if key and key in enriched_map:
                    source_row = enriched_map[key]
                    # Map source columns to target columns
                    row["Researched Name"] = source_row.get("Researched Name", "")
                    row["Researched Affiliation"] = source_row.get("Researched Affiliation", "")
                    row["Researched Title"] = source_row.get("Researched Title", "")
                    row["Researched Link"] = source_row.get("Researched Link", "")
                else:
                    # Fill empty if no match
                    row["Researched Name"] = ""
                    row["Researched Affiliation"] = ""
                    row["Researched Title"] = ""
                    row["Researched Link"] = ""
                
                merged_rows.append(row)
                
    except FileNotFoundError:
        print(f"Error: {target_file} not found.")
        return

    # Write to new file
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_rows)
        
    print(f"Merged data saved to {output_file}")
    
    # Overwrite original as implied by "merge into"
    try:
        shutil.move(output_path, target_path)
        print(f"Overwrote {target_file} with merged data.")
    except Exception as e:
        print(f"Error overwriting file: {e}. Data is in {output_file}")

if __name__ == "__main__":
    main()
