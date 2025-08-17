import json
import platform
import sys
import time
import datetime
from functools import wraps
from .constants import *
import inspect



g_time_start = 0
g_time_end = 0
g_time_delta = 0


def timer_start():
    """开始计时"""
    global g_time_start
    g_time_start = time.time()


def timer_stop():
    """停止计时并返回毫秒"""
    global g_time_delta, g_time_end
    g_time_end = time.time()
    g_time_delta = g_time_end - g_time_start
    return int(g_time_delta * 1000)


def _timeit(func):
    """函数执行时间装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("{} executed in {:.4f} seconds".format(func.__name__, end - start))
        return result

    return wrapper


def _timeit_summary(func):
    """
    Same as the timeit decorator except that the value is shown as an averave
    Put @_timeit_summary as a decorator to a function to get the time spent in that function printed out

    :param func: Decorated function
    :type func:
    :return:     Execution time for the decorated function
    :rtype:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        global _timeit_counter, _timeit_total

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        _timeit_counter += 1
        _timeit_total += end - start
        if _timeit_counter > MAX_TIMEIT_COUNT:
            print(
                "{} executed in {:.4f} seconds".format(
                    func.__name__, _timeit_total / MAX_TIMEIT_COUNT
                )
            )
            _timeit_counter = 0
            _timeit_total = 0
        return result

    return wrapper


def formatted_datetime_now() -> str:
    """返回格式化当前时间"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


# 系统检测函数
def running_linux() -> bool:
    return sys.platform.startswith("linux")


def running_mac() -> bool:
    return sys.platform.startswith("darwin")


def running_windows() -> bool:
    return sys.platform.startswith("win")


# ====================================================================== #
# One-liner functions that are handy as f_ck                             #
# ====================================================================== #
def rgb(red, green, blue):
    """
    Given integer values of Red, Green, Blue, return a color string "#RRGGBB"
    :param red:   Red portion from 0 to 255
    :type red:    (int)
    :param green: Green portion from 0 to 255
    :type green:  (int)
    :param blue:  Blue portion from 0 to 255
    :type  blue:  (int)
    :return:      A single RGB String in the format "#RRGGBB" where each pair is a hex number.
    :rtype:       (str)
    """
    red = min(int(red), 255) if red > 0 else 0
    blue = min(int(blue), 255) if blue > 0 else 0
    green = min(int(green), 255) if green > 0 else 0
    return "#%02x%02x%02x" % (red, green, blue)




def _random_error_emoji():
    c = random.choice(EMOJI_BASE64_SAD_LIST)
    return c


def _random_happy_emoji():
    c = random.choice(EMOJI_BASE64_HAPPY_LIST)
    return c



def __send_dict(ip, port, dict_to_send):
    """
    Send a dictionary to the upgrade server and get back a dictionary in response
    :param ip:           ip address of the upgrade server
    :type ip:            str
    :param port:         port number
    :type port:          int | str
    :param dict_to_send: dictionary of items to send
    :type dict_to_send:  dict
    :return:             dictionary that is the reply
    :rtype:              dict
    """

    # print(f'sending dictionary to ip {ip} port {port}')
    try:
        # Create a socket object
        s = socket.socket()

        s.settimeout(5.0)  # set a 5 second timeout

        # connect to the server on local computer
        s.connect((ip, int(port)))
        # send a python dictionary
        s.send(json.dumps(dict_to_send).encode())

        # receive data from the server
        reply_data = s.recv(1024).decode()
        # close the connection
        s.close()
    except Exception as e:
        # print(f'Error sending to server:', e)
        # print(f'payload:\n', dict_to_send)
        reply_data = e
    try:
        data_dict = json.loads(reply_data)
    except Exception:
        # print(f'UPGRADE THREAD - Error decoding reply {reply_data} as a dictionary. Error = {e}')
        data_dict = {}
    return data_dict


def __get_linux_distribution():
    line_tuple = ("Linux Distro", "Unknown", "No lines Found in //etc//os-release")
    try:
        with open("/etc/os-release") as f:
            data = f.read()
        lines = data.split("\n")
        for line in lines:
            if line.startswith("PRETTY_NAME"):
                line_split = line.split("=")[1].strip('"')
                line_tuple = tuple(line_split.split(" "))
                return line_tuple
    except Exception:
        line_tuple = (
            "Linux Distro",
            "Exception",
            "Error reading//processing //etc//os-release",
        )

    return line_tuple




def get_versions():
    """
    Returns a human-readable string of version numbers for:

    Python version
    Platform (Win, Mac, Linux)
    Platform version (tuple with information from the platform module)
    PySimpleGUI Port (PySimpleGUI in this case)
    tkinter version
    PySimpleGUI version
    The location of the PySimpleGUI.py file

    The format is a newline between each value and descriptive text for each line

    :return:
    :rtype:  str
    """
    if running_mac():
        platform_name, platform_ver = "Mac", platform.mac_ver()
    elif running_windows():
        platform_name, platform_ver = "Windows", platform.win32_ver()
    elif running_linux():
        platform_name, platform_ver = "Linux", platform.libc_ver()
    else:
        platform_name, platform_ver = "Unknown platorm", "Unknown platform version"

    versions = "Python Interpeter: {}\nPython version: {}.{}.{}\nPlatform: {}\nPlatform version: {}\nPort: {}\ntkinter version: {}\nPySimpleGUI version: {}\nPySimpleGUI filename: {}".format(
        sys.executable,
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
        platform_name,
        platform_ver,
        port,
        tclversion_detailed,
        ver,
        __file__,
    )
    return versions




def user_settings_filename(filename=None, path=None):
    """
    Sets the filename and path for your settings file.  Either paramter can be optional.

    If you don't choose a path, one is provided for you that is OS specific
    Windows path default = users/name/AppData/Local/PySimpleGUI/settings.

    If you don't choose a filename, your application's filename + '.json' will be used.

    Normally the filename and path are split in the user_settings calls. However for this call they
    can be combined so that the filename contains both the path and filename.

    :param filename: The name of the file to use. Can be a full path and filename or just filename
    :type filename:  (str)
    :param path:     The folder that the settings file will be stored in. Do not include the filename.
    :type path:      (str)
    :return:         The full pathname of the settings file that has both the path and filename combined.
    :rtype:          (str)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get_filename(filename, path)


