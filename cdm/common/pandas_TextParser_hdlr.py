"""
Created on Tue Apr  2 10:34:56 2019

Module with functions to handle pd.io.parsers.TextFileReader objects.

@author: iregon
"""

import pandas as pd

from ..common import logging_hdlr

logger = logging_hdlr.init_logger(__name__, level="ERROR")


def restore(TextParser_ref, TextParser_options):
    """
    NEEDS DOCUMENTING

    Parameters
    ----------
    TextParser_ref:
    TextParser_options:

    Returns
    -------
    TextParser:
    """
    try:
        TextParser_ref.seek(0)
        TextParser = pd.read_csv(
            TextParser_ref,
            names=TextParser_options["names"],
            chunksize=TextParser_options["chunksize"],
            dtype=TextParser_options["dtype"],
        )  # , skiprows = options['skiprows'])
        return TextParser
    except Exception:
        logger.error("Failed to restore TextParser", exc_info=True)
        return TextParser


def is_not_empty(TextParser):
    """
    NEEDS DOCUMENTING

    Parameters
    ----------
    TextParser:

    Returns
    -------
    logger.error: logs specific messages if there is any error.
    bool:
    TextParser:

    """
    try:
        TextParser_ref = TextParser.handles.handle
        TextParser_options = TextParser.orig_options
    except Exception:
        logger.error(
            f"Failed to process input. Input type is {type(TextParser)}", exc_info=True
        )
        return
    try:
        first_chunk = TextParser.get_chunk()
        TextParser = restore(TextParser_ref, TextParser_options)
        if len(first_chunk) > 0:
            logger.debug("Is not empty")
            return True, TextParser
        else:
            return False, TextParser
    except Exception:
        return False, TextParser