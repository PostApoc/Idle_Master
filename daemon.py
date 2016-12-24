import atexit
import subprocess

global procList
procList = []

def daemon():
    import sys
    import time
    import logging
    import utils
    from colorama import init, Fore, Back, Style

    #TODO: Close all processes when pressing Ctrl-C

    logging.basicConfig(filename="daemon.log",filemode="w",format="[ %(asctime)s ] %(message)s", datefmt="%Y/%m/%d %I:%M:%S %p",level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(logging.Formatter("[ %(asctime)s ] %(message)s", "%m/%d/%Y %I:%M:%S %p"))
    logging.getLogger('').addHandler(console)

    #TODO: Move bash* variables to settings.txt
    #TODO: Use python to generate cookie login information

    bashSteam = (["exagear",  "debian-8",  "--", "/bin/bash",  "-c", "/usr/games/steam -silent"])
    bashIdleMaster = (["exagear", "debian-8", "--", "/bin/bash", "-c", "python /home/carl/idle_master/start.py"])

    logging.warning("Running Idle Master daemon")

    int_delay = 600

    while True:
        try:
            logging.warning("Checking if daemon needs to run Idle Master")
            int_gamesLeft = utils.gamesLeft()
            logging.warning("Steam games with cards remaining: " + str(int_gamesLeft))
            bool_inGame = utils.inGame()
            logging.warning("Steam user online playing: " + str(bool_inGame))
        except:
            logging.fatal("Error when checking Steam. Exiting")
            sys.exit()

        if(int_gamesLeft > 0 and bool_inGame == False):

            #TODO: Check if Steam is already running

            logging.warning("Daemon is starting Steam")

            for line in run_command(bashSteam):
                logging.info(line)
                if("STEAM_RUNTIME has been set by the user to: " in line):
                    logging.warning("Steam is done starting. Running Idle Master")
                    proc_IdleMaster = subprocess.Popen(bashIdleMaster)
                    procList.append(proc_IdleMaster)
                    logging.warning("Waiting for Idle Master to finish")
                    proc_IdleMaster.wait()
                    logging.warning("Idle Master is finished")
            try:
                logging.warning("Trying to close all started processes")
                terminate_subprocesses()
            except:
                logging.fatal("Error when terminating processeses. Exiting")
                sys.exit()

        logging.warning("Next check in " + str(int_delay / 60) + " minutes")
        time.sleep(int_delay)

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    procList.append(p)
    return iter(p.stdout.readline, b'')

def terminate_subprocesses():
    for proc in procList:
        try:
            proc.terminate()
        except:
            continue

@atexit.register
def kill_subprocesses():
    for proc in procList:
        try:
            proc.kill()
        except:
            logging.warning("Could not kill process " + proc)
            continue

if __name__ == '__main__':

    # executed as a script
    daemon()