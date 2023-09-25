import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pyperclip  # Import the pyperclip library

# Define a user agent to simulate a web browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def extract_all_urls_from_sitemap(sitemap_url):
    url_list = []

    def extract_recursive(sitemap_url):
        try:
            # Send an HTTP GET request with the user agent
            headers = {"User-Agent": user_agent}
            response = requests.get(sitemap_url, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the XML content of the sitemap
                soup = BeautifulSoup(response.text, "xml")

                # Find all URL elements within the sitemap
                url_elements = soup.find_all("loc")

                # Extract and add the URLs to the list
                urls = [url.text for url in url_elements]
                url_list.extend(urls)

                # Look for sub-sitemap references (sitemapindex)
                sitemapindex_elements = soup.find_all("sitemap")
                for sitemapindex_element in sitemapindex_elements:
                    sub_sitemap_url = sitemapindex_element.find("loc").text
                    extract_recursive(sub_sitemap_url)
        except requests.exceptions.RequestException as e:
            pass

    extract_recursive(sitemap_url)
    return url_list

def main():
    st.title("Sitemap URL Extractor")

    domain = st.text_input("Enter the domain (e.g., https://example.com):")
    
    if st.button("Extract URLs"):
        if domain:
            # Ensure the domain is properly formatted
            if not domain.startswith("http://") and not domain.startswith("https://"):
                domain = "https://" + domain  # Add HTTPS if missing

            sitemap_url = urljoin(domain, "sitemap.xml")
            url_list = extract_all_urls_from_sitemap(sitemap_url)

            if url_list:
                # Create dictionaries to group URLs by file extension
                url_dict = {"Images (.jpg, .png, .webp)": [],
                            "HTML Pages (.html)": []}

                # Sort URLs based on their file extensions
                for url in url_list:
                    parsed_url = urlparse(url)
                    path = parsed_url.path
                    if path.endswith((".jpg", ".png", ".webp")):
                        url_dict["Images (.jpg, .png, .webp)"].append(url)
                    elif path.endswith(".html"):
                        url_dict["HTML Pages (.html)"].append(url)
                    else:
                        # Add any other extensions here
                        pass

                # Display URLs in separate boxes
                for category, urls in url_dict.items():
                    if urls:
                        st.subheader(category)
                        st.text_area(category, "\n".join(urls))

                # Add a "Copy All" button for each category
                for category, urls in url_dict.items():
                    if urls and st.button(f"Copy {category} URLs"):
                        # Join the URLs into a single string with line breaks
                        urls_text = "\n".join(urls)
                        # Copy the URLs to the clipboard
                        pyperclip.copy(urls_text)
                        st.success(f"All {category} URLs copied to clipboard.")
            else:
                st.error("Failed to retrieve the sitemap or extract URLs.")

if __name__ == "__main__":
    main()
