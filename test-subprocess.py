import subprocess
import atexit

global procList
procList = []

def run_command(command):
    import subprocess
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    procList.append(p)
    return iter(p.stdout.readline, b'')

def start():

    bashSteam = (["slump.exe"])
    bashIdleMaster = (["python", "utils.py"])
    bashTest = (["python", "test.py"])

    while True:
        for line in run_command(bashTest):
            print(line)
        
        proc_IdleMaster = subprocess.Popen(bashIdleMaster)
        procList.append(proc_IdleMaster)
        proc_IdleMaster.wait()
        kill_subprocesses()

@atexit.register
def kill_subprocesses():
    for proc in procList:
        try:
            proc.kill()
        except:
            continue

if __name__ == '__main__':

    # executed as a script
    start()