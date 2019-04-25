# -*- coding: utf-8 -*-
from __future__ import absolute_import

from aiida.engine import CalcJob
from aiida.orm import Dict
from aiida.common import InputValidationError, ValidationError
from aiida.common import CalcInfo, CodeInfo

import json
import six


class SumCalculation(CalcJob):
    """
    A generic plugin for adding two numbers.
    """

    _DEFAULT_INPUT_FILE = 'in.json'
    _DEFAULT_OUTPUT_FILE = 'out.json'
    _default_parser = 'sum'
    
    @classmethod
    def define(cls, spec):
        super(SumCalculation, cls).define(spec)
        spec.input('code', valid_type=Code)
        spec.input('metadata.options.input_filename', valid_type=six.string_types, default=cls._DEFAULT_INPUT_FILE, non_db=True)
        spec.input('metadata.options.output_filename', valid_type=six.string_types, default=cls._DEFAULT_OUTPUT_FILE, non_db=True)
        spec.input('metadata.options.parser_name', valid_type=six.string_types, default=cls._default_parser, non_db=True)
        spec.input('parameters', valid_type=Dict, help='Pass a Dict node with the two numbers to sum, as items "x1" and "x2".')
        spec.output('output_parameters', valid_type=Dict)
        spec.exit_code(100, 'ERROR_NO_RETRIEVED_FOLDER', message='The retrieved folder data node could not be accessed.')
        spec.exit_code(110, 'ERROR_READING_OUTPUT_FILE', message='The output file could not be read from the retrieved folder.')
        spec.exit_code(120, 'ERROR_PARSING_FAILURE', help='An error happened while parsing the output file.')

    def prepare_for_submission(self, folder):
        """
        This is the routine to be called when you want to create
        the input files and related stuff with a plugin.

          
        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """
        code = self.inputs.code  # an aiida Code
        parameters = self.inputs.parameters  # an aiida Dict
        
        input_dict = parameters.get_dict() # a python dict
        if 'x1' not in input_dict or 'x2' not in input_dict:
            raise InputValidationError('The input parameters node should contain both keys "x1" and "x2", '
                                       'but it doesn\'t.')
        
        ##############################
        # END OF INITIAL INPUT CHECK #
        ##############################

        input_filename = self.inputs.metadata.options.input_filename
        output_filename = self.inputs.metadata.options.output_filename

        # write all the input to a file
        with folder.open(input_filename,'w') as infile:
            json.dump(input_dict, infile)

        # ============================ calcinfo ================================

        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = [output_filename]
        calcinfo.retrieve_temporary_list = [['path/hugefiles*[0-9].xml', '.', '1']]

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = [input_filename, output_filename]
        codeinfo.code_uuid = code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