def user_settings_delete_filename(filename=None, path=None, report_error=False):
    """
    Deltes the filename and path for your settings file.  Either paramter can be optional.
    If you don't choose a path, one is provided for you that is OS specific
    Windows path default = users/name/AppData/Local/PySimpleGUI/settings.
    If you don't choose a filename, your application's filename + '.json' will be used
    Also sets your current dictionary to a blank one.

    :param report_error:
    :param filename: The name of the file to use. Can be a full path and filename or just filename
    :type filename:  (str)
    :param path:     The folder that the settings file will be stored in. Do not include the filename.
    :type path:      (str)
    """
    settings = UserSettings._default_for_function_interface
    settings.delete_file(filename, path, report_error=report_error)


def user_settings_set_entry(key, value):
    """
    Sets an individual setting to the specified value.  If no filename has been specified up to this point,
    then a default filename will be used.
    After value has been modified, the settings file is written to disk.

    :param key:   Setting to be saved. Can be any valid dictionary key type
    :type key:    (Any)
    :param value: Value to save as the setting's value. Can be anything
    :type value:  (Any)
    """
    settings = UserSettings._default_for_function_interface
    settings.set(key, value)


def user_settings_delete_entry(key, silent_on_error=None):
    """
    Deletes an individual entry.  If no filename has been specified up to this point,
    then a default filename will be used.
    After value has been deleted, the settings file is written to disk.

    :param key: Setting to be saved. Can be any valid dictionary key type (hashable)
    :type key:  (Any)
    :param silent_on_error: Determines if an error popup should be shown if an error occurs. Overrides the silent onf effort setting from initialization
    :type silent_on_error:  (bool)
    """
    settings = UserSettings._default_for_function_interface
    settings.delete_entry(key, silent_on_error=silent_on_error)


