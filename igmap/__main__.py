import argparse

from .vidjil import VidjilWrapper


def main():
    print(VidjilWrapper().run_cmd('input', 'output'))
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('preset')           # positional argument
    parser.add_argument('input')           # positional argument
    parser.add_argument('output')
    parser.add_argument('-m', '--mode')      
    parser.add_argument('-v', '--verbose',
                        action='store_true')  # on/off flag

    args = parser.parse_args()
    print(args.filename, args.count, args.verbose)

if __name__ == '__main__':
    main()