#!/usr/bin/env python

__author__ = "Icaro Raupp Henrique"
__copyright__ = ""
__credits__ = ["Icaro Raupp Henrique"]
__license__ = ""
__version__ = "2.2.1"
__maintainer__ = "Icaro Raupp Henrique"
__email__ = "icaro.henrique@cpca.pucrs.br"
__status__ = ""

import sys
import traceback

from os.path import splitext, split, join, basename

ICON_URL = "http://www.n3phele.com/qiimeIcon"

# Default values if parameters are not provided
QIIME_IMAGE = "360427"
NODE_COUNT = "1"
FLAVOR = "101"

# Constants
VM_NAME = "vmGen"
OPTIONAL_VAR = "OPTIONAL_FILES"
PATH_FIX = "source /home/ubuntu/sandbox/qiime_software/activate.sh ;"

# Default values when parameters have no default values set
STR_DEFAULT = "\"\""
NUM_DEFAULT = 0

type_converter = {}
# Parameters types
type_converter['string'] = "string"
type_converter['int'] = "int"
type_converter['long'] = "int"
type_converter['float'] = "float"
type_converter['boolean'] = "boolean"

# Input/output types
type_converter['multiple_choice'] = "multiple_select"
type_converter['existing_filepath'] = "file"
type_converter['existing_filepaths'] = "repeat"
type_converter['existing_dirpath'] = "input_dir"
type_converter['existing_path'] = "input_dir"
type_converter['new_filepath'] = "file"
type_converter['new_dirpath'] = "output_dir"
type_converter['new_path'] = "output_dir"
type_converter['blast_db'] = "blast_db"

# Unsupported types
type_converter['choice'] = "select"

parameter_types = [
    type_converter['string'], type_converter['int'],
    type_converter['long'], type_converter['float'],
    type_converter['boolean']]
unsupported_types = [type_converter['choice']]

# Output directories that will be zipped
dirs_types = [
    type_converter['existing_path'], type_converter['existing_dirpath'],
    type_converter['new_path'], type_converter['new_dirpath']]
output_dirs = []


class OptionInfo(object):
    def __init__(self, option):
        self.name = option.get_opt_string().replace("-", "")

        try:
            self.type = "boolean" if option.action in [
                'store_true',
                'store_false'] else type_converter[option.type]
        except KeyError:
            raise ValueError(
                "Option type %s not supported on Galaxy" % option.type)

        self.short_opt = option._short_opts[0] if len(option._short_opts) > 0\
            else None
        self.long_opt = option._long_opts[0] if len(option._long_opts) > 0\
            else None

        self.label = option.help

        self.default = None
        if self.type == "boolean":
            self.default = "False"
        else:
            self.default = str(option.default) if option.default.__class__ !=\
                tuple else None

        if self.type == "select":
            self.choices = option.choices
        elif self.type == "multiple_select":
            self.choices = option.mchoices
        else:
            self.choices = None

        self.format = None
        if self.type == "output":
            self.format = "txt"
        elif self.type == "output_dir":
            self.format = "tgz"

    def get_command_line_string(self):
        return self.short_opt if self.short_opt else self.long_opt

    def is_short_command_line(self):
        return self.short_opt is not None

    def has_default(self):
        return self.default is not None

    def get_label(self):
        label = self.short_opt + "/" if self.short_opt else ""
        label = label + self.long_opt if self.long_opt else label[:-1]
        label += ": " + self.label.replace("%default", str(self.default))
        return label