def user_settings_get_entry(key, default=None):
    """
    Returns the value of a specified setting.  If the setting is not found in the settings dictionary, then
    the user specified default value will be returned.  It no default is specified and nothing is found, then
    None is returned.  If the key isn't in the dictionary, then it will be added and the settings file saved.
    If no filename has been specified up to this point, then a default filename will be assigned and used.
    The settings are SAVED prior to returning.

    :param key:     Key used to lookup the setting in the settings dictionary
    :type key:      (Any)
    :param default: Value to use should the key not be found in the dictionary
    :type default:  (Any)
    :return:        Value of specified settings
    :rtype:         (Any)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get(key, default)


def user_settings_save(filename=None, path=None):
    """
    Saves the current settings dictionary.  If a filename or path is specified in the call, then it will override any
    previously specitfied filename to create a new settings file.  The settings dictionary is then saved to the newly defined file.

    :param filename: The fFilename to save to. Can specify a path or just the filename. If no filename specified, then the caller's filename will be used.
    :type filename:  (str)
    :param path:     The (optional) path to use to save the file.
    :type path:      (str)
    :return:         The full path and filename used to save the settings
    :rtype:          (str)
    """
    settings = UserSettings._default_for_function_interface
    return settings.save(filename, path)


def user_settings_load(filename=None, path=None):
    """
    Specifies the path and filename to use for the settings and reads the contents of the file.
    The filename can be a full filename including a path, or the path can be specified separately.
    If  no filename is specified, then the caller's filename will be used with the extension ".json"

    :param filename: Filename to load settings from (and save to in the future)
    :type filename:  (str)
    :param path:     Path to the file. Defaults to a specific folder depending on the operating system
    :type path:      (str)
    :return:         The settings dictionary (i.e. all settings)
    :rtype:          (dict)
    """
    settings = UserSettings._default_for_function_interface
    return settings.load(filename, path)


def user_settings_file_exists(filename=None, path=None):
    """
    Determines if a settings file exists.  If so a boolean True is returned.
    If either a filename or a path is not included, then the appropriate default
    will be used.

    :param filename: Filename to check
    :type filename:  (str)
    :param path:     Path to the file. Defaults to a specific folder depending on the operating system
    :type path:      (str)
    :return:         True if the file exists
    :rtype:          (bool)
    """
    settings = UserSettings._default_for_function_interface
    return settings.exists(filename=filename, path=path)


def user_settings_write_new_dictionary(settings_dict):
    """
    Writes a specified dictionary to the currently defined settings filename.

    :param settings_dict: The dictionary to be written to the currently defined settings file
    :type settings_dict:  (dict)
    """
    settings = UserSettings._default_for_function_interface
    settings.write_new_dictionary(settings_dict)


def user_settings_silent_on_error(silent_on_error=False):
    """
    Used to control the display of error messages.  By default, error messages are displayed to stdout.

    :param silent_on_error: If True then all error messages are silenced (not displayed on the console)
    :type silent_on_error:  (bool)
    """
    settings = UserSettings._default_for_function_interface
    settings.silent_on_error = silent_on_error


def user_settings():
    """
    Returns the current settings dictionary.  If you've not setup the filename for the
    settings, a default one will be used and then read.
    :return:            The current settings dictionary as a dictionary or a nicely formatted string representing it
    :rtype:             (dict or str)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get_dict()


def user_settings_object():
    """
    Returns the object that is used for the function version of this API.
    With this object you can use the object interface, print it out in a nice format, etc.

    :return:    The UserSettings obect used for the function level interface
    :rtype:     (UserSettings)
    """
    return UserSettings._default_for_function_interface



"""
These are the functions used to implement the subprocess APIs (Exec APIs) of PySimpleGUI

"""


