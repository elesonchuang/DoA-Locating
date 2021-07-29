from subprocess import Popen, PIPE # Used to run native OS commads in python wrapped subproccess
def get_Signal(interface, freq, name):
    scan_command = ['sudo','iw','dev',interface,'scan','freq',freq]
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = str(raw_output)
    name = name + '\n'
    for i in range(len(raw_output.split('signal:'))-1):
        ssid = raw_output.split('SSID:')[i+1]
        ssid = ssid.split(' ')[1]
        if ssid.startswith(name):
            signal = raw_output.split('signal:')[i+1]
            signal = float(signal.split(' ')[1])
            return signal
#print(raw_output, raw_error)
