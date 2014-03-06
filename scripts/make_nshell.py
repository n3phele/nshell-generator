#!/usr/bin/env python

__author__ = "Icaro Raupp Henrique"
__copyright__ = ""
__credits__ = ["Icaro Raupp Henrique"]
__license__ = ""
__version__ = "2.2"
__maintainer__ = "Icaro Raupp Henrique"
__email__ = "icaro.henrique@cpca.pucrs.br"
__status__ = ""

from cogent.util.option_parsing import (
    parse_command_line_parameters, make_option)
from nshell_generator import make_nshell

script_info = {}
script_info['brief_description'] =\
    """Generates a nshell file from a given QIIME script"""
script_info['script_description'] = """Reads the input script, looks for its\
 'script_info' and extract all the information necessary to generate the XML\
 file."""
script_info['script_usage'] =\
    [("Example:", "Generate a \"nshell\" file from the \"qimme.py\" script\
    that will run in HPZone1 and will be saved in the \"output\" folder.",
        "%prog -o ../output -s qiime.py -z HPZone1 -m nshell)")]
script_info['output_description'] =\
    "A nshell file that can be run in the n3phele environment"
script_info['required_options'] = [
    make_option('-s', '--script_path', type="existing_filepath",
                help='the QIIME python script filepath to generate'),
    make_option('-o', '--output_dir', type="existing_dirpath",
                help='output directory where to save the nshell file'),
    make_option('-z', '--zone', type="string",
                help='zone to run the command')
]
script_info['optional_options'] = [
    make_option('-m', '--name', type="string",
                help='machine name'),
    make_option('-i', '--image', type="string",
                help='machine image (imageId for Amazon) reference'),
    make_option('-n', '--nodes', type="string",
                help='quantity of nodes to run the command'),
    make_option('-f', '--flavor', type="string",
                help='machine flavor (instanceType for Amazon) reference'),
    make_option('-c', '--concat', type="existing_filepath",
                help='nshell expressions to concatenate and run\
                before the script execution'),
    make_option('--amazon', default=False,
                help='adapt CREATEVM parameters for Amazon')
]
script_info['version'] = __version__

if __name__ == '__main__':
    option_parser, opts, args = parse_command_line_parameters(**script_info)
    script_path = opts.script_path
    output_dir = opts.output_dir

    params_cmd = {}
    params_cmd['zone'] = opts.zone
    params_cmd['name'] = opts.name
    params_cmd['image'] = opts.image
    params_cmd['nodes'] = opts.nodes
    params_cmd['flavor'] = opts.flavor
    params_cmd['concat'] = opts.concat
    params_cmd['amazon'] = opts.amazon

    make_nshell(script_path, output_dir, params_cmd)