def execute_command_subprocess(
    command,
    *args,
    wait=False,
    cwd=None,
    pipe_output=False,
    merge_stderr_with_stdout=True,
    stdin=None,
):
    """
    Runs the specified command as a subprocess.
    By default the call is non-blocking.
    The function will immediately return without waiting for the process to complete running. You can use the returned Popen object to communicate with the subprocess and get the results.
    Returns a subprocess Popen object.

    :param command:                  The command/file to execute. What you would type at a console to run a program or shell command.
    :type command:                   (str)
    :param wait:                     If True then wait for the subprocess to finish
    :type wait:                      (bool)
    :param cwd:                      Working directory to use when executing the subprocess
    :type cwd:                       (str))
    :param pipe_output:              If True then output from the subprocess will be piped. You MUST empty the pipe by calling execute_get_results or your subprocess will block until no longer full
    :type pipe_output:               (bool)
    :param merge_stderr_with_stdout: If True then output from the subprocess stderr will be merged with stdout. The result is ALL output will be on stdout.
    :type merge_stderr_with_stdout:  (bool)
    :param stdin:                    Value passed to the Popen call. Defaults to subprocess.DEVNULL so that the pyinstaller created executable work correctly
    :type stdin:                     (bool)
    :return:                         Popen object
    :rtype:                          (subprocess.Popen)
    """
    if stdin is None:
        stdin = subprocess.DEVNULL
    try:
        if args is not None:
            expanded_args = " ".join(args)
            # print('executing subprocess command:',command, 'args:',expanded_args)
            if command[0] != '"' and " " in command:
                command = '"' + command + '"'
            # print('calling popen with:', command +' '+ expanded_args)
            # sp = subprocess.Popen(command +' '+ expanded_args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=cwd)
            if pipe_output:
                if merge_stderr_with_stdout:
                    sp = subprocess.Popen(
                        command + " " + expanded_args,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        cwd=cwd,
                        stdin=stdin,
                    )
                else:
                    sp = subprocess.Popen(
                        command + " " + expanded_args,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=cwd,
                        stdin=stdin,
                    )
            else:
                sp = subprocess.Popen(
                    command + " " + expanded_args,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    cwd=cwd,
                    stdin=stdin,
                )
        else:
            sp = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                stdin=stdin,
            )
        if wait:
            out, err = sp.communicate()
            if out:
                print(out.decode("utf-8"))
            if err:
                print(err.decode("utf-8"))
    except Exception as e:
        warnings.warn("Error in execute_command_subprocess {}".format(e), UserWarning)
        _error_popup_with_traceback(
            "Error in execute_command_subprocess",
            e,
            "command={}".format(command),
            "args={}".format(args),
            "cwd={}".format(cwd),
        )
        sp = None
    return sp


def execute_py_file(
    pyfile,
    parms=None,
    cwd=None,
    interpreter_command=None,
    wait=False,
    pipe_output=False,
    merge_stderr_with_stdout=True,
):
    """
    Executes a Python file.
    The interpreter to use is chosen based on this priority order:
        1. interpreter_command paramter
        2. global setting "-python command-"
        3. the interpreter running running PySimpleGUI
    :param pyfile:                   the file to run
    :type pyfile:                    (str)
    :param parms:                    parameters to pass on the command line
    :type parms:                     (str)
    :param cwd:                      the working directory to use
    :type cwd:                       (str)
    :param interpreter_command:      the command used to invoke the Python interpreter
    :type interpreter_command:       (str)
    :param wait:                     the working directory to use
    :type wait:                      (bool)
    :param pipe_output:              If True then output from the subprocess will be piped. You MUST empty the pipe by calling execute_get_results or your subprocess will block until no longer full
    :type pipe_output:               (bool)
    :param merge_stderr_with_stdout: If True then output from the subprocess stderr will be merged with stdout. The result is ALL output will be on stdout.
    :type merge_stderr_with_stdout:  (bool)
    :return:                         Popen object
    :rtype:                          (subprocess.Popen) | None
    """

    if cwd is None:
        # if the specific file is not found (not an absolute path) then assume it's relative to '.'
        if not os.path.exists(pyfile):
            cwd = "."

    if pyfile[0] != '"' and " " in pyfile:
        pyfile = '"' + pyfile + '"'
    if interpreter_command is not None:
        python_program = interpreter_command
    else:
        # use the version CURRENTLY RUNNING if nothing is specified. Previously used the one from the settings file
        # ^ hmmm... that's not the code is doing now... it's getting the one from the settings file first
        pysimplegui_user_settings.load()  # Refresh the settings just in case they've changed via another program
        python_program = pysimplegui_user_settings.get("-python command-", "")
        if (
            python_program == ""
        ):  # if no interpreter set in the settings, then use the current one
            python_program = sys.executable
            # python_program = 'python' if running_windows() else 'python3'
    if parms is not None and python_program:
        sp = execute_command_subprocess(
            python_program,
            pyfile,
            parms,
            wait=wait,
            cwd=cwd,
            pipe_output=pipe_output,
            merge_stderr_with_stdout=merge_stderr_with_stdout,
        )
    elif python_program:
        sp = execute_command_subprocess(
            python_program,
            pyfile,
            wait=wait,
            cwd=cwd,
            pipe_output=pipe_output,
            merge_stderr_with_stdout=merge_stderr_with_stdout,
        )
    else:
        print("execute_py_file - No interpreter has been configured")
        sp = None
    return sp


