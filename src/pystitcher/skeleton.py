"""
This is the entry script

References:
    - https://setuptools.readthedocs.io/en/latest/userguide/entry_point.html
"""

import argparse
import logging
import sys
from .stitcher import Stitcher
from pystitcher import __version__

__author__ = "Nemo"
__copyright__ = "Nemo"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Stitch PDF files together")
    parser.add_argument(
        "--version",
        action="version",
        version="pystitcher {ver}".format(ver=__version__),
    )
    parser.add_argument(dest="input", help="Input markdown file", type=argparse.FileType('r', encoding='UTF-8'), metavar="spine.md")
    parser.add_argument(dest="output", help="Output PDF file", type=str, metavar="output.pdf")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="log more things",
        action="store_const",
        const=logging.INFO,
    )

    parser.add_argument(
        '--no-cleanup',
        action='store_false',
        default=True,
        dest='cleanup',
        help="Delete temporary files"
    )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Main CLI function
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    stitcher = Stitcher(args.input)
    stitcher.generate(args.output, args.cleanup)

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m pystitcher.skeleton 42
    #
    run()
