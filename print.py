import sys


class Print(object):
    @staticmethod
    def print_etr(txt):
        print(txt, file=sys.stderr)

    @staticmethod
    def print_str(txt):
        print(txt, file=sys.stdout)