def execute_py_get_interpreter():
    """
    Returns Python Interpreter from the system settings. If none found in the settings file
    then the currently running interpreter is returned.

    :return: Full path to python interpreter (uses settings file or sys.executable)
    :rtype:  (str)
    """
    pysimplegui_user_settings.load()  # Refresh the settings just in case they've changed via another program
    interpreter = pysimplegui_user_settings.get("-python command-", "")
    if interpreter == "":
        interpreter = sys.executable
    return interpreter


def execute_py_get_running_interpreter():
    """
    Returns the command that is currently running.

    :return: Full path to python interpreter (uses sys.executable)
    :rtype:  (str)
    """
    return sys.executable


def execute_editor(file_to_edit, line_number=None):
    """
    Runs the editor that was configured in the global settings and opens the file to a specific line number.
    Two global settings keys are used.
    '-editor program-' the command line used to startup your editor. It's set
        in the global settings window or by directly manipulating the PySimpleGUI settings object
    '-editor format string-' a string containing 3 "tokens" that describes the command that is executed
            <editor> <file> <line>
    :param file_to_edit: the full path to the file to edit
    :type file_to_edit:  (str)
    :param line_number:  optional line number to place the cursor
    :type line_number:   (int)
    :return:             Popen object
    :rtype:              (subprocess.Popen) | None
    """
    if (
        file_to_edit is not None
        and len(file_to_edit) != 0
        and file_to_edit[0] not in ('"', "'")
        and " " in file_to_edit
    ):
        file_to_edit = '"' + file_to_edit + '"'
    pysimplegui_user_settings.load()  # Refresh the settings just in case they've changed via another program
    editor_program = pysimplegui_user_settings.get("-editor program-", None)
    if editor_program is not None:
        format_string = pysimplegui_user_settings.get("-editor format string-", None)
        # if no format string, then just launch the editor with the filename
        if not format_string or line_number is None:
            sp = execute_command_subprocess(editor_program, file_to_edit)
        else:
            command = _create_full_editor_command(
                file_to_edit, line_number, format_string
            )
            # print('final command line = ', command)
            sp = execute_command_subprocess(editor_program, command)
    else:
        print("No editor has been configured in the global settings")
        sp = None
    return sp


def execute_get_results(subprocess_id, timeout=None):
    """
    Get the text results of a previously executed execute call
    Returns a tuple of the strings (stdout, stderr)
    :param subprocess_id: a Popen subprocess ID returned from a previous execute call
    :type subprocess_id:  (subprocess.Popen)
    :param timeout:       Time in fractions of a second to wait. Returns '','' if timeout. Default of None means wait forever
    :type timeout:        (None | float)
    :returns:             Tuple with 2 strings (stdout, stderr)
    :rtype:               (str | None , str | None)
    """

    out_decoded = err_decoded = None
    if subprocess_id is not None:
        try:
            out, err = subprocess_id.communicate(timeout=timeout)
            if out:
                out_decoded = out.decode("utf-8")
            if err:
                err_decoded = err.decode("utf-8")
        except ValueError:
            # will get an error if stdout and stderr are combined and attempt to read stderr
            # so ignore the error that would be generated
            pass
        except subprocess.TimeoutExpired:
            # a Timeout error is not actually an error that needs to be reported
            pass
        except Exception as e:
            popup_error("Error in execute_get_results", e)
    return out_decoded, err_decoded


