from subprocess import Popen, PIPE # Used to run native OS commads in python wrapped subproccess
def get_interface(station):
    scan_command = ['sudo','iw','dev']
    scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
    (raw_output, raw_error) = scan_process.communicate()
    scan_process.wait()
    raw_output = raw_output.decode() 
    data = raw_output.split('\n')
    interface ={} #create return dictionary
    macs = ['35:98','31:9b','75:81','32:6d','37:73','73:57']
    # index 0,1 --> Rpi0    index 2,3 --> Rpi1  index 4,5 --> Rpi2
    # print('raw_output', type(raw_output), raw_output) 
    for i in range(len(raw_output.split('\n'))):
        if data[i].endswith('addr', 0,-18):
            if (data[i].endswith(macs[2*station])):
                interface['sum'] = (data[i-3].split())[-1]
            elif (data[i].endswith(macs[2*station+1])):
                interface['difference'] = (data[i-3].split())[-1]
    return interface