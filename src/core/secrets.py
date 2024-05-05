from environs import Env

env = Env()
env.read_env()

TOKEN = env.str('TOKEN')  # bot token
CHAT_ID = env.int('CHAT_ID')  # group/channel ID for sending requests to the administrators
CHAT_ID_STATISTIC = env.int('CHAT_ID_STATISTIC')  # group/channel ID for sending statistic
WEBAPPURL = env.str('WEBAPPURL')  # application domain
WEBAPPHOST = env.str('WEBAPPHOST')  # application host
WEBAPPPORT = env.str('WEBAPPPORT')  # application port

DB_PORT = env.str('DB_PORT')  # main (acid) db port
DB_HOST = env.str('DB_HOST')  # db host
DB_USER = env.str('DB_USER')  # db user
DB_PWD = env.str('DB_PWD')  # db password
DB_NAME = env.str('DB_NAME')  # db name
DB_SOCKETPATH = env.str('DB_SOCKETPATH')  # db socketpath
DB_URL = f'mysql+aiomysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'  # db url
# DB_URL = f'mysql+aiomysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?unix_socket={DB_SOCKETPATH}'  # db url with socket

REDIS_PORT = env.str('REDIS_PORT')  # redis db port
MEMCACHE_PORT = env.str('MEMCACHE_PORT')  # memcache port
CACHE_TIME = env.int('CACHE_TIME')  # cache time in seconds
LOG_PATH = env.str('LOG_PATH')  # log dir
LOG_SIZE = env.int('LOG_SIZE')  # size of log files in bytes
N_LOGS = env.int('N_LOGS')  # number of log files
ENCODING = env.str('ENCODING')  # encoding type

YOOKASSA_TOKEN = env.str('YOOKASSA_TOKEN')  # yookassa token

MASTER_ADMIN = env.int('MASTER_ADMIN')  # super admin telegram uid

PHOTO_GALLERY_PATH = env.str('PHOTO_GALLERY_PATH')  # dir where all the media files are stored
PHOTO_EXTENSION = env.str('PHOTO_EXTENSION')  # photo extension (jpg/png etc)
