# coding:utf-8

from __future__ import print_function
import os
import sys
import time
import re
import Conn as conn
import Sundry as s
from collections import OrderedDict as odd

# <<<Get Config Field>>>

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
# <<<Get Config Field>>>

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

def config_target(IP_Entered,license,version,speed,solid_args):

    objEngine = ActionOldVersion(IP_Entered, telnet_port, passwd, FTP_port, 1.5, version, solid_args)
    
    objEngine.change_FW(firmware_file_name)

    change_firmware(IP_Entered,version,solid_args)
    factory_default(IP_Entered,solid_args)
    change_ip_address(IP_Entered,ip_engine_target)
    install_license(ip_engine_target,license)
    change_UID(ip_engine_target)
    shutdown_behaviour(ip_engine_target)
    change_FC_mode(ip_engine_target)
    change_FC_speed(ip_engine_target,speed)
    sync_time(ip_engine_target)
    create_fake_drive(ip_engine_target)
    mirror_and_mapping(ip_engine_target)


def change_firmware(ip, version, fw_file):
    Action(ip, telnet_port, passwd, FTP_port).change_FW(fw_file)


def get_trace_all(trace_level):
    folder = '%s/%s' % (strTraceFolder, s.time_now_folder())
    if trace_level:
        for ip in list_engines_IP:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level)
    else:
        for ip in list_engines_IP:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level_cfg)


def get_trace(ip, trace_level):
    folder = '%s/%s' % (strTraceFolder, s.time_now_folder())
    try:
        if trace_level:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level)
        else:
            Action(ip, telnet_port, passwd, FTP_port).get_trace(
                folder, trace_level_cfg)
    finally:
        return folder


def execute_multi_commands(ip, command_file):
    Action(ip, telnet_port, passwd, FTP_port).auto_commands(command_file)


def set_time_all():
    for ip in list_engines_IP:
        Action(ip, telnet_port, passwd, FTP_port).set_time()


def set_time(ip):
    Action(ip, telnet_port, passwd, FTP_port).set_time()


def show_time_all():
    for ip in list_engines_IP:
        Action(ip, telnet_port, passwd, FTP_port).show_time()


def show_time(ip):
    Action(ip, telnet_port, passwd, FTP_port).show_time()


def periodically_check_all():
    for ip in list_engines_IP:
        PCFile_name = 'PC_%s_Engine_%s.log' % (
            s.time_now_folder(), ip)
        Action(ip, telnet_port, passwd, FTP_port).periodic_check(
            lstPCCommand, strPCFolder, PCFile_name)


def periodically_check(ip):
    PCFile_name = 'PC_%s_Engine_%s.log' % (
        s.time_now_folder(), ip)
    Action(ip, telnet_port, passwd, FTP_port).periodic_check(
        lstPCCommand, strPCFolder, PCFile_name)

class ActionOldVersion(Action):
    """docstring for ActionOldVersion"""
    def __init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, version, solid_args, intTimeout=1.5):
        super().__init__(self, strIP, intTNPort, strPassword,
                 intFTPPort, intTimeout)
        if version == 'vicom':
            self._FTP_username = 'vicomftp'
        elif version == 'vicom':
            self._FTP_username = 'ftpadmin'
        self.solid_args = solid_args

#rewrite function _FTP_connect with alterable FTP username
    def _FTP_connect(self):
        self._FTP_Conn = conn.FTPConn(self._host,
                                      self._FTPport,
                                      self._FTP_username,
                                      self._password,
                                      self._timeout)
        


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
                 intFTPPort, intTimeout=1.5):
        self._host = strIP
        self._TNport = intTNPort
        self._FTPport = intFTPPort
        self._password = strPassword
        self._timeout = intTimeout
        self._TN_Conn = None
        self._FTP_Conn = None
        self._TN_Connect_Status = None
        self._telnet_connect()
        self.AHStatus = self._TN_Conn.is_AH()
        self.strVPD = self._executeCMD('vpd')

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
                                      'adminftp',
                                      self._password,
                                      self._timeout)

    def _ftp(self):
        if self._FTP_Conn:
            connFTP = self._FTP_Conn
        else:
            self._FTP_connect()
            connFTP = self._FTP_Conn
        return connFTP

    @s.deco_Exception
    def change_FW(self, strFWFile):
        connFTP = self._ftp()
        time.sleep(0.25)
        connFTP.PutFile('/mbflash', './', 'fwimage', strFWFile)
        print('FW upgrade completed for {}, waiting for reboot...'.format(
            self._host))

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