class ScriptInfo(object):
    def __init__(self, script_info, script_name):
        self.name_param = script_name.replace("_", " ")
        self.description_param = script_info['brief_description']
        self.version_param = script_info['version']

        self.required_options = map(
            OptionInfo, script_info['required_options'])
        try:
            self.optional_options = map(
                OptionInfo, script_info['optional_options'])
        except KeyError:
            self.optional_options = []

        required_params =\
            self.extract_required_parameters(self.required_options)
        optional_params =\
            self.extract_optional_parameters(self.optional_options)
        self.parameters_list = [required_params, optional_params]

        required_output_files =\
            self.extract_required_output_files(self.required_options)
        optional_output_files =\
            self.extract_optional_output_files(self.optional_options)
        self.output_files_list =\
            [required_output_files, optional_output_files]

        required_input_files =\
            self.extract_required_input_files(self.required_options)
        optional_input_files =\
            self.extract_optional_input_files(self.optional_options)
        self.input_files_list = [required_input_files, optional_input_files]

    def extract_required_parameters(self, required_options):
        required_params = []
        for option in required_options:
            if option.type in parameter_types and\
                    option.type not in unsupported_types:
                param = {}
                param['type'] = option.type
                param['name'] = option.name
                param['label'] = option.label
                param['short_opt'] = option.short_opt
                param['long_opt'] = option.long_opt
                if option.default is not None:
                    param['default'] = option.default
                else:
                    param['default'] = None

                required_params.append(param)

        return required_params

    def extract_optional_parameters(self, optional_options):
        optional_params = []
        for option in optional_options:
            if option.type in parameter_types and\
                    option.type not in unsupported_types:
                param = {}
                param['type'] = option.type
                param['name'] = option.name
                param['label'] = option.label
                param['short_opt'] = option.short_opt
                param['long_opt'] = option.long_opt
                # Default can come as undeclared value (NoneType) or
                # default=None (str)
                if option.default is not None and\
                        option.default != "None":
                    param['default'] = option.default
                else:
                    param['default'] = None

                optional_params.append(param)

        return optional_params

    def extract_required_input_files(self, required_options):
        required_input_files = []
        for option in required_options:
            if option.type not in parameter_types and\
                    option.type not in unsupported_types:
                input_file = {}
                input_file['type'] = option.type
                input_file['name'] = option.name
                input_file['label'] = option.label
                input_file['short_opt'] = option.short_opt
                input_file['long_opt'] = option.long_opt
                required_input_files.append(input_file)

        return required_input_files

    def extract_optional_input_files(self, optional_options):
        optional_input_files = []
        for option in optional_options:
            if option.type not in parameter_types and\
                    option.type not in unsupported_types:
                input_file = {}
                input_file['type'] = option.type
                input_file['name'] = option.name
                input_file['label'] = option.label
                input_file['short_opt'] = option.short_opt
                input_file['long_opt'] = option.long_opt
                optional_input_files.append(input_file)

        return optional_input_files

    def extract_required_output_files(self, required_options):
        output_param = "-o"
        required_output_files = []
        for opt, idx in zip(required_options, range(len(required_options))):
            if opt.type not in parameter_types and\
                    opt.short_opt == output_param and\
                    opt.type not in unsupported_types:
                output_file = {}
                output_file['type'] = opt.type
                output_file['name'] = opt.name
                output_file['label'] = opt.label
                output_file['short_opt'] = opt.short_opt
                output_file['long_opt'] = opt.long_opt
                required_output_files.append(output_file)

                required_options.pop(idx)

                if opt.type in dirs_types:
                    output_dirs.append(opt.name)
                    output_file['type'] = "zip"

        return required_output_files

    def extract_optional_output_files(self, optional_options):
        output_param = "-o"
        optional_output_files = []
        for opt, idx in zip(optional_options, range(len(optional_options))):
            if opt.type not in parameter_types and\
                    opt.short_opt == output_param and\
                    opt.type not in unsupported_types:
                output_file = {}
                output_file['type'] = opt.type
                output_file['name'] = opt.name
                output_file['label'] = opt.label
                output_file['short_opt'] = opt.short_opt
                output_file['long_opt'] = opt.long_opt
                optional_output_files.append(output_file)

                optional_options.pop(idx)

                if opt.type in dirs_types:
                    output_dirs.append(opt.name)
                    output_file['type'] = "zip"

        return optional_output_files


