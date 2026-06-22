import os
import time
import cloudscraper

def scrape_all_feynman_volumes():
    """
    Downloads all chapters of Feynman Lectures Volumes I, II, and III
    and saves them as HTML files in the data/raw folder.
    """
    base_url = "https://www.feynmanlectures.caltech.edu/"
    save_dir = "../data/raw"
    
    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Initialize cloudscraper to bypass anti-bot protections
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    print("Starting automated download of all Feynman Lectures...")
    
    # Dictionary mapping the Volume numeral to its total number of chapters
    volumes = {
        "I": 52,
        "II": 42,
        "III": 21
    }
    
    for vol, num_chapters in volumes.items():
        print(f"\n--- Downloading Volume {vol} ({num_chapters} chapters) ---")
        
        for i in range(1, num_chapters + 1):
            # Format the chapter number with a leading zero (e.g., 1 becomes '01')
            chapter_str = f"{i:02d}"
            
            # This creates the correct filename (e.g., II_05.html, III_12.html)
            filename = f"{vol}_{chapter_str}.html"
            
            direct_url = f"{base_url}{filename}"
            save_path = os.path.join(save_dir, filename)
            
            # Skip if we already downloaded it (so it won't re-download Vol 1)
            if os.path.exists(save_path):
                print(f"Skipping {filename} (Already exists)")
                continue
                
            print(f"Downloading {filename}...")
            
            # Send the web request
            response = scraper.get(direct_url)
            
            if response.status_code == 200:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                print(f"Failed to download {filename} (Status Code: {response.status_code})")
                
            # Be polite to their server! 
            time.sleep(2)
            
    print("\nScraping complete! All 3 volumes are safely in your data/raw folder.")

if __name__ == "__main__":
    scrape_all_feynman_volumes()