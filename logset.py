import logging, os
from logging.handlers import TimedRotatingFileHandler

log_dir = os.path.abspath(os.path.join(__file__, '..', 'logs'))
log_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)s %(message)s")

# all log
log_handler = TimedRotatingFileHandler("%s/log" %(log_dir), when="midnight")
log_handler.setFormatter(log_formatter)
log_handler.suffix = "%Y%m%d"
logger = logging.getLogger("")
logger.addHandler(log_handler)
logger.setLevel(logging.NOTSET)
logger.setpropagate = False

# debug.log
debug_log_handler = TimedRotatingFileHandler("%s/debug.log" %(log_dir), when="midnight")
debug_log_handler.setFormatter(log_formatter)
debug_log_handler.suffix = "%Y%m%d"
debug_logger = logging.getLogger("debug")
debug_logger.addHandler(debug_log_handler)
debug_logger.setLevel(logging.DEBUG)
debug_logger.setpropagate = False

# access.log
ACCESS = 100
logging.addLevelName(ACCESS, "ACCESS")
def access(self, message, *args, **kws):
    self.log(ACCESS, message, *args, **kws)
logging.Logger.access = access

access_log_handler = TimedRotatingFileHandler("%s/access.log" %(log_dir), when="midnight")
access_log_handler.setFormatter(log_formatter)
access_log_handler.suffix = "%Y%m%d"
access_logger = logging.getLogger("access")
access_logger.addHandler(access_log_handler)
access_logger.setLevel(ACCESS)
access_logger.setpropagate = False

# error.log
error_log_handler = TimedRotatingFileHandler("%s/error.log" %(log_dir), when="midnight")
error_log_handler.setFormatter(log_formatter)
error_log_handler.suffix = "%Y%m%d"
error_logger = logging.getLogger("error")
error_logger.addHandler(error_log_handler)
error_logger.setLevel(logging.ERROR)
error_logger.setpropagate = False

# info.log
info_log_handler = TimedRotatingFileHandler("%s/info.log" %(log_dir), when="midnight")
info_log_handler.setFormatter(log_formatter)
info_log_handler.suffix = "%Y%m%d"
info_logger = logging.getLogger("info")
info_logger.addHandler(info_log_handler)
info_logger.setLevel(logging.INFO)
info_logger.setpropagate = False
