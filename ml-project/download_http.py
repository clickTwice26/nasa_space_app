#!/usr/bin/env python3
"""
TRMM Data Downloader using direct HTTPS URLs.
No AWS credentials needed - uses NASA Earthdata direct links.
"""

import os
import re
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

class TRMMDownloaderHTTP:
    def __init__(self, links_file, download_dir, max_workers=6):
        # Load environment variables
        load_dotenv()
        
        self.links_file = links_file
        self.download_dir = Path(download_dir)
        self.max_workers = max_workers
        self.log_file = self.download_dir.parent / "download_http.log"
        
        # Create session with appropriate settings for NASA Earthdata
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TRMM-Downloader/1.0 (NASA Earthdata Access)'
        })
        
        # Set up NASA Earthdata authentication
        # First try .netrc file, then fallback to manual auth
        netrc_path = Path.home() / '.netrc'
        if netrc_path.exists():
            print("✓ Using .netrc file for authentication")
        else:
            # Create .netrc file with provided credentials
            self._create_netrc_file()
        
        # Set up cookies for NASA Earthdata
        self.cookies_file = Path.home() / '.urs_cookies'
        
        # Set up NASA Earthdata authentication from environment variables
        username = os.getenv('NASA_USERNAME')
        password = os.getenv('NASA_PASSWORD')
        
        if not username or not password:
            raise ValueError("NASA_USERNAME and NASA_PASSWORD must be set in .env file")
        
        self.session.auth = HTTPBasicAuth(username, password)
        
        # Counters (thread-safe)
        self.lock = threading.Lock()
        self.downloaded = 0
        self.skipped = 0
        self.failed = 0
        self.processed = 0
    
    def _create_netrc_file(self):
        """Create .netrc file with NASA Earthdata credentials."""
        username = os.getenv('NASA_USERNAME')
        password = os.getenv('NASA_PASSWORD')
        
        if not username or not password:
            raise ValueError("NASA_USERNAME and NASA_PASSWORD must be set in .env file")
        
        netrc_path = Path.home() / '.netrc'
        netrc_content = f"""machine urs.earthdata.nasa.gov
login {username}
password {password}
"""
        try:
            with open(netrc_path, 'w') as f:
                f.write(netrc_content)
            # Set proper permissions (600 = rw-------)
            netrc_path.chmod(0o600)
            print("✓ Created .netrc file for NASA Earthdata authentication")
        except Exception as e:
            print(f"⚠ Warning: Could not create .netrc file: {e}")
            print("Manual authentication may be required")
    
    def parse_urls(self):
        """Parse URLs and organize by year/month."""
        urls_by_year_month = defaultdict(list)
        
        try:
            with open(self.links_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or not line.startswith('http'):
                        continue
                    
                    # Skip the PDF documentation file
                    if line.endswith('.pdf'):
                        continue
                    
                    # Extract year and month from the URL path
                    match = re.search(r'/(\d{4})/(\d{2})/', line)
                    if match:
                        year, month = match.groups()
                        urls_by_year_month[(year, month)].append(line)
                    else:
                        self.log_message(f"Could not parse year/month from line {line_num}: {line}")
        
        except FileNotFoundError:
            print(f"Error: Could not find file {self.links_file}")
            return {}
        
        return urls_by_year_month
    
    def log_message(self, message):
        """Thread-safe logging."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def download_file_http(self, url, local_path):
        """Download a single file using HTTP requests with NASA Earthdata authentication."""
        try:
            # Ensure directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use authentication from .netrc and cookies
            response = self.session.get(
                url, 
                stream=True, 
                timeout=60,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Get file size from headers
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress
            with open(local_path, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            # Verify download
            actual_size = local_path.stat().st_size
            if total_size > 0 and actual_size != total_size:
                return False, f"Size mismatch: expected {total_size}, got {actual_size}"
            
            # Verify minimum file size (TRMM files should be at least 500KB)
            if actual_size < 500000:
                return False, f"File too small: {actual_size} bytes (possible authentication error)"
            
            return True, None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False, "Authentication failed - check NASA Earthdata credentials"
            elif e.response.status_code == 403:
                return False, "Access forbidden - check data access permissions"
            else:
                return False, f"HTTP error {e.response.status_code}: {e}"
        except requests.exceptions.Timeout:
            return False, "Download timeout"
        except requests.exceptions.RequestException as e:
            return False, f"HTTP error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def download_worker(self, year, month, url):
        """Worker function for downloading a single file with proper year/month organization."""
        filename = url.split('/')[-1]
        
        # Create proper year/month directory structure
        local_dir = self.download_dir / year / month
        local_file = local_dir / filename
        
        # Update processed counter
        with self.lock:
            self.processed += 1
            current_processed = self.processed
        
        # Check if file already exists and has reasonable size
        if local_file.exists() and local_file.stat().st_size > 500000:  # At least 500KB for TRMM files
            with self.lock:
                self.skipped += 1
            self.log_message(f"SKIPPED: {year}/{month}/{filename} (already exists)")
            return f"Skipped {year}/{month}/{filename}"
        
        # Download the file
        success, error = self.download_file_http(url, local_file)
        
        if success:
            with self.lock:
                self.downloaded += 1
            file_size = local_file.stat().st_size
            self.log_message(f"SUCCESS: {year}/{month}/{filename} ({file_size:,} bytes)")
            return f"✓ Downloaded {year}/{month}/{filename} ({file_size:,} bytes)"
        else:
            with self.lock:
                self.failed += 1
            self.log_message(f"FAILED: {year}/{month}/{filename} - {error}")
            # Remove partial file if it exists
            if local_file.exists():
                local_file.unlink()
            return f"✗ Failed {year}/{month}/{filename}: {error}"
    
    def print_progress(self, total_files):
        """Print progress in a separate thread."""
        while True:
            with self.lock:
                current = self.processed
                downloaded = self.downloaded
                skipped = self.skipped
                failed = self.failed
            
            if current >= total_files:
                break
                
            percentage = (current / total_files) * 100
            print(f"\\rProgress: {current}/{total_files} ({percentage:.1f}%) | "
                  f"Downloaded: {downloaded} | Skipped: {skipped} | Failed: {failed}", 
                  end='', flush=True)
            time.sleep(2)
    
    def test_download(self):
        """Test download with a single file."""
        print("Testing download with a single file...")
        
        # Get the first data URL (skip PDF)
        with open(self.links_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('http') and not line.endswith('.pdf'):
                    test_url = line
                    break
        
        test_filename = test_url.split('/')[-1]
        test_path = self.download_dir.parent / f"test_{test_filename}"
        
        print(f"Testing URL: {test_url}")
        success, error = self.download_file_http(test_url, test_path)
        
        if success:
            file_size = test_path.stat().st_size
            print(f"✓ Test download successful: {file_size:,} bytes")
            test_path.unlink()  # Remove test file
            return True
        else:
            print(f"✗ Test download failed: {error}")
            if test_path.exists():
                test_path.unlink()
            return False
    
    def run(self):
        """Main download process."""
        print("TRMM Data Downloader (Direct HTTPS)")
        print("=" * 36)
        print(f"Source file: {self.links_file}")
        print(f"Download destination: {self.download_dir}")
        print(f"Max parallel downloads: {self.max_workers}")
        print(f"Log file: {self.log_file}")
        print()
        
        # Test download first
        if not self.test_download():
            print("Initial test failed. Please check your internet connection.")
            return False
        
        # Parse URLs
        print("Parsing URLs...")
        urls_by_year_month = self.parse_urls()
        
        if not urls_by_year_month:
            print("✗ No valid URLs found")
            return False
        
        total_files = sum(len(urls) for urls in urls_by_year_month.values())
        print(f"Found {total_files} files across {len(urls_by_year_month)} year/month combinations")
        
        # Show summary
        years = sorted(set(year for year, month in urls_by_year_month.keys()))
        for year in years:
            year_files = sum(len(urls) for (y, m), urls in urls_by_year_month.items() if y == year)
            months = sorted(set(month for y, month in urls_by_year_month.keys() if y == year))
            print(f"  {year}: {year_files} files across months {', '.join(months)}")
        print()
        
        # Confirm download
        response = input(f"Download {total_files} files with {self.max_workers} parallel workers? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Download cancelled.")
            return False
        
        # Initialize log
        self.download_dir.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w') as f:
            f.write(f"TRMM Download Log (HTTP) - {datetime.now()}\n")
            f.write("=" * 50 + "\n")
        
        print("\\nStarting parallel download...")
        start_time = time.time()
        
        # Start progress monitor
        progress_thread = threading.Thread(target=self.print_progress, args=(total_files,))
        progress_thread.daemon = True
        progress_thread.start()
        
        # Create all download tasks
        tasks = []
        for (year, month), urls in urls_by_year_month.items():
            for url in urls:
                tasks.append((year, month, url))
        
        # Execute downloads with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.download_worker, year, month, url): (year, month, url)
                for year, month, url in tasks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                except Exception as e:
                    year, month, url = future_to_task[future]
                    filename = url.split('/')[-1]
                    print(f"\\nException in {year}/{month}/{filename}: {e}")
                    with self.lock:
                        self.failed += 1
        
        print("\\n\\nDownload Complete!")
        print("=================")
        elapsed_time = time.time() - start_time
        print(f"Total time: {elapsed_time:.1f} seconds")
        print(f"Successfully downloaded: {self.downloaded} files")
        print(f"Skipped (already exist): {self.skipped} files")
        print(f"Failed downloads: {self.failed} files")
        print(f"Total processed: {self.processed} files")
        
        if self.downloaded > 0:
            avg_time = elapsed_time / max(self.downloaded, 1)
            print(f"Average download time: {avg_time:.2f} seconds per file")
            
            # Calculate total size
            total_size = 0
            for year_dir in self.download_dir.iterdir():
                if year_dir.is_dir():
                    for month_dir in year_dir.iterdir():
                        if month_dir.is_dir():
                            for file_path in month_dir.iterdir():
                                if file_path.is_file():
                                    total_size += file_path.stat().st_size
            
            print(f"Total downloaded size: {total_size / (1024**3):.2f} GB")
        
        print(f"\\nFiles organized in: {self.download_dir}")
        print(f"Detailed log: {self.log_file}")
        
        return True

def main():
    # Configuration - update these paths as needed
    links_file = "direct_weblinks.txt"  # Path to your links file
    download_dir = "data/raw"  # Download destination directory
    max_workers = 8  # Can be higher for HTTP downloads
    
    downloader = TRMMDownloaderHTTP(links_file, download_dir, max_workers)
    downloader.run()

if __name__ == "__main__":
    main()