def execute_subprocess_still_running(subprocess_id):
    """
    Returns True is the subprocess ID provided is for a process that is still running

    :param subprocess_id: ID previously returned from Exec API calls that indicate this value is returned
    :type subprocess_id:  (subprocess.Popen)
    :return:              True if the subproces is running
    :rtype:               bool
    """
    if subprocess_id.poll() == 0:
        return False
    return True


def execute_file_explorer(folder_to_open=""):
    """
    The global settings has a setting called -   "-explorer program-"
    It defines the program to run when this function is called.
    The optional folder paramter specified which path should be opened.

    :param folder_to_open: The path to open in the explorer program
    :type folder_to_open:  str
    :return:               Popen object
    :rtype:                (subprocess.Popen) | None
    """
    pysimplegui_user_settings.load()  # Refresh the settings just in case they've changed via another program
    explorer_program = pysimplegui_user_settings.get("-explorer program-", None)
    if explorer_program is not None:
        sp = execute_command_subprocess(explorer_program, folder_to_open)
    else:
        print("No file explorer has been configured in the global settings")
        sp = None
    return sp


def execute_find_callers_filename():
    """
    Returns the first filename found in a traceback that is not the name of this file (__file__)
    Used internally with the debugger for example.

    :return: filename of the caller, assumed to be the first non PySimpleGUI file
    :rtype:  str
    """
    try:  # lots can go wrong so wrapping the entire thing
        trace_details = traceback.format_stack()
        file_info_pysimplegui, error_message = None, ""
        for line in reversed(trace_details):
            if __file__ not in line:
                file_info_pysimplegui = line.split(",")[0]
                error_message = line
                break
        if file_info_pysimplegui is None:
            return ""
        error_parts = None
        if error_message != "":
            error_parts = error_message.split(", ")
            if len(error_parts) < 4:
                error_message = (
                    error_parts[0]
                    + "\n"
                    + error_parts[1]
                    + "\n"
                    + "".join(error_parts[2:])
                )
        if error_parts is None:
            print("*** Error popup attempted but unable to parse error details ***")
            print(trace_details)
            return ""
        filename = error_parts[0][error_parts[0].index("File ") + 5 :]
        return filename
    except Exception:
        return ""


def _create_full_editor_command(file_to_edit, line_number, edit_format_string):
    """
    The global settings has a setting called -   "-editor format string-"
    It uses 3 "tokens" to describe how to invoke the editor in a way that starts at a specific line #
    <editor> <file> <line>

    :param file_to_edit:
    :type file_to_edit:        str
    :param edit_format_string:
    :type edit_format_string:  str
    :return:
    :rtype:
    """

    command = edit_format_string
    command = command.replace("<editor>", "")
    command = command.replace("<file>", file_to_edit)
    command = command.replace(
        "<line>", str(line_number) if line_number is not None else ""
    )
    return command


def execute_get_editor():
    """
    Get the path to the editor based on user settings or on PySimpleGUI's global settings

    :return: Path to the editor
    :rtype:  str
    """
    try:  # in case running with old version of PySimpleGUI that doesn't have a global PSG settings path
        global_editor = pysimplegui_user_settings.get("-editor program-")
    except Exception:
        global_editor = ""

    return user_settings_get_entry("-editor program-", global_editor)





def _create_error_message():
    """
    Creates an error message containing the filename and line number of the users
    code that made the call into PySimpleGUI
    :return: Error string to display with file, line number, and line of code
    :rtype:  str
    """

    called_func = inspect.stack()[1].function
    trace_details = traceback.format_stack()
    error_message = ""
    file_info_pysimplegui = trace_details[-1].split(",")[0]
    for line in reversed(trace_details):
        if line.split(",")[0] != file_info_pysimplegui:
            error_message = line
            break
    if error_message != "":
        error_parts = error_message.split(", ")
        if len(error_parts) < 4:
            error_message = (
                error_parts[0] + "\n" + error_parts[1] + "\n" + "".join(error_parts[2:])
            )
    return (
        "The PySimpleGUI internal reporting function is "
        + called_func
        + "\n"
        + "The error originated from:\n"
        + error_message
    )




