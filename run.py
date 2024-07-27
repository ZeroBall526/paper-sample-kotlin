# Server Setting #

# Server directory name
DIR = ".Server"

# Please input the server download link api url
API_URL = "https://qing762.is-a.dev/api/papermc"

# Server version type (if you type 'latest' script will download the latest version in api)
SERVER_VERSION = "latest"

# Setting the server memory (GB)
RAM = "4"

# paper or spigot setting #

# Setting the maximum number of players
MAX_PLAYER = "20"

# Setting the server port
PORT = "25565"

# Setting use jdwp port, enable debug mode (if setting True, jdwp port will be open 5005)
USE_DEBUG_PORT = False

# Setting use command block
ENABLE_COMMAND_BLOCK = True

# Preinstallation plugins (url)
DEFAULT_PLUGINS = [
    # AutoReloader
    'https://github.com/monun/auto-reloader/releases/download/0.0.6/auto-reloader-0.0.6.jar',
    # WorldEdit
    'https://cdn.modrinth.com/data/1u6JkXh5/versions/vMrPkmgF/worldedit-bukkit-7.3.4.jar'
]

# Setting use whitelist
WHITELIST = True

# End of configuration #
# Setup code

import requests
import os
import json
import subprocess


class deploy:
    def __init__(self, DIR='.Server', API_URL='', SERVER_VERSION='latest', RAM=4, MAX_PLAYER=20, PORT=25565,
                 USE_DEBUG_PORT=False, ENABLE_COMMAND_BLOCK=False, DEFAULT_PLUGINS=None, WHITELIST=False):
        if DEFAULT_PLUGINS is None:
            DEFAULT_PLUGINS = []

        self.DIR = DIR
        self.API_URL = API_URL
        self.SERVER_VERSION = SERVER_VERSION
        self.RAM = int(RAM)
        self.MAX_PLAYER = MAX_PLAYER
        self.PORT = PORT
        self.USE_DEBUG_PORT = USE_DEBUG_PORT
        self.ENABLE_COMMAND_BLOCK = ENABLE_COMMAND_BLOCK
        self.DEFAULT_PLUGINS = DEFAULT_PLUGINS
        self.WHITELIST = WHITELIST

    def question(self, q):
        msg = input(q)

        if msg == "y" or msg == "yes":
            return True
        elif msg == "n" or msg == "no":
            return False
        else:
            print("wrong request! please try again.")
            return self.question(q)

    def install(self):
        print("Server file is making... please wait...")
        # make server dir
        if not os.path.exists(DIR):
            os.mkdir(DIR)

        # register server dir on properties
        with open('gradle.properties', 'r+') as file:
            lines = file.readlines()
            new_lines = []
            for line in lines:
                if line.startswith('server_dir'):
                    new_lines.append(f'server_dir={self.DIR}')
                else:
                    new_lines.append(line)
        with open('gradle.properties', 'w+') as file:
            file.writelines(new_lines)

        # make run script
        print("Making run script...")
        for server in [f'{self.DIR}/run.bat', f'{self.DIR}/run.sh']:
            runscript = open(server, 'w+')
            if self.USE_DEBUG_PORT is True:
                runscript.write(
                    f"java -Xmx{self.RAM * 1024}m -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar server.jar -nogui")
            else:
                runscript.write(f"java -Xmx{self.RAM * 1024}m -jar server.jar -nogui")
            runscript.close()

        # make eula.txt
        eula = open(f"{self.DIR}/eula.txt", "w+")
        eula.write("eula = true")

        # download server jar file
        print("Downloading server core...")
        try:
            rqdata = requests.get(self.API_URL).json()

            if self.SERVER_VERSION == "latest":
                self.SERVER_VERSION = rqdata["latest"]

            link = rqdata["versions"][self.SERVER_VERSION]
            serverfile = requests.get(link, timeout=30)

            with open(f'{self.DIR}/server.jar', 'wb') as file:
                file.write(serverfile.content)
                file.close()
        except Exception or ModuleNotFoundError:
            raise Exception('error occurred during download bukkit file!')

        # make server.properties
        print("Making server.properties...")
        debug = "false"
        cmd = "false"
        wlist = "false"
        if self.USE_DEBUG_PORT is True:
            debug = "true"
        if self.ENABLE_COMMAND_BLOCK is True:
            cmd = "true"
        if self.WHITELIST is True:
            wlist = "true"

        properties = open(f'{self.DIR}/server.properties', 'w+')

        write = ["#Minecraft server properties",
                 f"debug={debug}",
                 f"enable-command-block={cmd}",
                 f"hide-online-players=true",
                 f"max-players={self.MAX_PLAYER}",
                 f"server-port={self.PORT}",
                 f"white-list={wlist}"]

        for w in write:
            properties.write(w + "\n")
        properties.close()

        self.preinstallation()

        # if whitelist is turn on make whitelist file
        if self.WHITELIST is True:
            self.whitelist()

    def preinstallation(self):
        # install default plugins
        print("Downloading preinstallation plugins...")
        if not os.path.exists(f"{DIR}/plugins"):
            os.mkdir(f"{DIR}/plugins")

        try:
            for plugin in self.DEFAULT_PLUGINS:
                pluginfile = requests.get(plugin, timeout=30)
                filename = plugin.split("/")[-1]

                with open(f'{DIR}/plugins/{filename}', "wb") as file:
                    file.write(pluginfile.content)
        except Exception or ModuleNotFoundError:
            raise Exception("error occurred while download plugin!")

    def run(self):
        # run the server shell file
        print("Starting up server...")
        import platform

        host_os = platform.system()
        if host_os == "Windows":
            shell_path = os.path.abspath(f'{DIR}/run.bat')
        else:
            shell_path = os.path.abspath(f'{DIR}/run.sh')
        print(f"Run environment : {host_os}")
        process = subprocess.Popen(shell_path, shell=True, cwd=f'{DIR}/')
        process.wait()

    def whitelist(self):
        # check whitelist.json file exist

        if os.path.isfile(f'{DIR}/whitelist.json'):
            question = self.question(f"whitelist.json is exists do you want rewriting file? (y/n) \n=>")

            if question is True:
                os.remove(f'{DIR}/whitelist.json')
            if question is False:
                print('\033[31m' + "Setup canceled")
                return

        players = []
        while True:
            def add_list_on_player(players_list):
                print("making whitelist file...")
                json_list = []

                try:
                    for i in players_list:
                        username = i
                        url = f'https://api.mojang.com/users/profiles/minecraft/{username}?'
                        response = requests.get(url)
                        uuid = response.json()['id']

                        uuid = uuid[0:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20] + "-" + uuid[20:]
                        json_list.append({"name": f"{i}", "uuid": f"{uuid}"})
                except Exception as e:
                    print(e)
                    print(
                        '\033[31m' + "error occurred while getting user info! Please check player name or server status")
                    print('\033[31m' + 'Fail to make whitelist file')
                    return

                with open(f'{DIR}/whitelist.json', 'w') as file:
                    json.dump(json_list, file, sort_keys=True, indent=4)

            player = input(
                "if you want add player on whitelist, please type player name (you don't need to add player on whitelist, type enter) \n=>")

            if not player == "":
                players.append(player)
                print(f"Current players list: {players}")
                question = self.question(f"do you want add more players? (y/n) \n=>")

                if question is False:
                    add_list_on_player(players)
                    break
            elif players is not []:
                add_list_on_player(players)
                break
            else:
                break

    #copy built plugin file
    def copy_build_file(self):
        import shutil

        print("Copying built jar file..")

        if os.path.exists("build/libs") and os.path.exists(f"{DIR}/plugins"):
            file_list = [file for file in os.listdir("build/libs") if file.endswith(".jar")]
            print(f"Found jar file list : {file_list}")

            if len(file_list) > 1:
                print("\nFound multiple jar file, Select which you want copy file")
                for num, file in enumerate(file_list):
                    print(f"{num}. {file}")
                print("Enter. SKIP")

                while True:
                    choice = input("\nSelect number \n> ")

                    if choice != "":
                        try:
                            select = file_list[int(choice)]

                            shutil.copy(f'build/libs/{select}', f'{DIR}/plugins/{select}')
                            break
                        except Exception:
                            print("Error occurred while processing.")
                            print("Please check selected number or file & folder(e.g.dir name) status")

                    else:
                        print('\033[33m' + "Process Canceled")
                        break
            elif len(file_list) == 1:
                shutil.copy(f'build/libs/{file_list[0]}', f'{DIR}/plugins/{file_list[0]}')
            else:
                print('\033[33m' + "Can't find built jar file! SKIPPED...")
        else:
            print('\033[33m' + "Can't find tasking directory! SKIPPED...")
        print('\033[0m', end='')


# DEBUG MODE
SCRIPT_MODE = "custom"

INSTALL_AFTER_RUN = True

# check build/libs/ jar file and copy it
COPY_BUILD_PLUGIN = True

i = deploy(DIR, API_URL, SERVER_VERSION, RAM, MAX_PLAYER, PORT, USE_DEBUG_PORT, ENABLE_COMMAND_BLOCK, DEFAULT_PLUGINS,
           WHITELIST)

# TODO : make status file & check status file
if SCRIPT_MODE == "normal":
    if os.path.exists(DIR) and os.path.exists(f'{DIR}/run.bat'):
        SCRIPT_MODE = "run"
    else:
        SCRIPT_MODE = "install"

if SCRIPT_MODE == "install":
    i.install()
    if COPY_BUILD_PLUGIN is True:
        i.copy_build_file()
    if INSTALL_AFTER_RUN is True:
        i.run()
elif SCRIPT_MODE == "run":
    i.run()
elif SCRIPT_MODE == "whitelist":
    i.whitelist()
elif SCRIPT_MODE == "custom":
    i.copy_build_file()
    # type want specific function
    pass
else:
    raise Exception("Script mode select error! Please check debug option")
