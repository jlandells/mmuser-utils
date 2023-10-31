# mmuser-utils
A sample utility for managing Mattermost users.  This code is provided as a sample of how you could use Python to 
manage [Mattermost](https://mattermost.com) users.  Such a script could be useful for providing options via a cron job, 
for example.  The functionality could also be combined with other code to develop more comprehensive integrations with
Mattermost.

> [!NOTE]
> This code should not be considered production ready!

A number of options are presented in this sample code:
- Force logout of a user
- Disable/Enable a user
- Change (or remove) a user's nickname
- Add (or remove) a user to a Team
- Add (or remove) a user to a Channel

Each of these options is actionable via command line parameters.  These are split into two sections, covering the 
Site-specific parameters and the Task-specific parameters, as described below, and the utility is called as follows:

```shell
python userutil.py [-h] [--config CONFIG] [<-d | --debug>] 
                   [--siteurl URL] [--port PORT]
                   [--scheme {http,https}] [--tokenfile TOKENFILE] 
                   <-e EMAIL | --useremail EMAIL>
                   [--forcelogout] [--disableuser] [--enableuser]
                   [--newnickname NICKNAME] [--removenickname]
                   [--teamadd TEAM] [--teamremove TEAM]
                   [--channeladd CHANNEL] [--channelremove CHANNEL]
                   [--team TEAM]
```

### Site-Specific Arguments

These represent the Mattermost site connection arguments.  These arguments must either be presented on the command line,
or in a supplied config file.  By default, the config file should be in the same directory as the Python code, and be 
called `config.ini`.

| Argument | Description                                                                                                                                                                    |
| -------- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--siteurl URL` | Mattermost site URL.  Must be present either in the config file or on the command line. Argument overrides config file entry.                                                  |
| `--port PORT` | [Optional] Port on which Mattermost is listening. [Default: 443] Argument overrides config file entry.                                                                         |
| `--scheme {http,https}` | [Optional] The HTTP scheme to be used. [Default: https] Argument overrides config file entry.                                                                                  |
| `--tokenfile TOKENFILE` | A text file containing a valid Mattermost [Personal Access Token](https://docs.mattermost.com/developer/personal-access-tokens.html) from an account with System Admin access. |

### Task-Specific Arguments

These arguments specify the specific actions to perform.  

> [!WARNING]
> The arguments could potentially be combined to accomplish multiple tasks at once, but this should be avoided in 
> practise, as the results may not be as you expect!

| Argument                       | Description                                                                                            |
|--------------------------------|--------------------------------------------------------------------------------------------------------|
| `-e EMAIL`, `--username EMAIL` | Target user's email address.  **Required for all task types!**                                         |
| `--forcelogout`                | Forces a user to be logged out.                                                                        |
| `--disableuser`                | Disable an existing user.                                                                              |
| `--enableuser`                 | Enable a previously disabled user.                                                                     |
| `--newnickname NICKNAME`       | If this argument is present, the supplied user will have their nickname changed to the supplied value. |
| `--removenickname`             | If this argument is present, the specified user will have their nickname cleared.                      |
| `--teamadd TEAM`               | If this argument is present, the supplied user will be added to the specified team.                    |
| `--teamremove TEAM`            | If this argument is present, the supplied user will be removed from the specified team.                |
| `--channeladd CHANNEL`         | If this argument is present, the supplied user will be added to the specified channel.                 |
| `--channelremove CHANNEL`         | If this argument is present, the supplied user will be removed from the specified channel.                |
| `--team TEAM`                 | When using either of the 'channel' functions, a team nanme is required in order to uniquely idenfity the channel. |

### Optional Arguments

| Argument          | Description             |
|-------------------|-------------------------|
| `--config CONFIG` | Path to the config file |
| `-h`, `--help` | Display the help message and exit. |
| `-d`, `--debug` | Run the code in debug mode for additional output for troubleshooting. |


## Further Information

In order to use this code, you'll need to deploy the `mattermostdriver` Python library.  This can usually be done via:

`pip install mattermostdriver`

More information on this library can be found [here](https://pypi.org/project/mattermostdriver/)