def get_complimentary_hex(color:str):
    """
    :param color: color string, like "#RRGGBB"
    :type color:  (str)
    :return:      color string, like "#RRGGBB"
    :rtype:       (str)
    """

    # strip the # from the beginning
    color = color[1:]
    # convert the string into hex
    color = int(color, 16)
    # invert the three bytes
    # as good as substracting each of RGB component by 255(FF)
    comp_color = 0xFFFFFF ^ color
    # convert the color back to hex by prefixing a #
    comp_color = "#%06X" % comp_color
    return comp_color




# Converts an object's contents into a nice printable string.  Great for dumping debug data
def obj_to_string_single_obj(obj):
    """
    Dumps an Object's values as a formatted string.  Very nicely done. Great way to display an object's member variables in human form
    Returns only the top-most object's variables instead of drilling down to dispolay more
    :param obj: The object to display
    :type obj:  (Any)
    :return:    Formatted output of the object's values
    :rtype:     (str)
    """
    if obj is None:
        return "None"
    return (
        str(obj.__class__)
        + "\n"
        + "\n".join(
            (
                repr(item) + " = " + repr(obj.__dict__[item])
                for item in sorted(obj.__dict__)
            )
        )
    )


def obj_to_string(obj, extra="    "):
    """
    Dumps an Object's values as a formatted string.  Very nicely done. Great way to display an object's member variables in human form
    :param obj:   The object to display
    :type obj:    (Any)
    :param extra: extra stuff (Default value = '    ')
    :type extra:  (str)
    :return:      Formatted output of the object's values
    :rtype:       (str)
    """
    if obj is None:
        return "None"
    return (
        str(obj.__class__)
        + "\n"
        + "\n".join(
            (
                extra
                + (
                    str(item)
                    + " = "
                    + (
                        ObjToString(obj.__dict__[item], extra + "    ")
                        if hasattr(obj.__dict__[item], "__dict__")
                        else str(obj.__dict__[item])
                    )
                )
                for item in sorted(obj.__dict__)
            )
        )
    )




def _simplified_dual_color_to_tuple(color_tuple_or_string, default=(None, None)):
    """
    Convert a color tuple or color string into 2 components and returns them as a tuple
    (Text Color, Button Background Color)
    If None is passed in as the first parameter, theme_

    :param color_tuple_or_string: Button color - tuple or a simplied color string with word "on" between color
    :type  color_tuple_or_string: str | (str, str} | (None, None)
    :param default:               The 2 colors to use if there is a problem. Otherwise defaults to the theme's button color
    :type  default:               (str, str)
    :return:                      (str | (str, str)
    :rtype:                       str | (str, str)
    """
    if color_tuple_or_string is None or color_tuple_or_string == (None, None):
        color_tuple_or_string = default
    if color_tuple_or_string == COLOR_SYSTEM_DEFAULT:
        return COLOR_SYSTEM_DEFAULT, COLOR_SYSTEM_DEFAULT
    text_color = background_color = COLOR_SYSTEM_DEFAULT
    try:
        if isinstance(color_tuple_or_string, (tuple, list)):
            if len(color_tuple_or_string) >= 2:
                text_color = color_tuple_or_string[0] or default[0]
                background_color = color_tuple_or_string[1] or default[1]
            elif len(color_tuple_or_string) == 1:
                background_color = color_tuple_or_string[0] or default[1]
        elif isinstance(color_tuple_or_string, str):
            color_tuple_or_string = color_tuple_or_string.lower()
            split_colors = color_tuple_or_string.split(" on ")
            if len(split_colors) >= 2:
                text_color = split_colors[0].strip() or default[0]
                background_color = split_colors[1].strip() or default[1]
            elif len(split_colors) == 1:
                split_colors = color_tuple_or_string.split("on")
                if len(split_colors) == 1:
                    text_color, background_color = default[0], split_colors[0].strip()
                else:
                    split_colors = split_colors[0].strip(), split_colors[1].strip()
                    text_color = split_colors[0] or default[0]
                    background_color = split_colors[1] or default[1]
                    # text_color, background_color = color_tuple_or_string, default[1]
            else:
                text_color, background_color = default
        else:
            if not SUPPRESS_ERROR_POPUPS:
                _error_popup_with_traceback(
                    "** Badly formatted dual-color... not a tuple nor string **",
                    color_tuple_or_string,
                )
            else:
                print(
                    "** Badly formatted dual-color... not a tuple nor string **",
                    color_tuple_or_string,
                )
            text_color, background_color = default
    except Exception as e:
        if not SUPPRESS_ERROR_POPUPS:
            _error_popup_with_traceback(
                "** Badly formatted button color **", color_tuple_or_string, e
            )
        else:
            print(
                "** Badly formatted button color... not a tuple nor string **",
                color_tuple_or_string,
                e,
            )
        text_color, background_color = default
    if isinstance(text_color, int):
        text_color = "#%06X" % text_color
    if isinstance(background_color, int):
        background_color = "#%06X" % background_color
    # print('converted button color', color_tuple_or_string, 'to', (text_color, background_color))

    return text_color, background_color






