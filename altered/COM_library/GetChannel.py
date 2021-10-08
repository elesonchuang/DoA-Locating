from subprocess import Popen, PIPE # Used to run native OS commads in python wrapped subproccess
def get_Channel(interface, name):
    scan_command = ['sudo','iw','dev',interface,'scan','ssid',name]
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = raw_output.decode() 
    data = raw_output.split('\n')
    print('raw_output', type(raw_output), raw_output) 
    for i in range(len(raw_output.split('\n'))):
        if data[i].endswith(name):
            # print(data)
            for m in range(8):
                if data[i-m].startswith('freq',1):
                    return (data[i-m].split())[-1]
    return 0

