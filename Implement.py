# coding:utf-8

from __future__ import print_function
import os
import sys
import time
import re
import Conn as conn
import Sundry as s
import threading
from collections import OrderedDict as odd

# <<<Config Field>>>
ip_engine_target = '10.203.1.175' 
ip_engine_initiator = '10.203.1.176' 

telnet_port = 23
FTP_port = 21
passwd = 'password'
trace_level_cfg = 2
firmware_file_name = 'fw.bin'

strTraceFolder = 'Trace'
strPCFolder = 'Current_Config'
lstPCCommand = ['vpd',
                'conmgr status',
                'mirror',
                'group',
                'map',
                'drvstate',
                'history',
                'sfp all']
# <<<Config Field>>>

def receive(message_output,
        light_obj_telnet,
        light_telnet,
        light_obj_FTP,
        light_FTP,
        mode,
        IP_Entered,
        license,
        version,
        speed
        ):
    if s.is_IP(IP_Entered):
        pass
    else:
        message_output.insert('insert','\n***Please type correct IP address\n')
        sys.exit()
    solid_args = (message_output, light_obj_telnet, light_telnet, light_obj_FTP, light_FTP)
    if mode == 'target':
        config_target(IP_Entered,license,version,speed,solid_args)

    elif mode == 'initiator':
        config_initiator(IP_Entered,license,version,speed,solid_args)

    elif mode == 'start':
        start_test()

    elif mode == 'status':
        get_test_status()

    elif mode == 'result':
        get_test_result()

    elif mode == 'reset':
        reset_all_engines()

def _config_universal(mode, IP_Entered,license,version,speed,solid_args):
    obj_msg_out = solid_args[0]
    obj_light_telnet = solid_args[1]
    instance_light_telnet = solid_args[2]
    obj_light_FTP = solid_args[3]
    instance_light_FTP = solid_args[4]

    objEngine = Action(IP_Entered, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'  1. Start changing FW.\n')
    # objEngine.change_FW(firmware_file_name)
    s.msg_out(obj_msg_out,'  1. Finish changing FW, Rebooting...\n')
    del objEngine
    s.chg_light_to_red(obj_light_telnet,instance_light_telnet)
    s.chg_light_to_red(obj_light_FTP,instance_light_FTP)
    # s.sand_glass(45,obj_msg_out)

    objEngine = Action(IP_Entered, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'  2. Start restoring factory default.\n')
    objEngine.factory_default()
    s.msg_out(obj_msg_out,'  2. Finish restoring factory default, Rebooting...\n')
    del objEngine
    s.chg_light_to_red(obj_light_telnet,instance_light_telnet)
    s.chg_light_to_red(obj_light_FTP,instance_light_FTP)
    s.sand_glass(20,obj_msg_out)


    objEngine = Action(IP_Entered, telnet_port, passwd, FTP_port, version, solid_args)
    solid_args[0].insert('insert','  3. Start changing IP address.\n')
    objEngine.change_ip_address(ip_engine_target)
    solid_args[0].insert('insert','  3. Finish changing IP address, Rebooting...\n')
    del objEngine
    s.chg_light_to_red(obj_light_telnet,instance_light_telnet)
    s.chg_light_to_red(obj_light_FTP,instance_light_FTP)
    s.sand_glass(20,obj_msg_out)
    

    objEngine = Action(ip_engine_target, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'  4. Start changing UID.\n')
    objEngine.change_UID(mode)
    s.msg_out(obj_msg_out,'  4. Finish changing UID, Rebooting...\n')
    del objEngine
    s.chg_light_to_red(obj_light_telnet,instance_light_telnet)
    s.chg_light_to_red(obj_light_FTP,instance_light_FTP)
    s.sand_glass(20,obj_msg_out)

    objEngine = Action(ip_engine_target, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'  5. Start installing license.\n')
    objEngine.install_license(license)

    s.msg_out(obj_msg_out,'  6. Start setting shutdown behaviour.\n')
    objEngine.shutdown_behaviour()

    s.msg_out(obj_msg_out,'  7. Start changing mode of FC ports.\n')
    objEngine.change_FC_mode('all','loop')

    s.msg_out(obj_msg_out,'  8. Start changing speed of FC ports.\n')
    objEngine.change_FC_speed('all',speed)

    s.msg_out(obj_msg_out,'  9. Start syncing time of engine with system.\n')
    objEngine.sync_time()