def generate_nshell_header(info):
    header = ""
    header += fill_name(info.name_param) + '\n'
    header += fill_description(info.description_param) + '\n'
    header += fill_version(info.version_param) + '\n'
    header += fill_preferred() + '\n'
    header += fill_tags() + '\n'
    header += fill_privacy() + '\n'
    header += fill_icon() + '\n'

    # Some int values come with "None" as default
    # Put 0 to avoid type errors
    fill_none_int_defaults(info.parameters_list)

    header += fill_parameters(info.parameters_list) + '\n'
    header += fill_input_files(info.input_files_list) + '\n'
    header += fill_output_files(info.output_files_list) + '\n'

    return header


def fill_none_int_defaults(parameters_list):
    for parameter in parameters_list[0]:
        if parameter['type'] == type_converter['float'] or\
                parameter['type'] == type_converter['int'] or\
                parameter['type'] == type_converter['long'] and\
                parameter['default'] is not None:
            if parameter['default'] == "None":
                parameter['default'] = 0
    for parameter in parameters_list[1]:
        if parameter['type'] == type_converter['float'] or\
                parameter['type'] == type_converter['int'] or\
                parameter['type'] == type_converter['long'] and\
                parameter['default'] is not None:
            if parameter['default'] == "None":
                parameter['default'] = 0


def fill_name(name_param):
    name = ""
    name += "name\t\t: "
    name += name_param

    return name


def fill_description(description_param):
    description = ""
    description += "description\t: "
    description += description_param

    return description


def fill_version(version_param):
    version = ""
    version += "version\t\t: "
    version += version_param.split("-")[0]

    return version


def fill_preferred():
    preferred = ""
    preferred += "preferred\t: "
    preferred += "true"

    return preferred


def fill_tags():
    tags = ""
    tags += "tags\t\t: "
    tags += "qiime"

    return tags


def fill_privacy():
    privacy = ""
    privacy += "public\t\t: "
    privacy += "true"

    return privacy


def fill_icon():
    icon = ""
    icon += "icon\t\t:"
    icon += ICON_URL + "qiime"

    return icon


def fill_parameters(parameters_list):
    required_params = parameters_list[0]
    optional_params = parameters_list[1]

    parameters = ""
    parameters += "parameters\t:"

    for parameter in required_params:
        parameters += "\n" + "\t"
        parameters += parameter['type'] + " " + parameter['name']
        parameters += " = "

        if parameter['default'] != "None":
            parameters += value_format(parameter['type'], parameter['default'])
        else:
            parameters += value_format(parameter['type'], parameter['name'])
        parameters += " # " + parameter['label']

    for parameter in optional_params:
        parameters += "\n" + "\t"
        parameters += "optional "
        parameters += parameter['type'] + " " + parameter['name']
        parameters += " = "

        if parameter['default'] is not None:
            parameters += value_format(parameter['type'], parameter['default'])
        else:
            # If parameter has no default value,
            # put "" for strings and 0 for numeric values
            parameters += value_format(
                parameter['type'],
                STR_DEFAULT if parameter['type'] == type_converter['string']
                else NUM_DEFAULT)
        parameters += " # " + parameter['label']

    return parameters


# String values need quotes, bool and numeric values doesn't
def value_format(type_, value):
    if type_ == type_converter['string']:
        return "\"{0}\"".format(value)
    else:
        return "{0}".format(value)


def fill_input_files(input_files_list):
    required_input = input_files_list[0]
    optional_input = input_files_list[1]

    input_files = ""
    input_files += "input files:"

    for input_file in required_input:
        input_files += "\n" + "\t"
        input_files += input_file['name'] + "." + input_file['type']
        input_files += " # " + input_file['label']

    for input_file in optional_input:
        input_files += "\n" + "\t"
        input_files += "optional "
        input_files += input_file['name'] + "." + input_file['type']
        input_files += " # " + input_file['label']

    return input_files


def fill_output_files(output_files_list):
    required_output = output_files_list[0]
    optional_output = output_files_list[1]

    output_files = ""
    output_files += "output files:"

    for output_file in required_output:
        output_files += "\n" + "\t"
        output_files += output_file['name'] + "." + output_file['type']
        output_files += " # " + output_file['label']

    for output_file in optional_output:
        output_files += "\n" + "\t"
        # Optional output not supported
        # output_files += "optional "
        output_files += output_file['name'] + "." + output_file['type']
        output_files += " # " + output_file['label']

    return output_files


