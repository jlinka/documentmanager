import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'DGUTSX'
    MAIL_PASSWORD = 'DGUTSX163'
    MAIL_DEFAULT_SENDER = '学生实习系统<dgutsx@163.com>'
    #FLASKY_MAIL_SUBJECT_PREFIX = '[理工]'     #主题前面使修饰
    #FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    #FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    #SERVER_NAME ='dgut.edu.cn'
    MAIL_DEBUG = True
    #FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        #app.url_map.default_subdomain='shixi'
        #app.register_blueprint(public,subdomain='static')
        os.environ.setdefault('DEV_DATABASE_URL','mysql+pymysql://root:mysql@localhost/collecting_master')
	#os.environ.setdefault('DEV_DATABASE_URL','mysql://root:123456@localhost/InternshipSystem')
         # 'mysql+pymysql://intern:intern@172.28.89.13/InternshipSystem')
        # os.environ.setdefault('local_ip', '172.27.33.19')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://root:mysql@localhost/collecting_master'
    #SQLALCHEMY_DATABASE_URI ='mysql://root:123456@localhost/InternshipSystem'

    # 'mysql+pymysql://intern:intern@172.28.89.13/InternshipSystem'

    # os.environ.get('DEV_DATABASE_URL') or \
    # 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
