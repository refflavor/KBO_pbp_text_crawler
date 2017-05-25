# logManager.py

import logging
import logging.config
import logging.handlers
import os
import inspect

formatter = logging.Formatter(fmt='[%(asctime)s.%(msecs)03d %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')


class LogManager:
    def __init__(self, name=None):
        # main 에서 처음 실행할 때 호출
        # log directory 를 세팅하기 위해 사용
        if name is not None:
            assert isinstance(name, str)
            self.logger = logging.getLogger(name)
        else:
            self.logger = logging.getLogger('LogManager')

        self.logPath = '{}/log/'.format(os.getcwd())
        self.logFileName = 'base.log'

        # set root logger level
        logging.getLogger().setLevel(logging.DEBUG)

        # set my logger level
        self.logger.setLevel(logging.DEBUG)

    def setLogPath(self, lp=''):
        if lp is not '':
            self.logPath = lp
        # omit last slash in path
        if self.logPath[-1] == '/':
            self.logPath = self.logPath[:-1]

    def setLogFileName(self, name='base.log'):
        if name is not '':
            self.logFileName = name

    def createLogHandler(self):
        if not os.path.isdir(self.logPath):
            os.mkdir(self.logPath)

        file_handler =\
            logging.handlers.RotatingFileHandler('{}/{}'.format(self.logPath, self.logFileName),
                                                 encoding='utf-8', maxBytes=1024*10,
                                                 backupCount=20)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def killLogManager(self):
        logging.shutdown()

    def log(self, msg):
        assert isinstance(msg, str)
        message = 'in {} at {}:{}] > {}'.format(inspect.stack()[1].function,
                                                os.path.basename(inspect.stack()[1].filename),
                                                inspect.stack()[1].lineno,
                                                msg)
        self.logger.debug(message)

    def cleanLog(self):
        # 로그 파일 열기 전에 수행해야 함
        # setLogFilePath 이전에 수행해야 함
        if os.path.isdir(self.logPath):
            if os.listdir(self.logPath) is not None:
                files = [f for f in os.listdir(self.logPath)]
                for f in files:
                    elem = self.logPath.split('/')
                    if len(elem) == 1:
                        os.remove(os.path.join(self.logPath, f))
                    else:
                        cp = ''
                        for e in elem:
                            cp = os.path.join(cp, e)
                        os.remove(os.path.join(cp, f))