from subprocess import Popen, PIPE # Used to run native OS commads in python wrapped subproccess
def get_Signal(interface, freq, name):
    scan_command = ['sudo','iw','dev',interface,'scan','freq',freq,'ssid',name]
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = raw_output.decode() 
    data = raw_output.split('\n')
    info ={} #create return dictionary
    #print('raw_output', type(raw_output), raw_output) 
    for i in range(len(raw_output.split('\n'))):
        if data[i].endswith(name):
            for m in range(-5,5):
                if data[i-m].endswith('channel', 0,-2):
                    info['channel'] = (data[i-m].split())[-1]
                elif data[i-m].endswith('ago'):
                    info['interval'] = (data[i-m].split())[-3]    
                elif data[i-m].endswith('dBm'):
                    info['signal'] = (data[i-m].split())[1]
            return info
    return len(raw_output.split('\n'))
