# Following to access the subpackages main modules (or/and functions)
# directly wihout loops through the full subpackage path
from .gridded_stats import gridded_stats  # noqa
from .mapper.mapper import map_model as map_model  # noqa
from .table_reader.table_reader import read_tables as read_tables  # noqa
from .table_writer.table_writer import cdm_to_ascii as cdm_to_ascii  # noqa
from .table_writer.table_writer import table_to_ascii as table_to_ascii  # noqa


def _get_version():
    __version__ = "unknown"
    try:
        from ._version import __version__
    except ImportError:
        pass
    return __version__


__version__ = _get_version()
