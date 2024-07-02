# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
import argparse
import sys
from pathlib import Path
from importlib import import_module

from ansys.scadeone import __version__

def main():
    """Scade One Python command line"""
    parser = argparse.ArgumentParser(prog="pyscadeone",
                                     description="Scade One API command line tool",
                                     epilog="For more information see <<pyscadeone one URL>>",
                                     fromfile_prefix_chars="@")
    parser.add_argument("--version",
                        action="version",
                        version=__version__,
                        help="%(prog)s version")
    parser.add_argument("--project",
                        help="Scade One project")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbosity",
                       action="count",
                       default=0)
    group.add_argument("-q",
                       "--quiet",
                       action="store_true")

    subparser = parser.add_subparsers(help="sub-commands,  command --help for help")
    # Code command
    code_parser = subparser.add_parser('code', help='code generation command')
    code_parser.add_argument('--job', required=True, help="job name")
    code_parser.add_argument('--job-out', help="job output directory", default=None)
    # Test command
    test_parser = subparser.add_parser('test', help="testing command")
    test_parser.add_argument('--test', help="execute test")

    # Script mode
    # Test command
    script_parser = subparser.add_parser('script', help="script command")
    script_parser.add_argument('--file',
                               help="load & run script file",
                               dest='script')
    script_parser.add_argument('--module',
                               help="load & run module")
    script_parser.add_argument('--path',
                               action='append',
                               help="module path. Several --path can be given",
                               dest='module_path')

    # Parsing
    args = parser.parse_args()

    print(args)

    # Scripting
    if args.script:
        script = Path(args.script).with_suffix('')
        args.module = script.name
        args.module_path = [str(script.parent)]
    if args.module:
        if args.module_path:
            sys.path.extend(args.module_path)
        try:
            import_module(args.module)
            exit(0)
        except Exception as e:
            print(str(e))
            exit(1)


if __name__ == "__main__":
    main()