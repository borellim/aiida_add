#!/usr/bin/env runaiida
# -*- coding: utf-8 -*-
import sys
import os

from aiida.common import NotExistent
from aiida.orm import Code
from aiida.orm import Dict, Int, Float
from aiida.engine import launch
from aiida_add.calculations.add import SumCalculation

# The name of the code (and computer) setup in AiiDA
code_string = 'sum@localhost'

################################################################

try:
    dontsend = sys.argv[1]
    if dontsend == "--dont-send":
        submit_test = True
    elif dontsend == "--send":
        submit_test = False
    else:
        raise IndexError
except IndexError:
    print("The first parameter can only be either --send or --dont-send", sys.stderr)
    sys.exit(1)

code = Code.get_from_string(code_string)

# These are the two numbers to sum
parameters = Dict(dict={'x1':2, 'x2':3})

inputs = {
    'code': code,
    'parameters': parameters,
    'label': "Test sum",
    'description': "Test calculation with the sum code",
    'metadata': {
        'options': {
            'resources': {
                'num_machines': Int(1)
            },
            'max_wallclock_seconds': Float(30*60),  # 30 min
            'withmpi': False,
        }
    }
}

daemon = False  # set to True to use the daemon (non-blocking),
               # False to use a local runner (blocking)

if submit_test:
    raise NotImplementedError("Is there an equivalent for calc.submit_test?")
    # subfolder, script_filename = calc.submit_test()
    # print "Test submit file in {}".format(os.path.join(
    #     os.path.relpath(subfolder.abspath),
    #     script_filename
    #     ))
else:    
    if daemon:
        new_calc = launch.submit(AddCalculation, **inputs)
        click.echo('Submitted {}<{}> to the daemon'.format(AddCalculation.__name__, new_calc.pk))
    else:
        click.echo('Running an add calculation... ')
        _, new_calc = launch.run_get_node(AddCalculation, **inputs)
        click.echo('AddCalculation<{}> terminated with state: {}'.format(new_calc.pk, new_calc.process_state))
        click.echo('\n{link:25s} {node}'.format(link='Output link', node='Node pk and type'))
        click.echo('{s}'.format(s='-' * 60))
        for triple in sorted(new_calc.get_outgoing().all(), key=lambda triple: triple.link_label):
            click.echo('{:25s} {}<{}> '.format(triple.link_label, triple.node.__class__.__name__, triple.node.pk))
