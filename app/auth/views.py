from flask import render_template, redirect, url_for, request, flash
from . import auth
from .form import LoginForm
from ..models import Teacher, Student,Permission
from flask.ext.login import login_required, login_user, logout_user,session,current_user
from .LoginAction import LoginAction
import os


f = os.popen('ifconfig em1 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
server_ip = f.read().strip('\n')
if not server_ip:
    f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    server_ip = f.read()
server_ip = server_ip + ':5000'
logout_url = 'https://cas.dgut.edu.cn/user/logout?service=http://%s' % server_ip

f = os.popen('ifconfig eth0 | grep "inet\ 地址" | cut -d: -f2 | cut -d" " -f1')
server_ip = f.read().strip('\n')
if not server_ip:
    f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    server_ip = f.read()
server_ip = server_ip + ':5000'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
       teacher = Teacher.query.filter_by(teaId=form.ID.data).first()
#       stu = Student.query.filter_by(stuId=form.ID.data).first()
       if teacher is not None and teacher.password == form.password.data:
           login_user(teacher, form.remember_me.data)
           return render_template('index.html', form=form, Permission=Permission)
           #return redirect(request.args.get('next') or url_for('main.index'))
       flash('账户或密码不正确！')
    return render_template('auth/login.html', form=form, Permission=Permission)



@auth.route('lg',methods=['GET','POST'])
def lg():
    if not current_user.is_authenticated:
        flash('此用户信息暂未录入本系统！')
        return render_template('index.html',Permission=Permission)
    else:
        return redirect(url_for('main.index'))



@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))
    # return redirect('https://cas.dgut.edu.cn/user/logout?service=http://%s' % server_ip)


