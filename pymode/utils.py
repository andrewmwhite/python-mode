""" Pymode utils. """
import json
import os.path
import sys
import threading
from contextlib import contextmanager

import vim # noqa


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


DEBUG = int(vim.eval('g:pymode_debug'))
PY2 = sys.version_info[0] == 2


def pymode_message(content):
    """ Show message. """

    vim.command('call pymode#wide_message("%s")' % str(content))


def pymode_confirm(yes=True, msg='Do the changes:'):
    """ Confirmation.

    :return bool:

    """
    default = 'yes' if yes else 'no'
    action = pymode_input(msg, default)
    return action and 'yes'.startswith(action)


def pymode_inputlist(msg, opts):
    """ Get user choice.

    :return str: A choosen option

    """
    choices = ['[Pymode] %s' % msg]
    choices += ["%s. %s" % (num, opt) for num, opt in enumerate(opts, 1)]
    try:
        input_str = int(vim.eval('inputlist(%s)' % json.dumps(choices)))
    except (KeyboardInterrupt, ValueError):
        input_str = 0

    if not input_str:
        pymode_message('Cancelled!')
        return False

    try:
        return opts[input_str - 1]
    except (IndexError, ValueError):
        pymode_error('Invalid option: %s' % input_str)
        return pymode_inputlist(msg, opts)


def pymode_input(umsg, udefault='', opts=None):
    """ Get user input.

    :return str: A user input

    """
    msg = '[Pymode] %s ' % umsg
    default = udefault

    if default != '':
        msg += '[%s] ' % default

    try:
        vim.command('echohl Debug')
        input_str = vim.eval('input("%s> ")' % msg)
        vim.command('echohl none')
    except KeyboardInterrupt:
        input_str = ''

    return input_str or default


def pymode_error(content):
    """ Show error. """

    vim.command('call pymode#error("%s")' % str(content))


def catch_and_print_exceptions(func):
    """ Catch any exception.

    :return func:

    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (Exception, vim.error) as e: # noqa
            if DEBUG:
                raise
            pymode_error(e)
            return None
    return wrapper


@contextmanager
def silence_stderr():
    """ Redirect stderr. """

    with threading.Lock():
        stderr = sys.stderr
        sys.stderr = StringIO()

    yield

    with threading.Lock():
        sys.stderr = stderr


def patch_paths():
    """ Function description. """

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

    if PY2:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs2'))
    else:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs3'))


debug = lambda _: None

if DEBUG:
    def debug(msg): # noqa
        """ Debug message. """

        print(msg)
