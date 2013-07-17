#!/usr/bin/env python
# I hereby calleth this JKoom
#   JonKelley out of memory
#   Just Kill out of memory
#   Janky killer
#    whatever you wanna call it.

# This is suppose to be an aggressive memory watchdog and killer, with
#  a post exit shell command execution to handle recovery of a service
#   or a message to an ops admin or whatever you want, you code that yourself.

# If you want to sample the heapsize to create a limit for this program to apply constraints towards,
#   you can run pmap -p <PID> | tail -1 | cut -d' ' -f2 | cut -d'K' -f1

import signal, os, sys
import time # time.sleep()
import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/log/jkoom.py.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)
logger.info('** WATCHDOG START **')


import commands # Runs commands.
from optparse import OptionParser # guess

def signalprocess(pid,ksignal):
    """ This will immediately signal a process to die.
        Usage:
        >> signalprocess(pid,"SIGTERM")
        >> signalprocess(pid,15)
    """
    #  From the manpages.
    #       Signal     Value     Action   Comment
    #       -------------------------------------------------------------------------
    #       SIGHUP        1       Term    Hangup detected on controlling terminal
    #                                     or death of controlling process
    #       SIGINT        2       Term    Interrupt from keyboard
    #       SIGQUIT       3       Core    Quit from keyboard
    #       SIGILL        4       Core    Illegal Instruction
    #       SIGABRT       6       Core    Abort signal from abort(3)
    #       SIGFPE        8       Core    Floating point exception
    #       SIGKILL       9       Term    Kill signal
    #       SIGSEGV      11       Core    Invalid memory reference
    #       SIGPIPE      13       Term    Broken pipe: write to pipe with no readers
    #       SIGALRM      14       Term    Timer signal from alarm(2)
    #       SIGTERM      15       Term    Termination signal
    #       SIGUSR1   30,10,16    Term    User-defined signal 1
    #       SIGUSR2   31,12,17    Term    User-defined signal 2
    #       SIGCHLD   20,17,18    Ign     Child stopped or terminated
    #       SIGCONT   19,18,25    Cont    Continue if stopped
    #       SIGSTOP   17,19,23    Stop    Stop process
    #       SIGTSTP   18,20,24    Stop    Stop typed at tty
    #       SIGTTIN   21,21,26    Stop    tty input for background process
    #       SIGTTOU   22,22,27    Stop    tty output for background process

    if not pid:
        raise Exception('No pid defined for killsignal()')

    if type(ksignal) is str:
        if ksignal.lower() == 'SIGHUP':		ksignal = signal.SIGHUP # value 1
        elif ksignal.lower() == 'SIGINT': 	ksignal = signal.SIGINT # value 2
        elif ksignal.lower() == 'SIGQUIT': 	ksignal = signal.SIGQUIT # value 3
        elif ksignal.lower() == 'SIGILL': 	ksignal = signal.SIGILL # value 4
        elif ksignal.lower() == 'SIGABRT':	ksignal = signal.SIGABRT # value 6
        elif ksignal.lower() == 'SIGFPE': 	ksignal = signal.SIGFPE # value 8
        elif ksignal.lower() == 'SIGKILL': 	ksignal = signal.SIGKILL # value 9 # if your process gets out of line, I'll effin kill dash nine!
        elif ksignal.lower() == 'SIGSEGV': 	ksignal = signal.SIGSEGV # value 11
        elif ksignal.lower() == 'SIGPIPE': 	ksignal = signal.SIGPIPE # value 13
        elif ksignal.lower() == 'SIGALRM': 	ksignal = signal.SIGALRM # value 14
        elif ksignal.lower() == 'SIGTERM': 	ksignal = signal.SIGTERM # value 15 # Default killer
        elif ksignal.lower() == 'SIGUSR1': 	ksignal = signal.SIGUSR1 # value 30,10,16
        elif ksignal.lower() == 'SIGUSR2': 	ksignal = signal.SIGUSR2 # value 31.12.17

    if type(ksignal) is int:
        if ksignal == 1:		ksignal = signal.SIGHUP # value 1
        elif ksignal == 2: 	ksignal = signal.SIGINT # value 2
        elif ksignal == 3: 	ksignal = signal.SIGQUIT # value 3
        elif ksignal == 4: 	ksignal = signal.SIGILL # value 4
        elif ksignal == 6:	ksignal = signal.SIGABRT # value 6
        elif ksignal == 8: 	ksignal = signal.SIGFPE # value 8
        elif ksignal == 9: 	ksignal = signal.SIGKILL # value 9 # if your process gets out of line, I'll effin kill dash nine!
        elif ksignal == 11: ksignal = signal.SIGSEGV # value 11
        elif ksignal == 13: ksignal = signal.SIGPIPE # value 13
        elif ksignal == 14: ksignal = signal.SIGALRM # value 14
        elif ksignal == 15: ksignal = signal.SIGTERM # value 15 # Default killer
        elif ksignal == 30 or ksignal == 10 or ksignal == 16: 	ksignal = signal.SIGUSR1 # value 30,10,16
        elif ksignal == 31 or ksignal == 12 or ksignal == 17: 	ksignal = signal.SIGUSR2 # value 31.12.17

    os.kill(pid, ksignal)
    logger.info('Process %s killed by signal %s'%(pid,ksignal))

