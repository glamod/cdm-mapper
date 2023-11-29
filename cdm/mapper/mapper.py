"""
Created on Thu Apr 11 13:45:38 2019

Maps data contained in a pandas DataFrame (or pd.io.parsers.TextFileReader) to
the C3S Climate Data Store Common Data Model (CDM) header and observational
tables using the mapping information available in the tool's mapping library
for the input data model.

@author: iregon
"""

import importlib
import os
from io import StringIO

import numpy as np
import pandas as pd

from cdm import properties
from cdm.common import logging_hdlr, pandas_TextParser_hdlr
from cdm.lib.mappings import mappings_hdlr
from cdm.lib.tables import tables_hdlr

module_path = os.path.dirname(os.path.abspath(__file__))


def _map(imodel, data, data_atts, cdm_subset=None, log_level="INFO"):
    """
    Maps a pandas DataFrame (or pd.io.parsers.TextFileReader) to the C3S Climate Data Store Common Data Model (CDM)
    header and observational tables using mapping information from the input data model (imodel).

    Parameters
    ----------
    imodel: a data model that can be
            1. A generic mapping from a defined data model, like IMMA1's core and attachments
               e.g. ``~/cdm-mapper/lib/mappings/icoads_r3000``
            2. A specific mapping from generic data model to CDM, like map a SID-DCK from IMMA1's core and attachments
               to CDM in a specific way. e.g. ``~/cdm-mapper/lib/mappings/icoads_r3000_d704``
    data: input data to map
        e.g. a pandas.Dataframe or io.parsers.TextFileReader objects or in-memory text streams (io.StringIO object).
    data_atts:
        dictionary with the {element_name:element_attributes} of the data. Type: string.
    cdm_subset: subset of CDM model tables to map.
        Defaults to the full set of CDM tables defined for the imodel. Type: list.
    log_level: level of logging information to save.
        Defaults to ‘DEBUG’. Type: string.

    Returns
    -------
    cdm_tables: a python dictionary with the ``cdm_table_name`` and ``cdm_table_object`` pairs.

    cdm_table_name: is the name of the CDM table i.e. ``header``, ``observations_at``, etc.
    cdm_table_object: is the python dictionary with the ``{data:cdm_table_object, atts:cdm_table_atts}`` pairs.

    1. cdm_table_object: is a python pandas DataFrame object with the CDM elements aligned in columns according
    to the order established by the imodel.

    2. cdm_table_atts: python dictionary with the CDM element attributes. These element attributes can be the
    elements encoding, decimal places or other characteristics specified in the imodel.
    """
    logger = logging_hdlr.init_logger(__name__, level=log_level)

    # Get imodel mapping pack
    try:
        # Read mappings to CDM from imodel
        imodel_maps = mappings_hdlr.load_tables_maps(imodel, cdm_subset=cdm_subset)
        if len(imodel_maps) < 1:
            logger.error(f"No mappings found for model {imodel}")
            return
        # Import function modules and instantiate class with data_atts
        imodel_functions_mdl_tree = mappings_hdlr.get_functions_module_path(imodel)
        if len(imodel_functions_mdl_tree) > 0:
            imodel_functions_mdl = importlib.import_module(
                imodel_functions_mdl_tree, package=None
            )
            imodel_functions = imodel_functions_mdl.mapping_functions(data_atts)
        else:
            logger.warning(f"No mapping functions found for model {imodel}")
        # Read code table mappings
        imodel_code_tables = mappings_hdlr.load_code_tables_maps(imodel)
        if imodel_code_tables is None:
            logger.warning(f"No code table mappings found for model {imodel}")
        elif len(imodel_code_tables) < 1:
            logger.warning(
                f"No code table mappings found for model {imodel} (not NoneType)"
            )

    except Exception:
        logger.error(f"Error loading {imodel} cdm mappings", exc_info=True)
        return

    if not imodel_maps:
        logger.error(f"Error loading {imodel} cdm mappings")
        return
    # Read CDM table attributes
    cdm_atts = tables_hdlr.load_tables()
    # Check that imodel cdm tables are consistent with CDM tables (at least in naming....)
    not_in_tool = [x for x in imodel_maps.keys() if x not in cdm_atts.keys()]
    if len(not_in_tool) > 0:
        if any(not_in_tool):
            logger.error(
                "One or more tables registered in the data model is not supported by the tool: {}".format(
                    ",".join(not_in_tool)
                )
            )
            logger.info(
                "CDM tables registered in the tool in properties.py are: {}".format(
                    ",".join(properties.cdm_tables)
                )
            )
            return
    # Initialize dictionary to store temporal tables (buffer) and table attributes
    cdm_tables = {
        k: {"buffer": StringIO(), "atts": cdm_atts.get(k)} for k in imodel_maps.keys()
    }
    # Create pandas data types for buffer reading from CDM table definition pseudo-sql dtypes
    # Also keep track of datetime columns for reader to parse
    date_columns = {x: [] for x in imodel_maps.keys()}
    out_dtypes = {x: {} for x in imodel_maps.keys()}
    for table in out_dtypes:
        out_dtypes[table].update(
            {
                x: cdm_atts.get(table, {}).get(x, {}).get("data_type")
                for x in imodel_maps[table].keys()
            }
        )
        date_columns[table].extend(
            [
                i
                for i, x in enumerate(list(out_dtypes[table].keys()))
                if "timestamp" in out_dtypes[table].get(x)
            ]
        )
        out_dtypes[table].update(
            {
                k: properties.pandas_dtypes.get("from_sql").get(v, "object")
                for k, v in out_dtypes[table].items()
            }
        )

    # Now map per iterable item, per table
    for idata in data:
        cols = [x for x in idata]
        for table, mapping in imodel_maps.items():
            table_df_i = pd.DataFrame(
                index=idata.index, columns=mapping.keys()
            )  # We cannot predifine column based dtypes here!
            logger.debug(f"Table: {table}")
            for cdm_key, imapping in mapping.items():
                logger.debug(f"\tElement: {cdm_key}")
                [
                    elements,
                    transform,
                    kwargs,
                    code_table,
                    default,
                    fill_value,
                    decimal_places,
                ] = [
                    imapping.get("elements"),
                    imapping.get("transform"),
                    imapping.get("kwargs"),
                    imapping.get("code_table"),
                    imapping.get("default"),
                    imapping.get("fill_value"),
                    imapping.get("decimal_places"),
                ]

                if elements:
                    # make sure they are clean and conform to their atts (tie dtypes)
                    # we'll only let map if row complete so mapping functions do not need to worry about handling NA
                    logger.debug(
                        "\telements: {}".format(" ".join([str(x) for x in elements]))
                    )
                    missing_els = [x for x in elements if x not in cols]
                    if len(missing_els) > 0:
                        logger.warning(
                            "Following elements from data model missing from input data: {} to map {} ".format(
                                ",".join([str(x) for x in missing_els]), cdm_key
                            )
                        )
                        continue
                    to_map_types = {
                        element: properties.pandas_dtypes.get("from_atts").get(
                            data_atts.get(element).get("column_type")
                        )
                        for element in elements
                    }
                    notna_idx_idx = np.where(idata[elements].notna().all(axis=1))[0]
                    logger.debug(f"\tnotna_idx_idx: {notna_idx_idx}")
                    to_map = idata[elements].iloc[notna_idx_idx].astype(to_map_types)
                    # notna_idx = notna_idx_idx + idata.index[0]  # to account for parsers #original
                    notna_idx = idata.index[notna_idx_idx]  # fix?
                    if len(elements) == 1:
                        to_map = to_map.iloc[:, 0]
                    isEmpty = True if len(to_map) == 0 else False
                if transform and not isEmpty:
                    kwargs = {} if not kwargs else kwargs
                    logger.debug(f"\ttransform: {transform}")
                    logger.debug("\tkwargs: {}".format(",".join(list(kwargs.keys()))))

                    # os._exit(1)
                    trans = eval("imodel_functions." + transform)
                    logger.debug(f"\ttable_df_i Index: {table_df_i.index}")
                    logger.debug(f"\tidata_i Index: {idata.index}")
                    logger.debug(f"\tnotna_idx: {notna_idx}")
                    if elements:
                        # logger.warning('Table_df Index {}'.format(table_df_i))
                        # os._exit(1)
                        table_df_i.loc[notna_idx, cdm_key] = trans(to_map, **kwargs)
                    else:
                        table_df_i[cdm_key] = trans(**kwargs)
                elif code_table and not isEmpty:
                    # https://stackoverflow.com/questions/45161220/how-to-map-a-pandas-dataframe-column-to-a-nested-dictionary?rq=1
                    # Approach that does not work when it is not nested...so just try and assume not nested if fails
                    # Prepare code_table
                    table_map = imodel_code_tables.get(code_table)

                    try:
                        to_map = to_map.to_frame()
                    except:
                        pass

                    to_map_str = to_map.astype(str)

                    def map_to_df(m, x):
                        for x_ in x:
                            if x_ in m.keys():
                                v = m[x_]
                                if isinstance(v, dict):
                                    m = v
                                else:
                                    return v
                            else:
                                return

                    to_map_str.columns = [
                        "_".join(col) for col in to_map_str.columns.values
                    ]
                    table_df_i[cdm_key] = to_map_str.apply(
                        lambda x: map_to_df(table_map, x), axis=1
                    )

                elif elements and not isEmpty:
                    table_df_i[cdm_key] = to_map
                elif default is not None:  # (vakue = 0 evals to False!!)
                    if isinstance(default, list):
                        table_df_i[cdm_key] = [default] * len(table_df_i.index)
                    else:
                        table_df_i[cdm_key] = default
                #                else:
                #                    if fill_value is None:
                #                        logger.warning('Nothing defined for cdm element {}'.format(cdm_key))

                if fill_value is not None:
                    table_df_i[cdm_key].fillna(value=fill_value, inplace=True)

                if decimal_places is not None:
                    if isinstance(decimal_places, int):
                        cdm_tables[table]["atts"][cdm_key].update(
                            {"decimal_places": decimal_places}
                        )
                    else:
                        cdm_tables[table]["atts"][cdm_key].update(
                            {
                                "decimal_places": eval(
                                    "imodel_functions." + decimal_places
                                )(elements)
                            }
                        )

            # think that NaN also casts floats to float64....!keep floats of lower precision to its original one
            # will convert all NaN to object type!
            # but also some numerics with values, like imma observation-value (temperatures),
            # are being returned as objects!!! pero esto qué es?
            out_dtypes[table].update(
                {
                    i: table_df_i[i].dtype
                    for i in table_df_i
                    if table_df_i[i].dtype in properties.numpy_floats
                    and out_dtypes[table].get(i) not in properties.numpy_floats
                }
            )
            out_dtypes[table].update(
                {
                    i: table_df_i[i].dtype
                    for i in table_df_i
                    if table_df_i[i].dtype == "object"
                    and out_dtypes[table].get(i) not in properties.numpy_floats
                }
            )
            if "observation_value" in table_df_i:
                table_df_i.dropna(subset=["observation_value"], inplace=True)
            table_df_i.to_csv(
                cdm_tables[table]["buffer"], header=False, index=False, mode="a"
            )

    for table in cdm_tables.keys():
        # Convert dtime to object to be parsed by the reader
        logger.debug(
            f"\tParse datetime by reader; Table: {table}; Colums: {date_columns[table]}"
        )
        logger.debug(
            f"\tParse datetime by reader; out_dtype-keys: {out_dtypes[table].keys()}; out dtypes: {out_dtypes[table]}"
        )
        cdm_tables[table]["buffer"].seek(0)
        cdm_tables[table]["data"] = pd.read_csv(
            cdm_tables[table]["buffer"],
            names=out_dtypes[table].keys(),
            dtype=out_dtypes[table],
            parse_dates=date_columns[table],
        )
        cdm_tables[table]["buffer"].close()
        cdm_tables[table].pop("buffer")

    return cdm_tables


