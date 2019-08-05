# coding:utf-8

from __future__ import print_function
import sys
import SANSW as sw
import HAAP as haap
import Sundry as s
import Monitor as m

try:
    import configparser as cp
except Exception:
    import ConfigParser as cp

import GetConfig as gc

# <<<Get Config Field>>>
setting = gc.Setting()
strCFGFolder = setting.folder_cfgbackup()
strTraceFolder = setting.folder_trace()


# <<<Get Config Field>>>


# <<<Help String Feild>>>
strHelp = '''
        Command   Description

        ptes    : Port error count display for SAN switch(s)('porterrshow')
        ptcl    : Clear port error counter('statsclear' or 'portstatsclear')
        sws     : Print SAN switch info('switchshow')

        gt      : Get trace of HA-AP engine(s)
        at      : Analyse trace of HA-AP engine(s)
        bc      : Backup config for HA-AP engine(s)
        ec      : Execute commands
        fw      : Change firmware for HA-AP engine
        sts     : Show overall status for HA-AP engine(s)
        st      : Sync time with local system
        stm     : Show time now for HA-AP engine(s)

        pc      : Periodically check
        mnt     : Monitor and show status throgh web server
        '''


strPTESHelp = '''
    Show port error of defined pors as table formatted
    ptes <SW_IP> | all   
        SW_IP  - for defined SAN switch
        all    - for all SAN switchs defined in Conf.ini
'''

strPTCLHelp = '''
    Clear port error counter('statsclear' or 'portstatsclear')
    ptcl <SW_IP Port> | all
        SW_IP Port  - for defined port of defined SAN switch
        all         - for all SAN switchs defined in Conf.ini
'''

strSWSHelp = '''
    Print SAN switch connect info('switchshow')
    sws <SW_IP> | all
        SW_IP  - for defined SAN switch
        all    - for all SAN switchs defined in Conf.ini
'''

strFWHelp = '''
    Change firmware for given engine using <FW_File>
    fw <HAAP_IP> <FW_File>
'''

strBCHelp = '''
    Backup config for HA-AP engine(s), save in "{}" folder
    bc <HAAP_IP> | all
        HAAP_IP  - for given HA-AP engine
        all      - for all HA-AP engines defined in Config.ini        
'''.format(strCFGFolder)


strGTHelp = '''
    Get trace of HA-AP engine(s), save in "{}" folder
    gt <HAAP_IP> [Trace_Level] | all [Trace_Level]
        HAAP_IP        - for defined HA-AP engine
        all            - for all HA-AP engines defined in Config.ini
            [Trace_Level]  - option, given or defined
'''.format(strTraceFolder)

# strATHelp = '''
#     Analyse Trace of HA-AP Engine(s), Save in "{}" Folder
#     at <HAAP_IP> [Trace_Level] | all [Trace_Level]
#         HAAP_IP        - for defined HA-AP Engine
#         all            - for All HA-AP Engines Defined in Conf.ini
#             [Trace_Level]  - Option, Given or Defined        
# '''.format(strTraceFolder)

strATHelp = '''
    Analyse given trace of HA-AP engine(s) in folder <Trace_Folder>
    at <Trace_Folder>
'''

strECHelp = '''
    Execute commands listed in <Command_File> on given engine
    ec <HAAP_IP> <Command_File>
'''

strSTSHelp = '''
    sts <HAAP_IP> | all
        HAAP_IP  - for given HA-AP engine
        all      - for all HA-AP engines defined in Config.ini        
'''

strSTHelp = '''
    st <HAAP_IP> | all
        HAAP_IP  - for given HA-AP engine
        all      - for all HA-AP engines defined in Config.ini        
'''

strSTMHelp = '''
    stm <HAAP_IP> | all
        HAAP_IP  - for given HA-AP engine
        all      - for all HA-AP engines defined in Config.ini
'''