def thenexec(command):
    """ Covers the use case where you want to call an external script after the killing takes place.
    Maybe for a one liner that emails you. Maybe to recover the service.
    Who knows! You do.
    """
    exitcode, stdout = commands.getstatusoutput(command)
    if exitcode > 0:
        logger.error('Exec failed with exit code %s   Output:' % (str(exitcode), str(stdout)))
    else:
        logger.info('Exec success.   Output: %s' % (str(stdout)))

def ismemoryover(pid,kilomax):
    """  If process memory footprint is over a kilobyte range this function returns true.
            i.e.
                >> ismemoryover(1,200)
                    Returns: TRUE or FALSE depending if memory is over that amount
    """
    stdout = commands.getstatusoutput('pmap -d ' + str(pid) + ' | tail -1 | cut -d\' \' -f2 | cut -d\'K\' -f1')
    # CODEHACK ALERT -- Explanations below.
    # tail -1 == lists last line from pmap
    # cut -d' ' -f2 == cuts view to just be total mapped memory in kilobytes
    # cut -d'K' -f1' == cuts the K off the end of that.

    kilobytes_usage = stdout[1] # first indice is exit status, 1 is our savior

    if int(kilobytes_usage) <= int(kilomax):
        logger.debug('Process heap %sK heap limit %s ismemoryover?%s' % (str(kilobytes_usage),str(kilomax),'False') )
        return False # Usage is less than kilomax
    else:
        logger.debug('Process heap %sK heap limit %s ismemoryover?%s' % (str(kilobytes_usage),str(kilomax),'True') )
        return True

def main(processid,triggeraction,memorythreshold,killsignal,sigkilltimeout,sigkilltimeoutsignal,killscript,loopspeed):
    """ This is the function that actually does the heavy logic
    and loops. Forever.
    """
    processid = int(processid)
    memorythreshold = int(memorythreshold)
    killsignal = int(killsignal)
    sigkilltimeout = int(sigkilltimeout)
    sigkilltimeoutsignal = int(sigkilltimeoutsignal)
    loopspeed = float(loopspeed)
    
    DIE_AT_END_OF_LOOP=False
    while 1: 
        logger.debug('Checking if path %s exists...' % ("/proc/" + str(processid)))
        if not os.path.exists("/proc/" + str(processid)):
            logger.info('Process %s seems dead. ** WATCHDOG EXIT **' % (str(processid)))
            sys.exit(0)
        else:
            if ismemoryover(processid,memorythreshold):
                logger.error('Process %s heap has exceeded %s' % (str(processid),str(memorythreshold)) )
                # If we want to kill...
                if triggeraction == 'kill' or triggeraction == 'killthenexec':
                    logger.info('Process %s scheduled for death' % (str(processid)))
                    signalprocess(processid,killsignal)
                    
                    # Then wait the timeout threshold
                    #   and try with meaner options.
                    if int(sigkilltimeout) > 0:
                        logger.info('Waiting on %s to make sure it dies...' % (str(processid)))
                        time.sleep(sigkilltimeout)
                        # Then kill meanly.
                        if os.path.exists("/proc/" + str(processid)):
                            logger.info('Process %s did not die, scheduling kill signal %s' % (str(processid),str(sigkilltimeoutsignal)) )
                            signalprocess(processid,sigkilltimeoutsignal)
                        else:
                            logger.info('PID %s looks verified dead...' % (str(processid)))
                            DIE_AT_END_OF_LOOP=True
    
                if triggeraction == 'exec' or triggeraction == 'killthenexec':
                    logger.info('Process %s schedule exec: %s' % (str(processid),str(killscript)))
                    thenexec(killscript)
                    # EXEC processid memorythreshold action
                    # TODO because who cares about that for the moment.
        # SLEEP
        #   And then we repeat. Maybe.
        if DIE_AT_END_OF_LOOP:
            logger.info('** WATCHDOG EXIT **')
            sys.exit(0)
        logger.debug('tick')
        time.sleep(loopspeed)



