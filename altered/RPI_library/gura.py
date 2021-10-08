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

def get_Channel(interface, name):
    scan_command = ['sudo','iw','dev',interface,'scan','ssid',name]
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = raw_output.decode() 
    data = raw_output.split('\n')
    #print('raw_output', type(raw_output), raw_output) 
    for i in range(len(raw_output.split('\n'))):
        if data[i].endswith(name):
            # print(data)
            for m in range(8):
                if data[i-m].startswith('freq',1):
                    return (data[i-m].split())[-1]
    return 0

def get_interface(station):
    scan_command = ['sudo','iw','dev']
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = raw_output.decode() 
    data = raw_output.split('\n')
    interface ={} #create return dictionary
    macs = ['75:81','32:6d','37:73','79:c0','35:98','31:9b']
    # index 0,1 --> Rpi0    index 2,3 --> Rpi1  index 4,5 --> Rpi2
    # print('raw_output', type(raw_output), raw_output) 
    for i in range(len(raw_output.split('\n'))):
        if data[i].endswith('addr', 0,-18):
            if (data[i].endswith(macs[2*station])):
                interface['sum'] = (data[i-3].split())[-1]
            elif (data[i].endswith(macs[2*station+1])):
                interface['difference'] = (data[i-3].split())[-1]
    return interface
