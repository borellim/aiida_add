# -*- coding: utf-8 -*-

from aiida.parsers import Parser, OutputParsingError
from aiida.orm import Dict

import json


class SumParser(Parser):
    """
    This class is the implementation of the Parser class for Sum.
    """
    def parse(self, **kwargs):
        """
        Parses the retrieved output file, stores the sum of the two numbers
        in a Dict, and links it as output_parameters.
        """

        successful = True
        # select the folder object
        # Check that the retrieved folder is there
        try:
            out_folder = self.retrieved
        except NotExistent:
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # Try to read the output file, which name was specified as an option
        try:
            output_filename = self.node.get_option('output_filename')  # aka self.node.inputs.metadata.options.output_filename (or None)
            with out_folder.open(filename_stdout, 'r') as f:
                    out_dict = json.load(f)
        except OSError:
            return self.exit_codes.ERROR_READING_OUTPUT_FILE
        except json.JSONDecodeError:
            return self.exit_codes.ERROR_PARSING_FAILURE
            # TODO: can we add the exception message as a custom exit message?

        # save the arrays
        output_data = Dict(dict=out_dict)
        self.out('output_parameters', output_data)

        return None
