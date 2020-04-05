# coding:utf-8

from __future__ import print_function
import os
import sys
import time
import re
import Conn as conn
import Sundry as s
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

    if mode == 'initiator':
        message_output.insert('insert',(ip_engine_initiator,
        string_license))
        for i in range(10):
            chg_light_to_green(light_obj_telnet,light_telnet)
            time.sleep(0.5)
            chg_light_to_red(light_obj_telnet,light_telnet)
            time.sleep(0.5)

    if mode == 'start':
        pass
    if mode == 'status':
        pass
    if mode == 'result':
        pass
    if mode == 'reset':
        pass





###-------------need improve message show using decorator----------
def config_target(IP_Entered,license,version,speed,solid_args):
    obj_msg_out = solid_args[0]

    s.msg_out(obj_msg_out,'0. Connecting to Engine %s \n' % IP_Entered)
    objEngine = Action(IP_Entered, telnet_port, passwd, FTP_port, version, solid_args)
    s.msg_out(obj_msg_out,'0. Connected to Engine %s \n' % IP_Entered)

    s.msg_out(obj_msg_out,'  1. Start to Change FW\n')
    objEngine.change_FW(firmware_file_name)
    s.msg_out(obj_msg_out,'  1. Change FW Done, Rebooting...\n')
    s.sand_glass(45)

    solid_args[0].insert('insert','  2. Start Restor Factory Default\n')
    objEngine.factory_default()
    solid_args[0].insert('insert','  2. Restor Factory Default Done, Rebooting...\n')
    sandglass(20)

    solid_args[0].insert('insert','  3. Start Changing IP Address\n')
    objEngine.change_ip_address(ip_engine_target)
    solid_args[0].insert('insert','  3. Change IP Address Done, Rebooting...\n')
    sandglass(15)

    del objEngine

    s.msg_out(obj_msg_out,'0. Connecting to Engine %s' % ip_engine_target)
    objEngine = Action(ip_engine_target, telnet_port, passwd, FTP_port, version, solid_args)
    
    s.msg_out(obj_msg_out,'  4. Start to Install License\n')
    objEngine.install_license(license)
    s.msg_out(obj_msg_out,'  4. Install License Done\n')

    # s.msg_out(obj_msg_out,'  5. Start to change UID\n')
    # objEngine.change_UID()
    # s.msg_out(obj_msg_out,'  5. change UID Done\n')

    # s.msg_out(obj_msg_out,'  6. Start to change UID\n')
    # objEngine.shutdown_behaviour()
    # s.msg_out(obj_msg_out,'  6. change UID Done\n')

    # s.msg_out(obj_msg_out,'  7. Start to change UID\n')
    # objEngine.change_FC_mode()
    # s.msg_out(obj_msg_out,'  7. change UID Done\n')

    # s.msg_out(obj_msg_out,'  5. Start to change UID\n')
    # objEngine.change_FC_speed(speed)
    # s.msg_out(obj_msg_out,'  5. change UID Done\n')

    # s.msg_out(obj_msg_out,'  5. Start to change UID\n')
    # objEngine.sync_time()
    # s.msg_out(obj_msg_out,'  5. change UID Done\n')

    # s.msg_out(obj_msg_out,'  5. Start to change UID\n')
    # objEngine.create_fake_drive()
    # s.msg_out(obj_msg_out,'  5. change UID Done\n')

    # s.msg_out(obj_msg_out,'  5. Start to change UID\n')
    # objEngine.mirror_and_mapping()
    # s.msg_out(obj_msg_out,'  5. change UID Done\n')

    # mirror_and_mapping = objEngine.show_mirror_and_mappting()
    # solid_args[0].insert('insert',
    #     '''  5. Mirror and Mapping info show below:\n
    #     --------------------------------------------\n
    #     %s
    #     --------------------------------------------\n''' % mirror_and_mapping)


# class ActionOldVersion(Action):
#     """docstring for ActionOldVersion"""
#     def __init__(self, strIP, intTNPort, strPassword,
#                  intFTPPort, version, solid_args, intTimeout=1.5):
#         super().__init__(self, strIP, intTNPort, strPassword,
#                  intFTPPort, intTimeout)
#         if version == 'vicom':
#             self._FTP_username = 'vicomftp'
#         elif version == 'vicom':
#             self._FTP_username = 'ftpadmin'
#         self.solid_args = solid_args

# #rewrite function _FTP_connect with alterable FTP username
#     def _FTP_connect(self):
#         self._FTP_Conn = conn.FTPConn(self._host,
#                                       self._FTPport,
#                                       self._FTP_username,
#                                       self._password,
#                                       self._timeout)
        


