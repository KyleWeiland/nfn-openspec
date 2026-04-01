"""Configuration file loading module."""

import json
import logging
import os
from url_extraction import is_valid_url


CONFIG_PATH = "feeds.config.json"


def load_config():
    """Load and validate the feeds configuration file.

    Returns:
        List of feed dictionaries with 'url' and 'category' keys, or None if loading fails
    """
    # Check if config file exists
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Configuration file not found: {CONFIG_PATH}")
        return None

    try:
        # Load JSON
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        # Validate structure
        if 'feeds' not in config:
            logging.error("Configuration file missing 'feeds' key")
            return None

        if not isinstance(config['feeds'], list):
            logging.error("Configuration 'feeds' must be an array")
            return None

        # Validate each feed
        valid_feeds = []
        for i, feed in enumerate(config['feeds']):
            if not isinstance(feed, dict):
                logging.error(f"Feed {i} is not an object")
                continue

            # Check for required fields
            if 'url' not in feed:
                logging.error(f"Feed {i} missing 'url' field")
                continue

            if 'category' not in feed:
                logging.error(f"Feed {i} missing 'category' field")
                continue

            url = feed['url']
            category = feed['category']

            # Validate URL
            if not isinstance(url, str) or not is_valid_url(url):
                logging.error(f"Feed {i} has invalid URL: {url}")
                continue

            # Validate category
            if not isinstance(category, str) or not category.strip():
                logging.error(f"Feed {i} has empty category")
                continue

            valid_feeds.append({
                'url': url,
                'category': category
            })

        if not valid_feeds:
            logging.error("No valid feeds found in configuration")
            return None

        logging.info(f"Loaded {len(valid_feeds)} feed(s) from configuration")
        return valid_feeds

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return None
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return None
