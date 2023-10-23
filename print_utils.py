import sys


def debug_print(msg: str) -> None:
    """
    This function is used to print debug information to stdout, if the global variable DEBUG
    is set to True.

    :param msg: Debug message to be printed
    :return: None
    """
    globals_dict = globals()

    debug_mode = globals_dict.get('DEBUG', True)

    if debug_mode:
        print(f"DEBUG: {msg}")

    return


def print_info(msg: str) -> None:
    """
    Prints a warning message to stdout.

    :param msg: The warning message to be printed
    :return: None
    """

    print(f"INFO: {msg}", file=sys.stdout)

    return


def print_warn(msg: str) -> None:
    """
    Prints a warning message to stderr.

    :param msg: The warning message to be printed
    :return: None
    """

    print(f"WARNING: {msg}", file=sys.stderr)

    return


def print_error(msg: str) -> None:
    """
    Prints a warning message to stderr.

    :param msg: The warning message to be printed
    :return: None
    """

    print(f"ERROR: {msg}", file=sys.stderr)

    return



