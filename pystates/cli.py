import argparse
import sys


from pystates.parser import fetch_and_parse_article
from pystates.exporters import save_article


def main():
    parser = argparse.ArgumentParser(description="Download and save web articles")
    parser.add_argument('-u', '--url', required=True, help="URL to article")
    parser.add_argument('-f', '--format', default='md', choices=['md', 'txt'], help="Output format (md or txt)")
    parser.add_argument('-o', '--output', default=None, help="Custom output filename")

    args = parser.parse_args()

    try:
        print(f"Downloading article from: {args.url}...")
        article_data = fetch_and_parse_article(args.url)

        saved_file = save_article(
            title=article_data["title"],
            content=article_data["content"],
            output_format=args.format,
            custom_filename=args.output
        )
        print(f"Saved article to: {saved_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()