#!/usr/bin/env python2
import os
import subprocess
import signal
import time
import sys
import socket
node1addr = '172.16.133.10'
node2addr = '172.16.134.10'
node1pass = 'test1q'
node2pass = 'test1q'
portmon = '3389'
servicename = 'haproxy'
node1 = "sshpass -p " + node1pass + " ssh root@" + node1addr + " service " + servicename + " status |grep Active | awk '{print $2}'"
node2 = "sshpass -p " + node2pass + " ssh root@" + node2addr + " service " + servicename + " status |grep Active | awk '{print $2}'"
start1 = "sshpass -p " + node1pass + " ssh root@" + node1addr + " 'service " + servicename + " start'"
stop1 = "sshpass -p " + node1pass + " ssh root@" + node1addr + " 'service " + servicename + " stop'"
start2 = "sshpass -p " + node2pass + " ssh root@" + node2addr + " 'service " + servicename + " start'"
stop2 = "sshpass -p " + node2pass + " ssh root@" + node2addr + " 'service " + servicename + " stop'"
def test_request(arg=None):
    time.sleep(2)
    return arg
class Timeout():
    class Timeout(Exception):
        pass
    def __init__(self, sec):
         self.sec = sec

    def __enter__(self):
         signal.signal(signal.SIGALRM, self.raise_timeout)
         signal.alarm(self.sec)
    def __exit__(self, *args):
        signal.alarm(0)
    def raise_timeout(self, *args):
        raise Timeout.Timeout()
def ssh():
    a = 0
    b = 0
    sys.stderr.write("test connections\n")
    try :
        with Timeout(5):
             proc = subprocess.Popen(node1, stdout=subprocess.PIPE, shell=True)
             (out_1, err) = proc.communicate()
             if out_1 == "active"'\n':
                 ssh.out1 = 1
             else:
                 ssh.out1 = 0
             ssh.a = 1
    except Timeout.Timeout:
         ssh.a = 0
         sys.stderr.write("cannot connect to hosts1\n")
    try :
        with Timeout(5):
            proc = subprocess.Popen(node2, stdout=subprocess.PIPE, shell=True)
            (out_2, err) = proc.communicate()
            ssh.b = 1
            if out_2 == "active"'\n':
                ssh.out2 = 1
            else:
                ssh.out2 = 0
    except Timeout.Timeout:
        ssh.b = 0
        sys.stderr.write("cannot connect to host2\n")
def ctrl():
    if (ssh.a==1 and ssh.b==1) :
        ctrl.x = 0
        if int(ssh.out1) > 0 :
            sys.stderr.write("node1 " + servicename + " running\n")
            ctrl.x = 1
            if int(ssh.out2) > 0 :
                ctrl.x = 2
                sys.stderr.write("all " + servicename + " running\n")
        elif int(ssh.out2) > 0 :
            ctrl.x = 3
            sys.stderr.write("node2 " + servicename + " running\n")
        else :
            sys.stderr.write("" + servicename + " not running\n")
            ctrl.x = 4
    elif (ssh.a==0 and ssh.b==0) :
        sys.stderr.write("cannot check state\n")
    elif ssh.a==0 :
        if int(ssh.out2) > 0 :
            ctrl.x = 5
            sys.stderr.write("node2 " + servicename + " running\n")
        else:
            os.system(start2)
            ctrl.x = 6
            sys.stderr.write("start " + servicename + " on node1\n")
    elif ssh.b==0 :
        if int(ssh.out1) > 0 :
            ctrl.x = 7
            sys.stderr.write("node1 " + servicename + " running\n")
        else:
            ctrl.x = 8
            os.system(start1)
            sys.stderr.write("start " + servicename + " on node2\n")
    else:
        ctrl.x = 9
        sys.stderr.write("cannot check state\n")
def stopstart():
    if ctrl.x == 2 :
        proc = subprocess.Popen(stop2, shell=True)
        proc.communicate()
        sys.stderr.write("stop " + servicename + " on node1\n")
    elif ctrl.x == 4 :
        proc = subprocess.Popen(start2, shell=True)
        proc.communicate()
        sys.stderr.write("start " + servicename + " on node2\n")
    else:
        sys.stderr.write("system online\n")
def sockets():
    sockets.node1 = 0
    sockets.node2 = 0
    s = socket.socket()
    try:
        s.connect((node1addr, portmon))
        sockets.node1 = 1
    except Exception as e:
        sockets.node1 = 0
    try:
        s.connect((node2addr, portmon))
        sockets.node2 = 1
    except Exception as e:
        sockets.node2 = 0
    finally:
        s.close()
if __name__ == '__main__':
    while True:
        sockets()
        if sockets.node1 == 1 :
            if sockets.node2 == 1:
                ssh()
                ctrl()
                stopstart()
            else:
                ssh()
                if ssh.out1 == 1 :
                    sys.stderr.write("System online\n")
                else :
                    ssh()
                    ctrl()
                    stopstart()
        elif sockets.node2 == 1 :
            ssh()
            if ssh.out2 == 1:
                sys.stderr.write("System online\n")
            else:
                ssh()
                ctrl()
                stopstart()
        else :
            ssh()
            ctrl()
            stopstart()
        time.sleep(60)