def nshell_info(filename):
    info = ""
    info += "# " + filename + "\n"
    info += "# " + "Created automatically by the nshell generator" + "\n"

    return info


def generate_nshell_commands(info, params_cmd):
    commands = ""
    commands += params_cmd['zone'] + ":" + "\n"

    # $$vmGen = CREATEVM ...
    commands += "\t" + "$$" + VM_NAME + " = "\
        + command_createVM(info, params_cmd) + "\n"
    # ON vmGen [--produces ...]
    commands += "\n\t" + "ON $$" + VM_NAME + " " + generate_produces() + "\n"

    # script_name.py <required_arguments>
    required_command = command_onVM_required(info, params_cmd)

    # OPTIONAL_VAR=""
    commands += "\t\t" + OPTIONAL_VAR + "=\"\" ;\n"

    commands += command_onVM_optional_files(info) + "\n"

    commands += "\n\t\t" + PATH_FIX + "\n"

    # Concatenate additional nshell expressions before script execution
    # if the file is supplied
    if params_cmd['concat'] is not None:
        with open(params_cmd['concat'], 'r') as concat_file:
            commands += "\n"
            line_text = concat_file.readline()
            while line_text != "":
                commands += "\t\t" + line_text
                line_text = concat_file.readline()

    commands += "\n\t\t" + required_command + " $" + OPTIONAL_VAR + " " +\
        command_onVM_optional_params(info) + " ;" + "\n"

    zips = generate_zips()
    if len(zips) > 0:
        commands += "\n\t\t" + zips

    return commands


def generate_produces():
    if len(output_dirs) > 0:
        produces = "--produces [\n{0}]"
        product_format = "\t\t{0}.zip: {0}.zip,\n"

        zips = ""
        for output in output_dirs:
            zips += product_format.format(output)

        # Need to remove ",\n" from last member
        return produces.format(zips[:-2])
    else:
        return ""


def generate_zips():
    if len(output_dirs) > 0:
        # Zip output folder contents
        # cd <folder_name> ;
        # zip -r <zip_name> ./ ;
        # mv <zip_name>.zip ../ ;
        zip_format =\
            "cd {0} ;\n\
        zip -r {0} ./ ;\n\
        mv {0}.zip ../ ;\n"

        zips = ""
        for output in output_dirs:
            zips += zip_format.format(output)

        return zips
    else:
        return ""


def command_createVM(info, params_cmd):
    command = "CREATEVM "

    command += "--name "
    if params_cmd['name'] is None:
        command += VM_NAME + " "
    else:
        command += params_cmd['name'] + " "

    command += "--imageRef "
    if params_cmd['image'] is None:
        command += QIIME_IMAGE + " "
    else:
        command += params_cmd['image'] + " "

    command += "--nodeCount "
    if params_cmd['nodes'] is None:
        command += NODE_COUNT + " "
    else:
        command += params_cmd['nodes'] + " "

    command += "--flavorRef "
    if params_cmd['flavor'] is None:
        command += FLAVOR + " "
    else:
        command += params_cmd['flavor'] + " "

    return command


def command_onVM_required(info, params_cmd):
    command = ""
    command += params_cmd['script'] + ".py "

    required_params = info.parameters_list[0]
    for parameter in required_params:
        command += ""
        if parameter['short_opt'] is not None:
            command += parameter['short_opt'] + " " + parameter['name']
        else:
            command += parameter['long_opt'] + "=" + parameter['name']

    required_input = info.input_files_list[0]
    for input_file in required_input:
        command += " "
        command += input_file['short_opt'] + " " +\
            input_file['name'] + "." + input_file['type']

    required_output = info.output_files_list[0]
    for output_file in required_output:
        command += " "
        command += output_file['short_opt'] + " " + output_file['name']
        # In the required output files, output folder can't be .zip
        if output_file['type'] != "zip":
            command += "." + output_file['type']

    return command


