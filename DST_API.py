import requests
import pandas as pd
from IPython.display import display
from io import StringIO
import warnings
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font
import locale
import numpy as np


import requests

class DstApi:
    def __init__(self, tablename) -> None:
        self.apiip = "https://api.statbank.dk/v1" # Base URL for connecting to the Statistikbanken API.
        self.tablename = str(tablename).lower() # Store the table name in lowercase to ensure consistency and ease of access. Makes it possible to connect to the individual table in statistikbanken through their tablename.
        self._tableinfo = None # Initialize _tableinfo as None; this will be used later to store table metadata.

    # Gives a short summary of the dataset.
    def tablesummary(self, verbose=True, language="da") -> pd.DataFrame:
        """
        Returns a summary of a published DST table containing the description of
        the table and of the variables according to which the values are
        reported
        """
        # Get table info from API
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)

        # Make report
        if verbose:
            print(f"Table {self._tableinfo['id']}: {self._tableinfo['description']}")
            print(f"Last update: {self._tableinfo['updated']}")

        table = self._wrap_tableinfo_variables(self._tableinfo)
        return table

    # Shows the possible variables to download.
    def variable_levels(self, varname, language="da") -> pd.DataFrame:
        """
        Returns a DataFrame with the possible values of `varname` in the table.
        Useful to define query parameters via the method `define_base_params`.

        Parameters:
        ----------
        varname : str        The name of the variable in the DST table to
        tabulate

        language : str       The language for the variable labels (default: "da", Danish).
        Provide "en" for english descriptions when available
        
        Returns:
        ----------
        A DataFrame with the possible values of `varname` in the DST table
        """
        # Get table info from API
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)

        try:
            return pd.DataFrame(
                [i for i in self._tableinfo["variables"] if i["id"] == varname][0][
                    "values"
                ]
            )
        except IndexError as err:
            print(
                """
                Error: The table does not seem to contain the requested variable.
                Check the spelling (variable names are case sensitive
                )"""
            )
            return err

    # The function that downloads tables according to API call.
    def get_data(
        self, params=None, language="da", as_DataFrame=True, override_warning=False
    ) -> pd.DataFrame:
        """
        Downloads table data according to API call specified in `params`. If
        `params` is None (default), parameters resulting in the download of the
        entire data table will be automatically generated, raising a warning.

        The function returns a Pandas DataFrame by default. 

        Parameters:
        ----------
        params : dict, optional A dictionary containing the parameters for the
        API query. These parameters control the selection of the table to
        download, and are crucial to avoid dowloading excessively large tables.
        The helper method `define_base_params` can be used to define the
        parameter structure for downloading the full table. From this parameter
        structure a user can restrict the query by selecting only the required
        values of selection variables (see `variable_levels` method).

        language : str, optional The language for the variable labels (default:
        "da", Danish).

        as_DataFrame : bool, optional If `True`, the method will return a
        pd.DataFrame. Specify `as_DataFrame=False` to obtain the original
        `requests.Response` object.
        """
        if params is None:
            if override_warning is False:
                warnings.warn(
                    (
                        "API call parameters are not specified. Parameters resulting "
                        "in the download of the entire table will be automatically generated. "
                        "This can result in massive data downloads."
                    ),
                    stacklevel=2,
                )
                answer = input("Continue (Y/Yes)?")
            else:
                answer = "yes"
            if answer.lower() in ["y", "yes"]:
                params = self._define_base_params(language=language)
            else:
                print("Execution aborted")
                return

        r = requests.post(self.apiip + "/data", json=params)
        if as_DataFrame:
            return pd.read_csv(StringIO(r.text), sep=";", decimal=",")
        else:
            return r

    def _get_tableinfo(self, language="da") -> dict:
        tableinfo = self._tableinfo = requests.get(
            self.apiip + "/tableinfo",
            params={"id": self.tablename, "format": "JSON", "lang": language},
        ).json()
        return tableinfo

# _define_base_params is not used as it is right now, but is kept incase it could be usefull later on
    def _define_base_params(self, language="da") -> dict:
        """
        Return a parameter dictionary resulting in the download of an entire
        data table. Use with caution.
        """
        ts = self.tablesummary(verbose=False)

        variables = [{"code": var, "values": ["*"]} for var in ts["variable name"]]
        params = {
            "table": self.tablename,
            "format": "BULK",
            "lang": language,
            "variables": variables,
        }

        return params

    def define_base_params(self, language="da") -> dict:
        """
        Returns a parameter dictionary resulting in the download of an entire
        data table.
        """
        return self._define_base_params(language=language)
# end of _define_base_params

    # _wrap_table_info is used to construct summary tables.
    @staticmethod
    def _wrap_tableinfo_variables(tiresponse) -> pd.DataFrame:
        toplist = []
        for var in tiresponse["variables"]:
            vallist = [var["id"]]
            vallist.append(len(var["values"]))
            vallist.append(var["values"][0]["id"])
            vallist.append(var["values"][0]["text"])
            vallist.append(var["values"][-1]["id"])
            vallist.append(var["values"][-1]["text"])
            vallist.append(var["time"])
            toplist.append(vallist)
        return pd.DataFrame(
            toplist,
            columns=[
                "variable name",
                "# values",
                "First value",
                "First value label",
                "Last value",
                "Last value label",
                "Time variable",
            ],
        ) 

    # get_table_unit is used to have the "enhed" (unit) from dst in the excel file aswell. 
    def get_table_unit(self, language="en") -> str:
        """
        Fetches and returns the unit of measurement for the table.

        Returns:
        ----------
        The unit of measurement as a string.
        """
        if self._tableinfo is None:
            self._tableinfo = self._get_tableinfo(language=language)

        return self._tableinfo.get('unit', 'unit not found')
    