class Action():
    '''
get_trace
pc
backup
change_FW
emc
stt
st
    '''

    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, version, solid_args, intTimeout=1.5):
        self._host = strIP
        self._TNport = intTNPort
        self._FTPport = intFTPPort
        self._password = strPassword
        self._timeout = intTimeout

        #restore object and instance from solid_args
        self.message_output = solid_args[0]
        self.obj_light_telnet = solid_args[1]
        self.instance_light_telnet = solid_args[2]
        self.obj_light_FTP = solid_args[3]
        self.instance_light_FTP = solid_args[4]

        # version determines the value of FTP username
        if version == 'vicom':
            self._FTP_username = 'vicomftp'
        elif version == 'vicom':
            self._FTP_username = 'ftpadmin'

        self._TN_Conn = None
        self._FTP_Conn = None
        self._TN_Connect_Status = None
        self._telnet_connect()
        self.AHStatus = self._TN_Conn.is_AH()
        self.strVPD = self._executeCMD('vpd')

    def _output_to_window(self, msg):
        self.message_output.insert('insert',msg)

    def _telnet_connect(self):
        self._TN_Conn = conn.HAAPConn(self._host,
                                      self._TNport,
                                      self._password,
                                      self._timeout)
        self._TN_Connect_Status = self._TN_Conn.get_connection_status()

    @s.deco_Exception
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
        if self._FTP_Conn:
            connFTP = self._FTP_Conn
        else:
            self._FTP_connect()
            connFTP = self._FTP_Conn
        return connFTP

    def _telnet_write(self, str, time_out):
        str_encoded = s.encode_utf8(str)
        self._TN_Conn.Connection.write(str_encoded)
        time.sleep(time_out)


    @s.deco_Exception
    def change_FW(self, strFWFile):
        connFTP = self._ftp()
        time.sleep(0.25)
        connFTP.PutFile('/mbflash', './', 'fwimage', strFWFile)
        self._output_to_window(
            '    Rebooting Engine %s to change firmware, Wait for 45 seconds\n' % self._host)
        print('FW upgrade completed for {}, waiting for reboot...'.format(
            self._host))
        for i in range(45):
            print('. ')
            self._output_to_window('. ')
        print('\n')
        self._output_to_window('\n')

    def factory_default():
        if self._TN_Conn.go_to_main_menu():
            self._TN_Conn.Connection.write('f')
            self._TN_Conn.Connection.read_until('Reset'.encode(encoding="utf-8"), timeout = 1)
            time.sleep(0.25)
            self._TN_Conn.Connection.write('y')
            time.sleep(0.25)
            self._TN_Conn.Connection.write('y')
            time.sleep(0.25)
            self._TN_Conn.Connection.write('y')
            print('Engine reset successful, waiting for reboot...about 30s')

    def change_ip_address(self, new_ip_address):
        if self._TN_Conn.go_to_main_menu():
    #         self._TN_Conn.change_ip_address(new_ip_address)

    # def change_ip_address(self, new_ip_address):
    #     if self.go_to_main_menu():
            self._TN_Conn.Connection.write('6'.encode(encoding="utf-8"))
            self._TN_Conn.Connection.read_until(s.encode_utf8('interface'), timeout = 2)
            time.sleep(0.2)
            self._telnet_write('e', 0.1)
            self._telnet_write('a', 0.1)
            self._TN_Conn.Connection.read_until(s.encode_utf8('new IP'), timeout = 2)
            time.sleep(0.2)
            self._TN_Conn.Connection.write(s.encode_utf8('new_ip_address'))
            self._TN_Conn.Connection.write('\r'.encode(encoding="utf-8"))
            time.sleep(0.2)
            self._TN_Conn.Connection.write(s.encode_utf8('\r'))
            time.sleep(0.2)
            self._TN_Conn.Connection.read_until('<Enter> = done'.encode(encoding="utf-8"), timeout = 2)
            self._TN_Conn.Connection.write('\r'.encode(encoding="utf-8"))
            time.sleep(0.5)
            # try:
            self._TN_Conn.Connection.read_until(s.encode_utf8('Coredump'), timeout = 2)
            self._TN_Conn.Connection.write(s.encode_utf8('b'))
            self._TN_Conn.Connection.read_until(s.encode_utf8('Reboot'), timeout = 1)
            time.sleep(0.4)
            self._TN_Conn.Connection.write(s.encode_utf8('y'))
            print('Rebooting engine, Please waiting...\n')
            s.sand_glass(45,self.message_output)

    def install_license():
        pass

    def change_UID():
        pass

    def shutdown_behaviour():
        pass

    def change_FC_mode():
        pass

    def change_fC_speed():
        pass

    def sync_time():
        pass

    def create_fake_drive():
        pass

    def mirror_and_mapping():
        pass

    def show_mirror_and_mappting():
        pass

    @s.deco_Exception
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
                time.sleep(0.5)

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

    def show_time(self):
        if self.AHStatus:
            print("Engine '%s' is at AH Status(AH Code %d)"
                  % (self._host, self.AHStatus))
            return
        print('Time of engine "%s":' % self._host)
        if self._TN_Conn:
            try:
                print(self._TN_Conn.exctCMD('rtc').replace(
                    '\nCLI>', '').replace('rtc\r\n', ''))
            except BaseException:
                print('Get time of engine "%s" failed' % self._host)

    def get_version(self):
        if self.strVPD is None:
            return
        reFirmWare = re.compile(r'Firmware\sV\d+(.\d+)*')
        resultFW = reFirmWare.search(self.strVPD)
        if resultFW:
            return resultFW.group().replace('Firmware ', '')
        else:
            print('Get firmware version failed for engine "%s"' % self._host)

if __name__ == '__main__':

    pass
