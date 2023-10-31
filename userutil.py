import _io
import os
import sys
from mattermostdriver import Driver
import configparser
import argparse


# Constants
DEFAULT_CONFIG_FILE='config.ini'
DEFAULT_PORT = '443'
DEFAULT_SCHEME = 'https'

DEBUG = False


def debug_print(msg: str) -> None:
    """
    This function is used to print debug information to stdout, if the global variable DEBUG
    is set to True.

    :param msg: Debug message to be printed
    :return: None
    """

    if DEBUG:
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


def is_valid_file(parser: argparse.ArgumentParser, arg: argparse.Namespace) -> _io.TextIOWrapper:
    if not os.path.exists(arg):
        parser.error("The file {} does not exist!".format(arg))
    else:
        return open(arg, 'r')  # return an open file handle


def load_site_config(config_file: str) -> dict:
    """
    Load the default configuration from file.  This supplies us with a set of defaults that can be reused
    so that we don't have to pass them as command line parameters every time.

    :param config_file: The path to the config file to be used
    :return: Dictionary of the INI file entries in the 'Site' section
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return dict(config['Site'])


def setup_parser(defaults: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage user tasks.")
    site_args = parser.add_argument_group('Site', 'Mattermost site connection arguments')
    task_args = parser.add_argument_group('Task', 'Task specific arguments')

    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG_FILE, help="Path to the config file")
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', help="Execute the code in DEBUG mode.")

    # Site override arguments
    site_args.add_argument(
        '--siteurl',
        type=str,
        default=defaults.get('siteurl'),
        metavar="URL",
        help='Mattermost site URL.  Must be present either in config file or on command line.'
    )
    site_args.add_argument(
        '--port',
        type=str,
        default=defaults.get('port', DEFAULT_PORT),
        help=f"Port on which Mattermost is running [Default: {DEFAULT_PORT}]. Argument overrides config file entry."
    )
    site_args.add_argument(
        '--scheme',
        type=str,
        default=defaults.get('scheme', DEFAULT_SCHEME),
        help=f"The HTTP scheme to be used [Default: {DEFAULT_SCHEME}]. Argument overrides config file entry.",
        choices=['http', 'https']
    )
    site_args.add_argument(
        '--tokenfile',
        type=lambda x: is_valid_file(parser, x),
        default=defaults.get('tokenfile'),
        help="Required - default from config file.  A text file containing a valid Mattermost Personal Access token from an account with System Admin access."
    )

    # User task arguments
    task_args.add_argument(
        '-e', '--useremail',
        type=str,
        required=True,
        metavar="EMAIL",
        help="User email address.  Required for all task types."
    )
    task_args.add_argument(
        '--forcelogout',
        action='store_true',
        help="Force a user to be logged out."
    )
    task_args.add_argument(
        '--disableuser',
        action='store_true',
        help="Disable an existing user."
    )
    task_args.add_argument(
        '--enableuser',
        action='store_true',
        help="Enable an existing user."
    )
    task_args.add_argument(
        '--newnickname',
        type=str,
        metavar="NICKNAME",
        help="If this argument is present, the supplied user will have their nickname changed to the supplied value."
    )
    task_args.add_argument(
        '--removenickname',
        action='store_true',
        help="If this argument is present, the supplied user will have their nickname cleared."
    )
    task_args.add_argument(
        '--teamadd',
        type=str,
        metavar="TEAM",
        help="If this argument is present, the supplied user will be added to the specified team."
    )
    task_args.add_argument(
        '--teamremove',
        type=str,
        metavar="TEAM",
        help="If this argument is present, the supplied user will be removed from the specified team."
    )
    task_args.add_argument(
        '--channeladd',
        type=str,
        metavar="CHANNEL",
        help="If this argument is present, the supplied user will be added to the specified channel.  Requires a team name."
    )
    task_args.add_argument(
        '--channelremove',
        type=str,
        metavar="CHANNEL",
        help="If this argument is present, the supplied user will be removed from the specified channel.  Requires a team name."
    )
    task_args.add_argument(
        '--team',
        type=str,
        help="This parameter is required when requesting one of the channel operations."
    )

    return parser


def validate_args(args: argparse.Namespace):
    debug_print(f"Using Mattermost instance at {args.scheme}://{args.siteurl}:{args.port}")
    if not args.siteurl or not args.port or not args.scheme or not args.tokenfile:
        print_error("Site URL, port, HTTP scheme and token file are all required parameter!")
        exit(1)

    if args.forcelogout or \
            args.disableuser or \
            args.newnickname or \
            args.enableuser or \
            args.newnickname or \
            args.removenickname or \
            args.teamadd or \
            args.teamremove or \
            args.channeladd or \
            args.channelremove:
        # These options all require a user email
        if not args.useremail:
            print_error("User email required!")
            exit(2)

    if args.channeladd or args.channelremove:
        # These arguments also require a Team name
        if not args.team:
            print_error("A team name is required when performing channel operations!")
            exit(3)

    return


def force_user_logout(mm: Driver, email: str) -> bool:
    """
    Forces the logout of a user, given their email address.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :return: True (success) / False (failure)
    """

    print_info(f"Logging out user: {email}")

    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    response = mm.users.revoke_all_user_sessions(user_id)

    debug_print(response)

    if not response['status']=='OK':
        print_warn(f"Failed to logout user: {email}")
        return False

    print_info(f"User '{email}' logged out!")

    return True


def disable_user(mm: Driver, email: str, revert=False) -> bool:
    """
    Disables a Mattermost user, given their email address.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param revert: Optional flag to re-enable the user
    :return: True (success) / False (failure)
    """

    payload = {}
    if revert:
        print_info(f"Re-enabling user: {email}")
        payload['active'] = True
    else:
        print_info(f"Disabling user: {email}")
        payload['active'] = False

    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    response = mm.users.update_user_active_status(user_id, options=payload)

    debug_print(response)

    if not response['status'] == 'OK':
        print_warn(f"Failed to update user: {email}")
        return False

    print_info(f"User '{email}' updated successfully!")

    return True


def new_nickname(mm: Driver, email: str, newnickname: str) -> bool:
    """
    Forces the logout of a user, given their email address.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param newnickname: The nickname that should be set for the supplied user
    :return: True (success) / False (failure)
    """

    print_info(f"Setting new nickname for user: {email} to '{newnickname}'")

    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    response = mm.users.patch_user(user_id, options={"nickname": f"{newnickname}"})

    debug_print(response)

    if not response['nickname'] == newnickname:
        print_warn(f"Failed to set nickname for user: {email}")
        return False

    print_info(f"User '{email}' nickname updated to '{newnickname}'!")

    return True


def remove_nickname(mm: Driver, email: str) -> bool:
    """
    Forces the logout of a user, given their email address.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :return: True (success) / False (failure)
    """

    print_info(f"Clearing nickname for user: {email}")

    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    response = mm.users.patch_user(user_id, options={"nickname": ""})

    debug_print(response)

    if not response['nickname'] == "":
        print_warn(f"Failed to clear nickname for user: {email}")
        return False

    print_info(f"User '{email}' nickname cleared!")

    return True


def add_user_to_team(mm: Driver, email: str, teamname: str) -> bool:
    """
    Adds a user to a specified team.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param teamname: The name of the Mattermost team to which the user should be added
    :return: True (success) / False (failure)
    """
    print_info(f"Adding user '{email}' to team '{teamname}'")

    # To start with, we need the ID of the user
    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    # Now we need the ID of the Team
    team = mm.teams.get_team_by_name(teamname)

    if not team:
        print_warn(f"Unable to get ID of team: '{teamname}")
        return False

    team_id = team['id']

    debug_print(f"User ID: {user_id} -- Team ID: {team_id}")

    payload = {
        "team_id": team_id,
        "user_id": user_id
    }

    response = mm.teams.add_user_to_team(team_id, options=payload)

    debug_print(response)

    # Only a successful response will contain a "team_id" value in the response
    if not response['team_id']:
        print_warn("Failed to add user to team!")
        return False

    print_info(f"User '{email}' added to team '{teamname}'!")

    return True


def remove_user_from_team(mm: Driver, email: str, teamname: str) -> bool:
    """
    Removes a user from a specified team.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param teamname: The name of the Mattermost team from which the user should be removed
    :return: True (success) / False (failure)
    """
    print_info(f"Removing user '{email}' from team '{teamname}'")

    # To start with, we need the ID of the user
    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    # Now we need the ID of the Team
    team = mm.teams.get_team_by_name(teamname)

    if not team:
        print_warn(f"Unable to get ID of team: '{teamname}")
        return False

    team_id = team['id']

    debug_print(f"User ID: {user_id} -- Team ID: {team_id}")

    payload = {
        "team_id": team_id,
        "user_id": user_id
    }

    response = mm.teams.remove_user_from_team(team_id, user_id)

    debug_print(response)

    # Only a successful response will contain a "status" value in the response
    if not response['status']:
        print_warn("Failed to remove user from team!")
        return False

    print_info(f"User '{email}' removed from team '{teamname}'!")

    return True


def parse_channel_name(channelname:str) -> str:
    """
    Takes a human readable and converts it to a form that can be passed to URLs.
    All characters are converted to lower case, and spaces are replaced with dashes '-'.

    :param channelname: The human readable string format of the channel name.
    :return: String - Converted channel name
    """

    debug_print(f"Converting channel: '{channelname}'")

    lowercase_channelname = channelname.lower()
    converted_channelname = lowercase_channelname.replace(' ', '-')

    return converted_channelname

def add_user_to_channel(mm: Driver, email: str, channelname: str, teamname: str) -> bool:
    """
    Adds a user to a specified channel.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param channelname: The name of the Mattermost Channel to which the user should be added
    :param teamname: The name of the Mattermost Team in which the Channel is located
    :return: True (success) / False (failure)
    """
    print_info(f"Adding user '{email}' to channel '{channelname}' in team '{teamname}")

    # To start with, we need the ID of the user
    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    # Now we need the Channel ID
    channel = mm.channels.get_channel_by_name_and_team_name(teamname, parse_channel_name(channelname))

    if not channel:
        print_warn("Unable to retrieve channel!")
        return False

    channel_id = channel['id']

    payload = {"user_id": user_id}

    response = mm.channels.add_user(channel_id, options=payload)

    if response.get("status_code"):
        # There will only be a 'status_code' element if the call fails
        print_error(f"Failed to add user {email} to channel: {channelname}")
        return False

    return True


def remove_user_from_channel(mm: Driver, email: str, channelname: str, teamname: str) -> bool:
    """
    Removes a user from a specified team.

    :param mm: The Mattermost Driver object that defines the connection
    :param email: Email address of the user.
    :param channelname: The name of the Mattermost Channel from which the user should be removed
    :param teamname: The name of the Mattermost Team in which the Channel is located
    :return: True (success) / False (failure)
    """
    print_info(f"Removing user '{email}' from team '{teamname}'")

    # To start with, we need the ID of the user
    user = mm.users.get_user_by_email(email)

    if not user:
        print_warn(f"User '{email}' not found!")
        return False

    user_id = user['id']

    # Now we need the Channel ID
    channel = mm.channels.get_channel_by_name_and_team_name(teamname, parse_channel_name(channelname))

    if not channel:
        print_warn("Unable to retrieve channel!")
        return False

    channel_id = channel['id']

    response = mm.channels.remove_channel_member(channel_id, user_id)

    if response.get("status_code"):
        # There will only be a 'status_code' element if the call fails
        print_error(f"Failed to remove user {email} from channel: {channelname}")
        return False

    return True


def main():
    initial_defaults = load_site_config(DEFAULT_CONFIG_FILE)

    parser = setup_parser(initial_defaults)
    args = parser.parse_args()
    if args.debug:
        global DEBUG
        DEBUG = True
        print_info("Running in DEBUG mode, per command line parameter")

    if args.config:
        debug_print(f"Found updated config: {args.config}")
        new_defaults = load_site_config(args.config)

        # Update parser
        parser = setup_parser(new_defaults)
        args = parser.parse_args()

    validate_args(args)

    userToken = args.tokenfile.readline().strip()

    debug_print(f"User token: {userToken}")

    mm = Driver({'url': args.siteurl,
                 'port': int(args.port),
                 'token': userToken,
                 'scheme': args.scheme,
                 'debug': DEBUG,
                 })

    mm.login()

    if args.forcelogout:
        if not force_user_logout(mm, args.useremail):
            print_warn(f"Failed to logout user: {args.useremail}")

    if args.disableuser:
        if not disable_user(mm, args.useremail):
            print_warn(f"Failed to disable user: {args.useremail}")

    if args.enableuser:
        if not disable_user(mm, args.useremail, revert=True):
            print_warn(f"Failed to enable user: {args.useremail}")

    if args.newnickname:
        if not new_nickname(mm, args.useremail, args.newnickname):
            print_warn(f"Failed to rename user: {args.useremail}")

    if args.removenickname:
        if not remove_nickname(mm, args.useremail):
            print_warn(f"Failed to remove nickname for user: {args.useremail}")

    if args.teamadd:
        if not add_user_to_team(mm, args.useremail, args.teamadd):
            print_warn(f"Failed to add user '{args.useremail}' to team '{args.teamadd}'")

    if args.teamremove:
        if not remove_user_from_team(mm, args.useremail, args.teamremove):
            print_warn(f"Failed to remove user '{args.useremail}' from team '{args.teamremove}'")

    if args.channeladd:
        if not add_user_to_channel(mm, args.useremail, args.channeladd, args.team):
            print_warn("Failed to add user to channel")

    if args.channelremove:
        if not remove_user_from_channel(mm, args.useremail, args.channelremove, args.team):
            print_warn("Failed to remove user from channel")

    return


if __name__ == '__main__':
    main()