def button_color_to_tuple(color_tuple_or_string, default=(None, None)):
    """
    Convert a color tuple or color string into 2 components and returns them as a tuple
    (Text Color, Button Background Color)
    If None is passed in as the first parameter, then the theme's button color is
    returned

    :param color_tuple_or_string: Button color - tuple or a simplied color string with word "on" between color
    :type  color_tuple_or_string: str | (str, str)
    :param default:               The 2 colors to use if there is a problem. Otherwise defaults to the theme's button color
    :type  default:               (str, str)
    :return:                      (str | (str, str)
    :rtype:                       str | (str, str)
    """
    if default == (None, None):
        color_tuple = _simplified_dual_color_to_tuple(
            color_tuple_or_string, default=theme_button_color()
        )
    elif color_tuple_or_string == COLOR_SYSTEM_DEFAULT:
        color_tuple = (COLOR_SYSTEM_DEFAULT, COLOR_SYSTEM_DEFAULT)
    else:
        color_tuple = _simplified_dual_color_to_tuple(
            color_tuple_or_string, default=default
        )

    return color_tuple






def _parse_colors_parm(colors):
    """
    Parse a colors parameter into its separate colors.
    Some functions accept a dual colors string/tuple.
    This function parses the parameter into the component colors

    :param colors: Either a tuple or a string that has both the text and background colors
    :type colors:  (str) or (str, str)
    :return:       tuple with the individual text and background colors
    :rtype:        (str, str)
    """
    if colors is None:
        return None, None
    dual_color = colors
    kw_text_color = kw_background_color = None
    try:
        if isinstance(dual_color, tuple):
            kw_text_color = dual_color[0]
            kw_background_color = dual_color[1]
        elif isinstance(dual_color, str):
            if (
                " on " in dual_color
            ):  # if has "on" in the string, then have both text and background
                kw_text_color = dual_color.split(" on ")[0]
                kw_background_color = dual_color.split(" on ")[1]
            else:  # if no "on" then assume the color string is just the text color
                kw_text_color = dual_color
    except Exception as e:
        print("* warning * you messed up with color formatting", e)

    return kw_text_color, kw_background_color





def convert_args_to_single_string(*args):
    """ """
    (
        max_line_total,
        width_used,
        total_lines,
    ) = 0, 0, 0
    single_line_message = ""
    # loop through args and built a SINGLE string from them
    for message in args:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        longest_line_len = max([len(l) for l in message.split("\n")])
        width_used = max(longest_line_len, width_used)
        max_line_total = max(max_line_total, width_used)
        lines_needed = _GetNumLinesNeeded(message, width_used)
        total_lines += lines_needed
        single_line_message += message + "\n"
    return single_line_message, width_used, total_lines






# ==============================_GetNumLinesNeeded ==#
# Helper function for determining how to wrap text   #
# ===================================================#
def _GetNumLinesNeeded(text, max_line_width:int):
    if max_line_width == 0:
        return 1
    lines = text.split("\n")
    num_lines = len(lines)  # number of original lines of text
    max_line_len = max([len(l) for l in lines])  # longest line
    lines_used = []
    for L in lines:
        lines_used.append(
            len(L) // max_line_width + (len(L) % max_line_width > 0)
        )  # fancy math to round up
    total_lines_needed = sum(lines_used)
    return total_lines_needed