def config_target(IP_Entered,license,version,speed,solid_args):
    obj_msg_out = solid_args[0]
    _config_universal('target', IP_Entered,license,version,speed,solid_args)

    objEngine = Action(ip_engine_target, telnet_port, passwd, FTP_port, version, solid_args)

    s.msg_out(obj_msg_out,'  10. Start creating fake drives.\n')
    objEngine.create_fake_drive()

    s.msg_out(obj_msg_out,'  11. Start creating mirror and mapping.\n')
    objEngine.mirror_and_mapping()

    s.msg_out(obj_msg_out,'  12. Start registering initiators.\n')
    objEngine.register_initiator()

    #show info -- mirror and mapping.
    objEngine.show_mirror_and_mappting()

    #show info -- conmgr status.
    objEngine.show_conmgr_status()

def config_initiator(IP_Entered,license,version,speed,solid_args):
    obj_msg_out = solid_args[0]
    _config_universal('initiator', IP_Entered,license,version,speed,solid_args)

    objEngine = Action(ip_engine_initiator, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'  10. Start registering drives.\n')
    objEngine.register_drives()

    #show info -- conmgr status.
    objEngine.show_conmgr_status()

def start_test():
    pass

def get_test_status():
    pass

def get_test_result():
    pass

def reset_all_engines():
    pass