def command_onVM_optional_files(info):
    optional_checks = "\n\t\t# Optional input files"
    optional_input = info.input_files_list[1]
    for input_file in optional_input:
        optional_checks += "\n\t\t"
        optional_checks += if_optional_file(
            input_file['short_opt'],
            input_file['name'], input_file['type'], True)

    optional_checks += "\n\t\t# Optional output files"
    optional_output = info.output_files_list[1]
    for output_file in optional_output:
        optional_checks += "\n\t\t"
        optional_checks += if_optional_file(
            output_file['short_opt'],
            output_file['name'], output_file['type'], False)

    return optional_checks


def command_onVM_optional_params(info):
    optional_checks = ""

    optional_params = info.parameters_list[1]
    for parameter in optional_params:
        optional_checks += if_optional_parameter(
            parameter['short_opt'], parameter['long_opt'],
            parameter['name'], parameter['type'], parameter['default'])

    return optional_checks


def if_optional_parameter(short_opt, long_opt, name, type_, default):
    # -d <param>
    param_with_opt_format = "\" {0} \"+$${1}"
    # --d=<param>
    param_without_opt_format = "\" {0}=\"+$${1}"

    # $$<bool_param>?" -d $$<bool_param>":""
    if_format_bool = " $${0}?\" {1}\":\"\""
    # $$d!=<value>?" -d $$d":""
    if_format_others = " $${0}!={1}?{2}:\"\""

    param = ""
    if short_opt is not None:
        param = param_with_opt_format.format(short_opt, name)
    else:
        param = param_without_opt_format.format(long_opt, name)

    # Different checks for bool and int and string
    # <bool>? ...
    # [<int>, <string>]!=<default>? ...
    if_expr = ""
    if type_ == "bool":
        if_expr = if_format_bool.format(name, param)
    else:
        # Put parameters in command if they are not empty
        value = STR_DEFAULT
        if type_ == "int" or type_ == "float":
            # Numeric values can't be compared to empty string, use default
            # If no default is set, use -1 as placeholder
            value = default if default is not None else NUM_DEFAULT
            if_expr = if_format_others.format(name, value, param)
        elif type_ == "string":
            if_expr = if_format_others.format(name, value, param)

    return if_expr


# Boolean parameter needed because "optional" output is not supported
def if_optional_file(short_opt, name, ext, is_optional):
    # file.txt
    file_format = "{0}.{1}"
    # -p file.txt
    param_with_file_format = "{0} {1}"
    # if [ -f file.txt ]; then OPTIONAL_VAR="$OPTIONAL_VAR -p file.txt"; fi;
    if_format = "if [ -f {0} ]; then {1}=\"${1} {2}\"; fi;"
    if_format_non_optional = "{0}=\"${0} {1}\";"

    file_with_ext = file_format.format(name, ext)
    # If it's and output folder (will be zipped)
    # remove .zip from QIIME parameter name
    # e.g. qiime_script.py -o out.zip -> qiime_script.py -o out
    if ext == "zip":
        file_with_ext = file_with_ext.split(".")[0]

    param_with_file = param_with_file_format.format(short_opt, file_with_ext)

    if is_optional:
        return if_format.format(file_with_ext, OPTIONAL_VAR, param_with_file)
    else:
        return if_format_non_optional.format(OPTIONAL_VAR, param_with_file)


def make_nshell(script_path, output_dir, params_cmd):
    dir_path, command = split(script_path)
    script_name, extension = splitext(command)

    try:
        script_qiime = __import__(script_name)

        info = ScriptInfo(script_qiime.script_info, script_name)

        nshell_header = generate_nshell_header(info)

        params_cmd['script'] = script_name
        nshell_commands = generate_nshell_commands(info, params_cmd)

        filename = script_name+".n"

        nshell_file = open(join(output_dir, filename), 'w')

        nshell_file.write(nshell_info(filename))
        nshell_file.write(nshell_header)
        nshell_file.write(nshell_commands)

        nshell_file.close()
    except Exception as e:
        top = traceback.extract_tb(sys.exc_info()[2])[-1]
        print "Error processing \'{0}\': ".format(script_name) +\
            ", ".join([type(e).__name__, basename(top[0]),
            str(top[1])]) + ", " + str(e)
