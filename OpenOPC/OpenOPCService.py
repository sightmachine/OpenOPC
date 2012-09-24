###########################################################################
#
# OpenOPC Gateway Service
#
# A Windows service providing remote access to the OpenOPC library.
#
# Copyright (c) 2007-2012 Barry Barnreiter (barry_b@users.sourceforge.net)
#
###########################################################################

import win32serviceutil
import win32service
import win32event
import servicemanager
import winerror
import _winreg
import select
import socket
import os
import time
import OpenOPC

try:
    import Pyro.core
    import Pyro.protocol
except ImportError:
    print 'Pyro module required (http://pyro.sourceforge.net/)'
    exit()

Pyro.config.PYRO_MULTITHREADED = 1

opc_class = OpenOPC.OPC_CLASS
opc_gate_host = ''
opc_gate_port = 7766

def getvar(env_var):
    """Read system enviornment variable from registry"""
    try:
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\Session Manager\Environment',0,_winreg.KEY_READ)
        value, valuetype = _winreg.QueryValueEx(key, env_var)
        return value
    except:
        return None

# Get env vars directly from the Registry since a reboot is normally required
# for the Local System account to inherit these.

if getvar('OPC_CLASS'):  opc_class = getvar('OPC_CLASS')
if getvar('OPC_GATE_HOST'):  opc_gate_host = getvar('OPC_GATE_HOST')
if getvar('OPC_GATE_PORT'):  opc_gate_port = int(getvar('OPC_GATE_PORT'))

class opc(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
        self._remote_hosts = {}
        self._init_times = {}
        self._tx_times = {}

    def get_clients(self):
        """Return list of server instances as a list of (GUID,host,time) tuples"""
        
        reg = self.getDaemon().getRegistered()
        hosts = self._remote_hosts
        init_times = self._init_times
        tx_times = self._tx_times
        
        hlist = [(k, hosts[k] if hosts.has_key(k) else '', init_times[k], tx_times[k]) for k,v in reg.iteritems() if v == None]
        return hlist
    
    def create_client(self):
        """Create a new OpenOPC instance in the Pyro server"""
        
        opc_obj = OpenOPC.client(opc_class)
        base_obj = Pyro.core.ObjBase()
        base_obj.delegateTo(opc_obj)
        uri = self.getDaemon().connect(base_obj)

        opc_obj._open_serv = self
        opc_obj._open_self = base_obj
        opc_obj._open_host = self.getDaemon().hostname
        opc_obj._open_port = self.getDaemon().port
        opc_obj._open_guid = uri.objectID
        
        remote_ip = self.getLocalStorage().caller.addr[0]
        try:
            remote_name = socket.gethostbyaddr(remote_ip)[0]
            self._remote_hosts[uri.objectID] = '%s (%s)' % (remote_ip, remote_name)
        except socket.herror:
            self._remote_hosts[uri.objectID] = '%s' % (remote_ip)
        self._init_times[uri.objectID] =  time.time()
        self._tx_times[uri.objectID] =  time.time()
        return Pyro.core.getProxyForURI(uri)

    def release_client(self, obj):
        """Release an OpenOPC instance in the Pyro server"""

        self.getDaemon().disconnect(obj)
        del self._remote_hosts[obj.GUID()]
        del self._init_times[obj.GUID()]
        del self._tx_times[obj.GUID()]
        del obj
   
class OpcService(win32serviceutil.ServiceFramework):
    _svc_name_ = "zzzOpenOPCService"
    _svc_display_name_ = "OpenOPC Gateway Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
    def SvcStop(self):
        servicemanager.LogInfoMsg('\n\nStopping service')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg('\n\nStarting service on port %d' % opc_gate_port)

        daemon = Pyro.core.Daemon(host=opc_gate_host, port=opc_gate_port)
        daemon.connect(opc(), "opc")

        while win32event.WaitForSingleObject(self.hWaitStop, 0) != win32event.WAIT_OBJECT_0:
            socks = daemon.getServerSockets()
            ins,outs,exs = select.select(socks,[],[],1)
            for s in socks:
                if s in ins:
                    daemon.handleRequests()
                    break
                    
        daemon.shutdown()
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(OpcService)
            servicemanager.Initialize('zzzOpenOPCService', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(OpcService)