class Action():

    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, version, solid_args, intTimeout=1.5):
        self._host = strIP
        self._TNport = intTNPort
        self._FTPport = intFTPPort
        self._FTP_username = self.get_ftp_username(version)
        self._password = strPassword
        self._timeout = intTimeout

        #restore object and instance from solid_args
        self.message_output = solid_args[0]
        self.obj_light_telnet = solid_args[1]
        self.instance_light_telnet = solid_args[2]
        self.obj_light_FTP = solid_args[3]
        self.instance_light_FTP = solid_args[4]

        self._TN_Conn = None
        self._FTP_Conn = None
        self._TN_Connect_Status = None
        self._telnet_connect()
        self.AHStatus = self._TN_Conn.is_AH()
        self.strVPD = self._executeCMD('vpd')

    # version determines the value of FTP username
    def get_ftp_username(self, version):
        if version == 'loxoll':
            return 'adminftp'
        elif version == 'vicom':
            return 'ftpvicom'

    def _telnet_connect(self):
        s.msg_out(self.message_output,'0. Telnet Connecting to %s ...\n' % self._host)
        self._TN_Conn = conn.HAAPConn(self._host,
                                      self._TNport,
                                      self._password,
                                      self._timeout)
        self._TN_Connect_Status = self._TN_Conn.get_connection_status()
        if self._TN_Connect_Status:
            s.msg_out(self.message_output, '0. Telnet Connected to %s.\n' % self._host)
            s.chg_light_to_green(self.obj_light_telnet,self.instance_light_telnet)
        else:
            s.msg_out(self.message_output, '0. Telnet Connect to %s Failed!!!\n' % self._host)

    # @s.deco_Exception
    def _executeCMD(self, cmd):
        if self._TN_Connect_Status:
            return self._TN_Conn.exctCMD(cmd)

    def _FTP_connect(self):
        self._FTP_Conn = conn.FTPConn(self._host,
                                      self._FTPport,
                                      self._FTP_username,
                                      self._password,
                                      self._timeout)

    def _ftp(self):
        s.msg_out(self.message_output, '0. FTP Connecting to %s ...\n' % self._host)
        if self._FTP_Conn:
            connFTP = self._FTP_Conn
        else:
            self._FTP_connect()
            connFTP = self._FTP_Conn
        if connFTP:
            s.msg_out(self.message_output, '0. FTP Connected to %s.\n' % self._host)
            s.chg_light_to_green(self.obj_light_FTP,self.instance_light_FTP)
        else:
            s.msg_out(self.message_output, '0. FTP Connect to %s Failed!!!\n' % self._host)
        return connFTP

    def _telnet_write(self, str, time_out):
        str_encoded = s.encode_utf8(str)
        self._TN_Conn.Connection.write(str_encoded)
        time.sleep(time_out)


    # @s.deco_Exception
    def change_FW(self, strFWFile):
        connFTP = self._ftp()
        time.sleep(0.25)
        connFTP.PutFile('/mbflash', './', 'fwimage', strFWFile)
        print('FW upgrade completed for {}, waiting for reboot...'.format(
            self._host))

    def factory_default(self):
        if self._TN_Conn.go_to_main_menu():
            self._telnet_write('f', 0.1)
            self._TN_Conn.Connection.read_until(s.encode_utf8('Reset'), timeout = 1)
            time.sleep(0.25)
            self._telnet_write('y', 0.1)
            self._telnet_write('y', 0.1)
            self._telnet_write('y', 0.1)
            print('Engine reset successful, waiting for reboot...about 20s\n')

    def change_ip_address(self, new_ip_address):
        s.msg_out(self.message_output,'    3.1 changing IP from "%s" to "%s" ...\n' % (self._host, new_ip_address))
        if self._TN_Conn.go_to_main_menu():
            self._telnet_write('6', 0.1)
            self._TN_Conn.Connection.read_until(s.encode_utf8('interface'), timeout = 2)
            time.sleep(0.2)
            self._telnet_write('e', 0.1)
            self._telnet_write('a', 0.1)
            self._TN_Conn.Connection.read_until(s.encode_utf8('new IP'), timeout = 2)
            self._telnet_write(new_ip_address, 0.1)
            self._telnet_write('\r', 0.1)
            self._telnet_write('\r', 0.1)

            self._TN_Conn.Connection.read_until('<Enter> = done'.encode(encoding="utf-8"), timeout = 2)
            self._telnet_write('\r', 0.1)
            # try:
            self._TN_Conn.Connection.read_until(s.encode_utf8('Coredump'), timeout = 2)
            self._TN_Conn.Connection.write(s.encode_utf8('b'))
            self._TN_Conn.Connection.read_until(s.encode_utf8('Reboot'), timeout = 1)
            time.sleep(0.4)
            self._TN_Conn.Connection.write(s.encode_utf8('y'))

    def change_UID(self,mode):
        if mode == 'target':
            str_uid = '0000006022112250'
        elif mode == 'initiator':
            str_uid = '0000006022112251'
        else:
            s.msg_out(self.message_output,'failed ,check')
            sys.exit()
        uid_cmd = 'uid %s' % str_uid
        output = self._executeCMD(uid_cmd)
        if 'take full effect!' in output:
            self._executeCMD('boot')
        s.msg_out(self.message_output,'  4. Finish changeing UID, Rebooting')
        s.sand_glass(20,self.message_output)

    def install_license(self, string_license):
        if string_license:
            lst_lsc = re.split(' |,|;',string_license)
            if len(lst_lsc) != 3:
                s.msg_out(self.message_output,'    ***5.0 Please check license code')
                sys.exit()
            lst_lsc_id = [3,5,6]
            lst_lsc_desc = ['Firmware Downgrade','IO Generater','Fake Drive']
            flag_success = 0
            for i in range(len(lst_lsc)):
                # Command: "license install 3 xxxxxxx"
                cmd_lsc_install = 'license install %s %s' % (str(lst_lsc_id[i]),lst_lsc[i])
                output = self._executeCMD(cmd_lsc_install)
                if 'installed' in output:
                    s.msg_out(
                        self.message_output,'    5.%d %s License install successful on %s.\n' % (
                            i+1,lst_lsc_desc[i],self._host))
                    flag_success = flag_success + 1
                else:
                    s.msg_out(self.message_output,'    ***5.%d %s License isntall failed!' % (i+1,lst_lsc_desc[i]))
            if flag_success == 3:
                s.msg_out(self.message_output,'  5. Finish installing licenses on %s.' % self._host)

        else:
            s.msg_out(self.message_output,'  ***5.0 License install failed on %s.\n    Please check license code' % self._host)
            sys.exit()

    def shutdown_behaviour(self):
        if self._TN_Conn.go_to_main_menu():
            self._telnet_write('6', 0.1)
            for i in range(2):
                output = self._TN_Conn.Connection.read_until(s.encode_utf8('seen'), timeout = 1)
                if not s.encode_utf8('stay up') in output:
                    self._telnet_write('x', 0.1)
                else:
                    break
            s.msg_out(self.message_output,'  6.Finish setting shutdown behaviour.\n')
        else:
            s.msg_out(self.message_output,'  ***5.Setting shutdown behaviour failed!')
            sys.exit()
    
    # port: 'a','b','c','d','all';mode: 'loop','point'
    def change_FC_mode(self,port,mode):

        def _change_mode(port,mode):
            self._telnet_write(port, 0.1)
            output = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
            # print('--------output after write port\n',output)
            if mode == 'loop':
                if not s.encode_utf8('Arbitrated loop') in output:
                    self._telnet_write('l', 0.1)
                    # o  = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
                    # print('----------\n',o)
            elif mode == 'point':
                if s.encode_utf8('Arbitrated loop') in output:
                    self._telnet_write('l', 0.1)
                    # o = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
                    # print('----------\n',o)
            self._telnet_write('\r', 0.1)
            self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)

        if self._TN_Conn.go_to_main_menu():
            time.sleep(0.25)
            self._telnet_write('6', 0.1)
            # output6 = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
            # print('--------output after write 6\n',output6)
            if port == 'all':
                lst_port = ['a','b','c','d']
                for port in lst_port:
                    _change_mode(port, mode)
                    s.msg_out(self.message_output,'      Port %s Changed.\n' % port)
            else:
                _change_mode(port, mode)
            self._telnet_write('\r', 0.1)
            self._telnet_write('\r', 0.1)
            s.msg_out(self.message_output,'  7. Finish changing mode of FC ports.\n')
        else:
            s.msg_out(self.message_output,'  ***7. Changing mode of FC ports failed.\n')
            sys.exit()

        

    def change_FC_speed(self,port,speed):
        def _change_speed(port,speed):
            self._telnet_write(port, 0.1)
            self._telnet_write('s', 0.1)
            self._telnet_write(speed, 0.1)
            # output = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
            # print('--------output after speed set\n',output)
            self._telnet_write('\r', 0.1)

        if self._TN_Conn.go_to_main_menu():
            self._telnet_write('6', 0.1)
            # output6 = self._TN_Conn.Connection.read_until(s.encode_utf8('Default: Point'), timeout = 1)
            # print('--------output after write 6\n',output6)
            if port == 'all':
                lst_port = ['a','b','c','d']
                for port in lst_port:
                    _change_speed(port, speed)
                    s.msg_out(self.message_output,'      Port %s Changed.\n' % port)
            else:
                _change_speed(port, speed)
            self._telnet_write('\r', 0.1)
            s.msg_out(self.message_output,'  8. Finish changing speed of FC ports.\n')
        else:
            s.msg_out(self.message_output,'  ***8. Changing speed of FC ports failed!\n')
            sys.exit()

    def sync_time(self):
        if self.AHStatus:
            print("Engine '%s' is at AH status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return

        def _exct_cmd():
            t = s.TimeNow()

            def complete_print(strDesc):
                print('    Set  %-13s for engine "%s" completed...' % ('"%s"' % strDesc, self._host))
                s.msg_out(self.message_output,'    Set  %-13s for engine "%s" completed.\n' % ('"%s"' % strDesc, self._host))
                time.sleep(0.25)

            try:
                # Set Time
                if self._TN_Conn.exctCMD('rtc set time %d %d %d' % (
                        t.h(), t.mi(), t.s())):
                    complete_print('Time')
                    # Set Date
                    if self._TN_Conn.exctCMD('rtc set date %d %d %d' % (
                            t.y() - 2000, t.mo(), t.d())):
                        complete_print('Date')
                        # Set Day of the Week
                        DoW = t.wd() + 2
                        if DoW == 8:
                            DoW - 7
                        if self._TN_Conn.exctCMD('rtc set day %d' % DoW):
                            complete_print('Day_of_Week')
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'rtc set faild for engine "{}" with error:'.format(
                              self._host),
                          '"{}"'.format(E))
                sys.exit()

        if self._TN_Conn:
            if _exct_cmd():
                print(
                    '\nSetting time for engine "%s" completed...' % 
                    self._host)
                s.msg_out(self.message_output,'  9. Finish syncing time of engine with system.\n')
            else:
                print('\nSetting time for engine "%s" failed!!!' % self._host)
                s.msg_out(self.message_output,'  ***9. Syncing time of engine failed.\n')

    def create_fake_drive(self):
        self._executeCMD('fake on')
        s.msg_out(self.message_output,'  10. Finish creating fake drives.\n')



    def mirror_and_mapping(self):
        self._executeCMD('mirror create 2044')
        self._executeCMD('map auto on')
        self._executeCMD('map 0 33281')
        s.msg_out(self.message_output,'  11. Finish creating mirror and mapping.\n')

    def show_mirror_and_mappting(self):
        string_to_show = ''
        string_to_show = string_to_show + self._executeCMD('mirror') + '\n'
        string_to_show =string_to_show + self._executeCMD('map') + '\n'
        s.msg_out(self.message_output, '''
  Mirror and Mapping:
  -------------------------------------------
  %s
  -------------------------------------------
              \n''' % string_to_show) 

    def _register(self, lst_cmd):
        self._executeCMD('conmgr read')
        for cmd in lst_cmd:
            self._executeCMD(cmd)
            time.sleep(0.1)
        self._executeCMD('conmgr write')

    def register_drives(self):
        #generate command
        lst_cmd = []
        lst_port = ['a1','a2','a3','a4']
        for i in range(len(lst_port)):
            str_cmd = 'conmgr drive add S %d %s 2%d00-006022-112250 0' % (
                i+1,lst_port[i],i+1)
            lst_cmd.append(str_cmd)

        #start registing
        self._register(lst_cmd)
        s.msg_out(self.message_output,'  12. Finish registering initiators.\n')

    def register_initiator(self):
        #generate command
        lst_cmd = []
        lst_port = ['a1','a2','a3','a4']
        for i in range(len(lst_port)):
            str_cmd = 'conmgr initiator add %d %s 2%d00-006022-112251' % (
                i+1,lst_port[i],i+1)
            lst_cmd.append(str_cmd)

        #start registing
        self._register(lst_cmd)

    def show_conmgr_status(self):
        string_to_show = self._executeCMD('conmgr status')
        s.msg_out(self.message_output, '''
  Conmgr Status:
  -------------------------------------------
  %s
  -------------------------------------------
              \n''' % string_to_show) 

    # @s.deco_Exception
    def auto_commands(self, strCMDFile):
        tn = self._TN_Conn
        if self.AHStatus:
            print("Engine '%s' is at AH status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return
        with open(strCMDFile, 'r') as f:
            lstCMD = f.readlines()
            for strCMD in lstCMD:
                strResult = tn.exctCMD(strCMD)
                if strResult:
                    print(strResult)
                else:
                    print('\rExecute command "{}" failed ...'.format(
                        strCMD))
                    break
                time.sleep(0.1)

    @s.deco_OutFromFolder
    def get_trace(self, strBaseFolder, intTraceLevel):
        tn = self._TN_Conn
        connFTP = self._ftp()

        def _get_oddCommand(intTraceLevel):
            oddCMD = odd()
            if intTraceLevel == 1 or intTraceLevel == 2 or intTraceLevel == 3:
                oddCMD['Trace'] = 'ftpprep trace'
                if intTraceLevel == 2 or intTraceLevel == 3:
                    oddCMD['Primary'] = 'ftpprep coredump primary all'
                    if intTraceLevel == 3:
                        oddCMD['Secondary'] = 'ftpprep coredump secondary all'
                return oddCMD
            else:
                print('Trace level must be: 1 or 2 or 3, please refer "Config.ini" ')

        def _get_trace_file(command, strTraceDes):

            # TraceDes = Trace Description
            def _get_trace_name():
                result = tn.exctCMD(command)
                reTraceName = re.compile(r'(ftp_data_\d{8}_\d{6}.txt)')
                strTraceName = reTraceName.search(result)
                if strTraceName:
                    return strTraceName.group()
                else:
                    print('Generate trace "{}" file failed for "{}"'.format(
                        strTraceDes, self._host))

            trace_name = _get_trace_name()
            if trace_name:
                time.sleep(0.1)
                local_name = 'Trace_{}_{}.log'.format(self._host, strTraceDes)
                if connFTP.GetFile('mbtrace', '.', trace_name, local_name):
                    print('Get trace "{:<10}" for "{}" completed ...'.format(
                        strTraceDes, self._host))
                    return True
                else:
                    print('Get trace "{:<10}" for engine "{}" failed!!!\
                        '.format(strTraceDes, self._host))
                #     s.ShowErr(self.__class__.__name__,
                #               sys._getframe().f_code.co_name,
                #               'Get Trace "{:<10}" for Engine "{}" Failed!!!\
                #               '.format(strTraceDes, self._host))

        oddCommand = _get_oddCommand(intTraceLevel)
        lstCommand = list(oddCommand.values())
        lstDescribe = list(oddCommand.keys())

        if s.GotoFolder(strBaseFolder):
            for i in range(len(lstDescribe)):
                try:
                    if _get_trace_file(lstCommand[i], lstDescribe[i]):
                        continue
                    else:
                        break
                except Exception as E:
                    # s.ShowErr(self.__class__.__name__,
                    #           sys._getframe().f_code.co_name,
                    #           'Get Trace "{}" Failed for Engine "{}",\
                    # Error:'.format(lstDescribe[i], self._host),
                    #           E)
                    break
                time.sleep(0.1)

    @s.deco_OutFromFolder
    def periodic_check(self, lstCommand, strResultFolder, strResultFile):
        if self.AHStatus:
            print("Engine '%s' is at AH status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return
        tn = self._TN_Conn
        s.GotoFolder(strResultFolder)
        if tn.exctCMD('\n'):
            with open(strResultFile, 'w') as f:
                for strCMD in lstCommand:
                    time.sleep(0.1)
                    strResult = tn.exctCMD(strCMD)
                    if strResult:
                        print(strResult)
                        f.write(strResult)
                    else:
                        strErr = '\n*** Execute command "{}" failed\n'.format(
                            strCMD)
                        print(strErr)
                        f.write(strErr)

    def set_time(self):
        if self.AHStatus:
            print("Engine '%s' is at AH status(AH Code %d)"
                  % (self.host, self.AHStatus))
            return

        def _exct_cmd():
            t = s.TimeNow()

            def complete_print(strDesc):
                print('    Set  %-13s for engine "%s" completed...\
                        ' % ('"%s"' % strDesc, self._host))
                time.sleep(0.25)

            try:
                # Set Time
                if self._TN_Conn.exctCMD('rtc set time %d %d %d' % (
                        t.h(), t.mi(), t.s())):
                    complete_print('Time')
                    # Set Date
                    if self._TN_Conn.exctCMD('rtc set date %d %d %d' % (
                            t.y() - 2000, t.mo(), t.d())):
                        complete_print('Date')
                        # Set Day of the Week
                        DoW = t.wd() + 2
                        if DoW == 8:
                            DoW - 7
                        if self._TN_Conn.exctCMD('rtc set day %d' % DoW):
                            complete_print('Day_of_Week')
                return True
            except Exception as E:
                s.ShowErr(self.__class__.__name__,
                          sys._getframe().f_code.co_name,
                          'rtc set faild for engine "{}" with error:'.format(
                              self._host),
                          '"{}"'.format(E))

        if self._TN_Conn:
            if _exct_cmd():
                print(
                    '\nSetting time for engine "%s" completed...' % 
                    self._host)
            else:
                print('\nSetting time for engine "%s" failed!!!' % self._host)
        else:
            print('\nSetting time for engine "%s" failed!!!' % self._host)


# solid_args = ('a','a','a','a','a')
        
# w = Action('10.203.1.177', 23, 'password',
#                  21, 'loxoll', solid_args, intTimeout=1.5)
# # w.change_ip_address('10.203.1.177')
# w.install_license('234234234,23424244,24224434')
# w.shutdown_behaviour()

if __name__ == '__main__':

    pass