if __name__ == "__main__":
    """ Parser magic.
    Forking magic.
    """
    # do the parser magic first.
    parser = OptionParser()
    parser.add_option("-p", "--pid", dest="processid",
                        help="Process ID to monitor", metavar="pid")
    parser.add_option("-a", "--triggeraction", dest="triggeraction",
                        help="Behavior if memory threshold is met [kill|exec|killthenexec]", metavar="kill|exec|killthenexec")
    parser.add_option("-m", "--memorythreshold", dest="memorythreshold",
                        help="Max allowable memory map, in kilobytes before trigger", metavar="int_in_kilobytes")
    parser.add_option("--killsignal", dest="killsignal",
                        help="If triggeraction kill, what signal to try kill with?", metavar="signal")
    parser.add_option("--sigkill-timeout", dest="sigkilltimeout", default=0,
                        help="If triggeraction kill, what timeout to wait for process death before force signal?", metavar="timeperiod")
    parser.add_option("--sigkill-timeout-sigal", dest="sigkilltimeoutsignal", default=9,
                        help="Reassign default sigkill from 9 to another number.", metavar="signal")
    parser.add_option("--killscript", dest="killscript",
                        help="If triggeraction kill, what timeout to wait for process death before signal 9?", metavar="timeperiod")
    parser.add_option("--loopspeed", dest="loopspeed", default=0.5,
                        help="How fast to check the process? Default is 0.5 seconds.", metavar="seconds")

    (options, args) = parser.parse_args()

#     Check mandatory things are filled in
    if not options.processid:
        print "--pid required man"
        sys.exit(1)
    if not options.memorythreshold:
        print "--memorythreshold required man"
        sys.exit(1)
    if not options.triggeraction:
        print "--triggeraction required man"
        sys.exit(1)

    if options.triggeraction == 'kill' or options.triggeraction == 'killthenexec':
        if not options.killsignal:
            print "Kill signal to use required man"
            sys.exit(1)

    if options.sigkilltimeout > 0:
            if not options.sigkilltimeoutsignal:
                print "Needs --sigkill-timeout-sigal 9 or something to know what to use when the timeout is met."
                sys.exit(1)

    if options.triggeraction == 'exec' or options.triggeraction == 'killthenexec':
        if not options.killscript:
            print "--killscript required to know what to exec man"
            sys.exit(1)
    

#     do the UNIX double-fork magic, see Stevens' "Advanced 
#     Programming in the UNIX Environment" for details on the double fork (ISBN 0201563177)
    try: 
        pid = os.fork() 
        if pid > 0:
#             exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

#     decouple from parent environment
    os.chdir("/") 
    os.setsid() 
    os.umask(0) 

#     do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
#             exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid 
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 

    # start the daemon main loop
    logger.debug('Forked()')
    
    # call main
    main(options.processid,options.triggeraction,
    options.memorythreshold,options.killsignal,
    options.sigkilltimeout,options.sigkilltimeoutsignal,
    options.killscript,options.loopspeed) 
