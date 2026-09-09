"""Configuration file loading module."""

import json
import logging
from pathlib import Path


# Get repository root (parent of scripts directory)
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "feeds.config.json"

REQUIRED_GNEWS_SETTINGS = ['language', 'country', 'max_results', 'period']


def load_config():
    """Load and validate the feeds configuration file.

    Returns:
        Dict with 'gnews_settings', 'excluded_domains', and 'feeds' keys,
        or None if loading fails
    """
    if not CONFIG_PATH.exists():
        logging.error(f"Configuration file not found: {CONFIG_PATH}")
        return None

    try:
        with CONFIG_PATH.open('r') as f:
            config = json.load(f)

        # Validate gnews_settings
        if 'gnews_settings' not in config:
            logging.error("Configuration file missing 'gnews_settings' key")
            return None

        gnews_settings = config['gnews_settings']
        for field in REQUIRED_GNEWS_SETTINGS:
            if field not in gnews_settings:
                logging.error(f"gnews_settings missing required field: {field}")
                return None

        # Validate feeds array
        if 'feeds' not in config:
            logging.error("Configuration file missing 'feeds' key")
            return None

        if not isinstance(config['feeds'], list):
            logging.error("Configuration 'feeds' must be an array")
            return None

        excluded_domains = config.get('excluded_domains', [])

        # Validate each feed
        valid_feeds = []
        for i, feed in enumerate(config['feeds']):
            if not isinstance(feed, dict):
                logging.error(f"Feed {i} is not an object")
                continue

            if 'query' not in feed:
                logging.error(f"Feed {i} missing 'query' field")
                continue

            if 'category' not in feed:
                logging.error(f"Feed {i} missing 'category' field")
                continue

            query = feed['query']
            category = feed['category']

            if not isinstance(query, str) or not query.strip():
                logging.error(f"Feed {i} has empty query")
                continue

            if not isinstance(category, str) or not category.strip():
                logging.error(f"Feed {i} has empty category")
                continue

            valid_feeds.append({
                'query': query,
                'category': category
            })

        if not valid_feeds:
            logging.error("No valid feeds found in configuration")
            return None

        logging.info(f"Loaded {len(valid_feeds)} feed(s) from configuration")
        return {
            'gnews_settings': gnews_settings,
            'excluded_domains': excluded_domains,
            'feeds': valid_feeds
        }

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return None
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return None
