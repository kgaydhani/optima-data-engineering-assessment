"""Entry point: run the Box Box Analytics pipeline."""

import logging
import sys

from boxbox_pipeline.pipeline import run
from boxbox_pipeline.validate import DataQualityError

logger = logging.getLogger(__name__)


def main() -> int:
    """Run the pipeline. Exit code 0 on success, 1 if the source data fails validation."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        run()
    except DataQualityError as error:
        logger.error("%s", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
