from . import db
from flask.ext.login import UserMixin
from . import login_manager
from datetime import datetime


# 装饰器not_student_login 所需要的模块
from functools import wraps
from flask import _request_ctx_stack, abort, current_app, flash, redirect, request, session, url_for, \
    has_request_context
from flask.ext.login import current_user


# 此装饰器用于学生没有权限访问的页面
def not_student_login(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif current_user.roleId == 0:
            return redirect('/')
        return func(*args, **kwargs)

    return decorated_view


@login_manager.user_loader
def load_user(Id):
    return Teacher.query.get(Id) or Student.query.get(Id)

class Task(db.Model, UserMixin):
    __tablename__ = 'Task'
    taskId = db.Column(db.Integer,primary_key=True)
    taskName = db.Column(db.String(20))
    taskType = db.Column(db.Integer)
    teaId = db.Column(db.String(20))
    deadline = db.Column(db.Date)

class Role(db.Model):
    __tablename__ = 'Role'
    roleId = db.Column(db.Integer, primary_key=True)
    roleName = db.Column(db.String(5), unique=True)
    permission = db.Column(db.String(8), unique=True)
    # backref='role'可代替Teacher的roleId
    roleDescribe = db.Column(db.String(200))
    teacher = db.relationship('Teacher', backref='role', lazy='dynamic')
    student = db.relationship('Student', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    # 对角色进行权限判断
    @staticmethod
    def can(role, permissions):
        if role.permission is not None:
            p = eval(role.permission)
        return (p & permissions) == permissions


class Teacher(db.Model, UserMixin):
    __tablename__ = 'Teacher'
    teaId = db.Column(db.String(10), primary_key=True)
    teaName = db.Column(db.String(4), index=True)
    teaSex = db.Column(db.String(2))
    roleId = db.Column(db.Integer, db.ForeignKey('Role.roleId'), default=1)
    password = db.Column(db.String(10))
    teaPosition = db.Column(db.String(20))
    teaPhone = db.Column(db.String(15))
    teaEmail = db.Column(db.String(20))

    def get_id(self):
        return self.teaId

    # 对教师用户进行权限判断
    def can(self, permissions):
        if self.role.permission is not None:
            p = eval(self.role.permission)
        return (p & permissions) == permissions

    def __repr__(self):
        return '<Teacher %r>' % self.teaName

    # 创建大量虚拟信息
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint, choice
        import forgery_py

        seed()
        for i in range(count):
            teacher = Teacher(
                teaId=randint(20000000, 20160000),
                teaName=forgery_py.internet.user_name(True),
                teaSex=choice(['男', '女']),
                password='123')
            db.session.add(teacher)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()



class Student(db.Model, UserMixin):
    __tablename__ = 'Student'
    stuId = db.Column(db.String(20), primary_key=True)
    stuName = db.Column(db.String(20), index=True)
    teaId = db.Column(db.String(20))
    roleId = db.Column(db.Integer, db.ForeignKey('Role.roleId'), default=0)
    password = db.Column(db.String(10))
    #internshipinfor = db.relationship('InternshipInfor', backref='student', lazy='dynamic')



    def get_id(self):
        return self.stuId

    # 对学生用户进行权限判断
    def can(self, permissions):
        if self.role.permission is not None:
            p = eval(self.role.permission)
        return (p & permissions) == permissions

    def __repr__(self):
        return '<Student %r>' % self.stuName

    # 创建大量虚拟信息
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint, choice
        import forgery_py

        seed()
        for i in range(count):
            student = Student(
                stuId=randint(201300000000, 201600000000),
                stuName=forgery_py.internet.user_name(True),
                institutes='计算机与网络安全学院',
                # institutes='计算机学院',
                major=choice(['计算机科学与技术', '网络工程', '软件工程', '信息科学与技术']),
                grade=choice([2013, 2014, 2015, 2016]),
                classes=randint(1, 10),
                sex=choice(['男', '女']),
                password='123'
            )
            db.session.add(student)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()




class Grade(db.Model):
    __tablename__='Grade'
    grade=db.Column(db.Integer, primary_key=True)


class Permission:

    # 权限管理
    PERMIS_MANAGE = 0X0040000