strPCHelp = '''
    Periodically check for HA-AP engine(s) or SAN switch(s)
    pc <sw [SW_IP]|haap [HAAP_IP]> | all
        sw SW_IP      - for given HA-AP engine
        haap HAAP_IP  - for given HA-AP engine
        all           - for all HA-AP engines and SAN switches
'''

strMNTHelp = '''
    Show status through web page
    mnt rt | db
        rt  - Get status real time
        db  - Get status from db(Need MongoDB)
'''

# <<<Help String Field>>>


def main():
    if len(sys.argv) == 1:#用户输入参数是否是本身，如果是
        print(strHelp)#打印帮助
    #OK
    elif sys.argv[1] == 'ptes':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strPTESHelp)
        elif sys.argv[2] == 'all':
            sw.print_porterror_all_formated()
        else:
            if s.is_IP(sys.argv[2]):
                sw.print_porterror_formated(sys.argv[2])
            else:
                print('Please provide correct switch ip...')
    #OK
    elif sys.argv[1] == 'ptcl':#判断执行参数是否为ptcl
        num_argv = len(sys.argv)  #获取参数的个数
        if num_argv == 2 or num_argv > 4:#如果是2个或者大于4个
            print(strPTCLHelp) #打印提示信息
        elif sys.argv[2] == 'all': #如果是3个参数是 all
            sw.clear_all() #调用清除所有交换机端口错误函数
        elif s.is_IP(sys.argv[2]):#如果第3个参数是ip的话,判断是不是ip
            if num_argv == 4:   #判断是否有第4个参数，如果有
                #if _isPort(sys.argv[3]):   错误
                if s.is_port(sys.argv[3]):   #在判断第4个参数是否是正确的端口      
                    sw.clear_one_port(sys.argv[2], sys.argv[3])#调用清除具体ip，端口错误
                else:
                    print('Please provide correct port number...') #请提供正确端口号
            else:
                print(strPTCLHelp) #打印提示
        else:
            print('Please provide correct switch ip...')#请提供正确的交换机ip
    #OK
    elif sys.argv[1] == 'sws':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSWSHelp)
        elif sys.argv[2] == 'all':
            sw.print_switchshow_all()
        else:
            if s.is_IP(sys.argv[2]):
                sw.print_switchshow(sys.argv[2])
            else:
                print('Please provide correct switch ip...')

    #OK
    elif sys.argv[1] == 'bc':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strBCHelp)
        elif sys.argv[2] == 'all':
            haap.backup_config_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.backup_config(sys.argv[2])
            else:
                print('Please provide correct engine ip...')

    # get engines' trace files under TraceFolder based on Trace levels
    #trace、primary、seaond
    #OK git Trace   NOT have Primary
    elif sys.argv[1] == 'gt':
        num_argv = len(sys.argv)
        if num_argv > 3:
            trace_level = int(sys.argv[3])
        if num_argv == 2 or num_argv > 4:
            print(strGTHelp)
        elif sys.argv[2] == 'all':
            if num_argv > 3:
                if s.is_trace_level(trace_level):
                    haap.get_trace_all(trace_level)
                else:
                    print('Trace level must be "1" or "2" or "3"')
            else:
                haap.get_trace_all(0)
        elif s.is_IP(sys.argv[2]):
            if num_argv > 3:
                if s.is_trace_level(trace_level):
                    haap.get_trace(sys.argv[2], trace_level)
                else:
                    print('Trace level must be "1" or "2" or "3"')
            else:
                haap.get_trace(sys.argv[2], 0)
        else:
            print('Please provide correct engine ip...')

    # elif sys.argv[1] == 'at':
    #     num_argv = len(sys.argv)
    #     if num_argv > 3:
    #         trace_level = sys.argv[3]
    #     if num_argv == 2 or num_argv > 4:
    #         print(strPTCLHelp)
    #     elif sys.argv[2] == 'all':
    #         if num_argv > 3:
    #             if s.is_trace_level(trace_level):
    #                 haap.analyse_trace_all(trace_level)
    #             else:
    #                 print('Trace Level Must Be "1" or "2" or "3"')
    #         else:
    #             haap.analyse_trace_all(0)
    #     elif s.is_IP(sys.argv[2]):
    #         if num_argv > 3:
    #             if s.is_trace_level(trace_level):
    #                 haap.analyse_trace(sys.argv[2], trace_level)
    #             else:
    #                 print('Trace Level Must Be "1" or "2" or "3"')
    #         else:
    #             haap.analyse_trace(sys.argv[2], 0)
    #     else:
    #         print('Please Provide Correct Engine IP...')
    #OK python Main.py at Trace\2019-00-00
    elif sys.argv[1] == 'at':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strATHelp)
        else:
            if s.is_folder(sys.argv[2]):
                s.TraceAnalyse(sys.argv[2])
            else:
                print('Please provide correct trace folder')
    #OK  python Main.py ec 10.203.1.223 cmd.txt
    elif sys.argv[1] == 'ec':
        if len(sys.argv) != 4:
            print(strECHelp)
        else:
            ip = sys.argv[2]
            command_file = sys.argv[3]
            if not s.is_IP(ip):
                print('Please provide correct engine ip...')
            if not s.is_file(command_file):
                print('File not exists. please provide correct file...')
            haap.execute_multi_commands(ip, command_file)
    #OK  python Main.py fw 10.203.1.223 FW15.9.7.7_OR.bin
    elif sys.argv[1] == 'fw':
        if len(sys.argv) != 4:
            print(strFWHelp)
        else:
            ip = sys.argv[2]
            fw_file = sys.argv[3]
            if not s.is_IP(ip):
                print('Please provide correct engine ip...')
            if not s.is_file(fw_file):
                print('File not exists. please provide correct file...')
            haap.change_firmware(ip, fw_file)
    #OK-
    elif sys.argv[1] == 'sts':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTSHelp)
        elif sys.argv[2] == 'all':
            haap.show_stauts_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.show_stauts(sys.argv[2])
            else:
                print('Please provide correct engine ip...')
    #OK
    elif sys.argv[1] == 'st':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTHelp)
        elif sys.argv[2] == 'all':
            haap.set_time_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.set_time(sys.argv[2])
            else:
                print('Please provide correct engine ip...')
    #OK    
    elif sys.argv[1] == 'stm':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 3:
            print(strSTMHelp)
        elif sys.argv[2] == 'all':
            haap.show_time_all()
        else:
            if s.is_IP(sys.argv[2]):
                haap.show_time(sys.argv[2])
            else:
                print('Please provide correct engine ip...')
    #OK
    elif sys.argv[1] == 'pc':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 4:
            print(strPCHelp)
#             print(strPTCLHelp) 原
        elif num_argv > 2:
            if sys.argv[2] == 'all':
                haap.periodically_check_all()
                sw.periodically_check_all()
            elif sys.argv[2] == 'haap':
                if num_argv == 3:
                    haap.periodically_check_all()
                elif num_argv > 3:
                    if s.is_IP(sys.argv[3]):
                        haap.periodically_check(sys.argv[3])
                    else:
                        print('Please provide correct engine ip...')
            elif sys.argv[2] == 'sw':
                if num_argv == 3:
                    sw.periodically_check_all()
                elif num_argv > 3:
                    if s.is_IP(sys.argv[3]):
                        sw.periodically_check(sys.argv[3])
                    else:
                        print('Please provide correct SAN switch ip...')
            else:
                print(strPCHelp)
    #OK
    elif sys.argv[1] == 'mnt':
        num_argv = len(sys.argv)
        if num_argv == 2 or num_argv > 4:
            print(strMNTHelp)
        elif sys.argv[2] == 'rt':
            m.monitor_rt_1_thread()
        elif sys.argv[2] == 'db':
            m.monitor_db_4_thread()
        else:
            print('rt(realtime) or db(datarase)')

    else:
        print(strHelp)


if __name__ == '__main__':
    main()