def map_model(imodel, data, data_atts, cdm_subset=None, log_level="INFO"):
    """
    Calls the main mapping function _map()

    Parameters
    ----------
    imodel: a data model that can be of several types.

        1. A generic mapping from a defined data model, like IMMA1’s core and attachments.
        e.g. ``~/cdm-mapper/lib/mappings/icoads_r3000``

        2. A specific mapping from generic data model to CDM, like map a SID-DCK from IMMA1’s core and attachments to
        CDM in a specific way.
            e.g. ``~/cdm-mapper/lib/mappings/icoads_r3000_d704``
    data: input data to map.
            e.g. a ``pandas.Dataframe`` or ``io.parsers.TextFileReader`` objects or in-memory text streams
            (io.StringIO object).
    data_atts: dictionary with the {element_name:element_attributes} of the data.
        Type: string.
    cdm_subset: subset of CDM model tables to map.
        Defaults to the full set of CDM tables defined for the imodel. Type: list.
    log_level: level of logging information to save.
        Defaults to ‘DEBUG’.
        Type string.

    Returns
    -------
    cdm_tables:
        a python dictionary with the ``{cdm_table_name: cdm_table_object}`` pairs.

    For more information look at the _map function.
    """
    logger = logging_hdlr.init_logger(__name__, level=log_level)
    # Check we have imodel registered, leave otherwise
    if imodel not in properties.supported_models:
        logger.error("Input data model " f"{imodel}" " not supported")
        return

    # Check input data type and content (empty?)
    # Make sure data is an iterable: this is to homogeneize how we handle
    # dataframes and textreaders
    if isinstance(data, pd.DataFrame):
        logger.debug("Input data is a pd.DataFrame")
        if len(data) == 0:
            logger.error("Input data is empty")
            return
        else:
            data = [data]
    elif isinstance(data, pd.io.parsers.TextFileReader):
        logger.debug("Input is a pd.TextFileReader")
        not_empty, data = pandas_TextParser_hdlr.is_not_empty(data)
        if not not_empty:
            logger.error("Input data is empty")
            return

    else:
        logger.error("Input data type " f"{type(data)}" " not supported")
        return

    # Map thing:
    data_cdm = _map(imodel, data, data_atts, cdm_subset=cdm_subset, log_level=log_level)

    return data_cdm
