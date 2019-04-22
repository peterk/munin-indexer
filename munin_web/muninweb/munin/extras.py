from urllib.parse import urlparse
import logging
logger = logging.getLogger(__name__)

def get_uid(url):
    """Get unique identifier depending on which platform we're on"""

    try:
        o = urlparse(url)
        path = o.path

        if url.startswith("https://www.facebook.com"):

            if "/photos/" in path or "/videos/" in path and path.endswith("/"):
                return path[:-1].split("/")[-1]

            else:
                return path.split("/")[-1]

        elif url.startswith("https://www.instagram.com/"):
                return path[:-1].split("/")[-1]

        elif url.startswith("https://vk.com/"):
            return path.split("wall-")[1]

        else:
            # we'll go with the url path as the unique identifier
            logger.info(f"Unknown site {url} - returning url path")
            return urlparse(url).path

    except Exception as e:
        logger.exception("Something bad happened in get_uid")
