# -*- coding: utf-8 -*-

from flask import render_template, url_for, flash, redirect, request, session, send_file
from .form import searchForm, permissionForm,taskForm
from . import main
from ..models import Permission,  Student, Role, Teacher, \
    not_student_login,Grade,Task

from flask.ext.login import current_user, login_required
from .. import db
from sqlalchemy import func, desc, and_, distinct
from datetime import datetime, timedelta, date
import xlwt, xlrd, os, random, subprocess, re,shutil
from collections import OrderedDict
from werkzeug.utils import secure_filename
from sqlalchemy.orm import aliased
from ..auth.views import logout_url
import time





# 系统角色列表
@main.route('/roleList', methods=['GET', 'POST'])
@login_required
def roleList():
    # 非管理员,不能进入
    if not current_user.can(Permission.PERMIS_MANAGE):
        return redirect('/')
    page = request.args.get('page', 1, type=int)
    pagination = Role.query.paginate(page, per_page=100, error_out=False)
    role = pagination.items
    return render_template('roleList.html', Permission=Permission, role=role, pagination=pagination)


# 添加角色,靠你们改善这个蠢方法了,\r\n不能换行，导致角色列表里的describe不能显全
@main.route('/addRole', methods=['GET', 'POST'])
@login_required
def addRole():
    form = permissionForm()
    a = 0
    if form.validate_on_submit():
        # 生成角色权限
        if form.SELECT_MANAGE.data:
            a = eval(form.SELECT_MANAGE.description) | a

        per = hex(a)
        # print(per)
        # describe = ''.join(p)
        # print(describe)
        id = getMaxRoleId() + 1
        role = Role(roleName=form.roleName.data, roleDescribe=form.roleDescribe.data, permission=per, roleId=id)
        try:
            db.session.add(role)
            db.session.commit()
            flash('添加系统角色成功！')
            return redirect(url_for('.roleList'))
        except Exception as e:
            flash('添加系统角色失败！请重试。。。')
            print('添加系统角色：', e)
            db.session.rollback()
            return redirect(url_for('.addRole'))
    return render_template('addRole.html', Permission=Permission, form=form)


# 删除角色
@main.route('/role_delete', methods=['GET', 'POST'])
@login_required
def role_delete():
    if request.method == 'POST':
        try:
            db.session.execute('delete from Role where roleId=%s' % request.form.get('roleId'))
            flash('删除成功！')
            return redirect(url_for('.roleList'))
        except Exception as e:
            print('删除角色：', e)
            flash('删除失败，请重试！')
            db.session.rollback()
            return redirect(url_for('.roleList'))






# 编辑角色
@main.route('/editRole', methods=['GET', 'POST'])
@login_required
def editRole():
    form = permissionForm()
    roleId = request.args.get('roleId')
    role = Role.query.filter_by(roleId=roleId).first()
    if request.method == 'POST':
        a = 0
        # 生成角色权限


        if form.SELECT_MANAGE.data:
            a = eval(form.SELECT_MANAGE.description) | a

        per = hex(a)
        role.roleName = form.roleName.data
        role.roleDescribe = request.form.get('roleDescribe')
        role.permission = per
        try:
            db.session.add(role)
            db.session.commit()
            flash('修改成功！')
            return redirect(url_for('.roleList'))
        except Exception as e:
            db.session.rollback()
            flash('修改失败，请重试！')
            print('修改角色', e)
            return redirect(url_for('.editRole', roleId=roleId))
    return render_template('editRole.html', Permission=Permission, role=role, form=form)


# 查询最大的角色Id
def getMaxRoleId():
    res = db.session.query(func.max(Role.roleId).label('max_roleId')).one()
    return res.max_roleId




# ---------------Excel表格导入导出-----------------------------------------------

# Excel文档列名的模板. 导入和导出

#任务列表
excel_export_Task = OrderedDict((('taskId', '任务Id'), ('taskName', '任务名称'), ('taskType', '任务类型'),
                                ('teaId', '教师Id'), ('deadline',' 截至日期')))
excel_import_Task = {'taskName': '任务名称', 'taskType': '任务类型', 'taskTeaName':'任务所属教师', 'deadline': '截至日期'}


#学生名单列表
excel_export_Student = OrderedDict((('stuId','学号'), ('stuName','学生姓名'), ('teaId', '教师Id'), ('flag', '标记有无上交')))
excel_import_Student = {'stuId': '学号', 'stuName': '学生姓名', 'teaName': '教师姓名'}


IMPORT_FOLDER = os.path.join(os.path.abspath('.'), 'file_cache/xls_import')
EXPORT_FOLDER = os.path.join(os.path.abspath('.'), 'file_cache/xls_export')
IMPORT_TEMPLATE_FOLDER = os.path.join(os.path.abspath('.'), 'file_cache/import_template')
EXPORT_ALL_FOLDER = os.path.join(os.path.abspath('.'), 'file_cache/all_export')
VISIT_EXPORT_ALL_FOLDER = os.path.join(os.path.abspath('.'), 'file_cache/visit_export')

# 导入excel表, 检查数据是否完整或出错
EXCEL_IMPORT_CHECK_TASK = [ 'taskName', 'taskType', 'taskTeaName', 'deadline']
EXCEL_IMPORT_CHECK_STUDENT = [ 'stuId', 'stuName', 'teaName']

# 可加上成果的上传文件格式限制
# ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])


def allowed_file(filename, secure_postfix):
    return '.' in filename and filename.rsplit('.', 1)[1] in secure_postfix


@main.route('/oneTaskupload', methods=['GET', 'POST'])
@login_required
def oneTaskupload():
    taskform = taskForm()
    try:
        if request.method == 'POST':
            taskTeaName = request.form.get('taskTeaName')
            task = Task(
                taskName=request.form.get('taskName'),
                taskType=request.form.get('taskType'),
                teaId=Teacher.query.filter_by(teaName=taskTeaName).first().teaId,
                deadline=datetime.strptime(request.form.get('taskDeadline'), '%Y-%m-%d').date()
            )


            try:
                db.session.add(task)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("任务信息：", e)
                flash('添加任务信息失败，请重试！')
                return redirect('/')
            db.session.commit()
            flash('提交任务信息成功！')
            return redirect(url_for('.taskUpload', flag=5))
    except Exception as e:
        print("任务信息：", e)
        db.session.rollback()
        flash('提交任务信息失败，请重试！')
        return redirect(url_for('.oneTaskupload'))
    return render_template('oneTaskupload.html', taskform=taskform,
                           Permission=Permission)

@main.route('/batchTaskupload', methods=['GET', 'POST'])
@login_required
def batchTaskupload():
    from_url = request.args.get('from_url')
    temp_dict = {
        'taskList':
            {'file_name': 'taskList_import_template.xlsx', 'attach_name': '任务批量导入模板.xlsx'}


    }
    if from_url == 'taskUpload':
        permission = current_user.can(Permission.PERMIS_MANAGE)
    print(from_url)
    if request.method == 'POST':
        # 模板下载
        import_template_download = request.form.get('import_template_download')
        now = datetime.now().date()
        if import_template_download:
            file_path = os.path.join(IMPORT_TEMPLATE_FOLDER, temp_dict[from_url]['file_name'])
            attach_name = temp_dict[from_url]['attach_name']
            return send_file(file_path, as_attachment=True, attachment_filename=attach_name.encode('utf-8'))
            # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        print("333333")
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename, ['xls', 'xlsx']):
            filename = '%s_import_%s.xls' % (from_url, random.randint(1, 99))
            print("111111")
            file.save(os.path.join(IMPORT_FOLDER, filename))
            print("222222")
            # 上传成功,开始导入
            try:
                if from_url == "taskList":

                    tasklist = excel_import(os.path.join(IMPORT_FOLDER, filename), excel_import_Task,
                                EXCEL_IMPORT_CHECK_TASK, from_url)
                    print(tasklist)
                if tasklist is False:
                    return redirect('/')
                print("444444")

                for task, col in zip(tasklist, range(len(tasklist))):
                    print(task['taskName'])
                    print(task['deadline'])
                    deadline=task['deadline']
                    task = Task(
                        taskName=task['taskName'],
                        taskType=task['taskType'],
                        teaId=Teacher.query.filter_by(teaName=task['taskTeaName']).first().teaId,
                        deadline=deadline
                    )
                    db.session.add(task)
                    db.session.commit()
                    flash("任务导入成功")
            except Exception as e:
                # flash('导入出现异常:%'% str(e))
                if str(e) == '部分数据有误, 请重新填写':
                    flash('部分数据有误, 请重新填写')
                else:
                    flash('导入失败')
                    print(from_url, '导入出现异常:', e)
                    db.session.rollback()
                    return redirect('/')
    return render_template('batchTaskupload.html', Permission=Permission)

@main.route('/taskUpload', methods=['GET', 'POST'])
@login_required
def taskUpload():
    # 非管理员,不能进入
    if not current_user.can(Permission.PERMIS_MANAGE):
        return redirect('/')
    page = request.args.get('page', 1, type=int)
    pagination = Role.query.paginate(page, per_page=100, error_out=False)
    role = pagination.items
    return render_template('taskUpload.html', Permission=Permission, role=role, pagination=pagination)


@main.route('/stuListUpload', methods=['GET', 'POST'])
@login_required
def stuListUpload():
    from_url = request.args.get('from_url')
    print(from_url)
    temp_dict = {
        'stuList':
            {'file_name': 'stuList_import_template.xlsx', 'attach_name': '学生导入模板.xlsx'}

    }
    print(from_url)
    if request.method == 'POST':
        # 模板下载
        import_template_download = request.form.get('import_template_download')
        now = datetime.now().date()
        if import_template_download:
            file_path = os.path.join(IMPORT_TEMPLATE_FOLDER, temp_dict[from_url]['file_name'])
            attach_name = temp_dict[from_url]['attach_name']
            return send_file(file_path, as_attachment=True, attachment_filename=attach_name.encode('utf-8'))
            # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        print("333333")
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('/')
        if file and allowed_file(file.filename, ['xls', 'xlsx']):
            filename = '%s_import_%s.xls' % (from_url, random.randint(1, 99))
            print("111111")
            file.save(os.path.join(IMPORT_FOLDER, filename))
            print("222222")
            # 上传成功,开始导入
            try:
                if from_url == "stuList":
                    stulist = excel_import(os.path.join(IMPORT_FOLDER, filename), excel_import_Student,
                                            EXCEL_IMPORT_CHECK_STUDENT, from_url)
                    print(stulist)
                    if stulist is False:
                        return redirect('/')

                    for student, col in zip(stulist, range(len(stulist))):

                        student = Student(
                            stuId=student['stuId'],
                            stuName=student['stuName'],
                            teaId=Teacher.query.filter_by(teaName=student['teaName']).first().teaId
                        )
                        db.session.add(student)
                        db.session.commit()
                        flash("任务导入成功")
            except Exception as e:
                # flash('导入出现异常:%'% str(e))
                if str(e) == '部分数据有误, 请重新填写':
                    flash('部分数据有误, 请重新填写')
                else:
                    flash('导入失败')
                    print(from_url, '导入出现异常:', e)
                    db.session.rollback()
                    return redirect('/')
    return render_template('stuListUpload.html', Permission=Permission)

# 下载导出文件
def export_download(file_path):
    template_dict = {'internlist':'实习信息导出表', 'comlist':'企业信息导出表', 'stuUserList':'学生用户信息导出表', 'teaUserList':'教师用户信息导出表', 'journalList':'日志记录导出表'}
    file_name = os.path.basename(file_path)
    index = file_name.split('_')[0]
    if index in template_dict.keys():
        file_attachname = template_dict[index] + '_%s.xls' % datetime.now().date()
    # attachment_finaname为下载时,提供的默认文件名
    return send_file(file_path, as_attachment=True, attachment_filename=file_attachname.encode('utf-8'))


# 导入Excel
def excel_import(file, template, check_template, from_url):
    book = xlrd.open_workbook(file)
    data = []
    for sheet in range(book.nsheets):
        sh = book.sheet_by_index(sheet)
        if(from_url=="taskList"):
            col_name = ['taskName', 'taskType', 'taskTeaName', 'deadline']
            for col in range(sh.ncols):
                # 如果template里面没找到对应的key,则为None. 所在列的数据也不会录入
                temp = template.get(sh.cell_value(rowx=0, colx=col))
                if temp in excel_import_Task.values() and temp in col_name:
                    flash('导入失败: 部分信息有重复, 请使用提供的模板来写入数据')
                    print('导入失败: 部分信息有重复, 请使用提供的模板来写入数据')
                    return False
                col_name.append(temp)
            print("555555")
            # 检查列名是否有错
            for x in check_template:
                # print ('template[x]', template[x])
                if x not in col_name:
                    flash('导入失败: 部分必需信息缺失,请使用提供的模板来写入数据')
                    print('导入失败: 部分必需信息缺失,请使用提供的模板来写入数据'+x)
                    # return redirect('/')
                    return False
            for row in range(sh.nrows - 1):
                # 导入数据
                data_row = {}
                for col in range(sh.ncols):
                    if col_name[col]:
                        # excel的日期类型数据会返回float, 此处修改为string
                        if col_name[col] == 'deadline':
                            data_row[col_name[col]] = datetime(*xlrd.xldate_as_tuple(sh.cell_value(rowx=row + 1, colx=col), book.datemode)).date()
                            print(data_row[col_name[col]])
                            # data_row[col_name[col]] = str(datetime(*xlrd.xldate_as_tuple(sh.cell_value(rowx=row + 1, colx=col), book.datemode)).date())
                        else:
                            data_row[col_name[col]] = str(sh.cell_value(rowx=row + 1, colx=col))

                # 检查每行的必要数据是否存在
                for x in check_template:
                    # excel的空白默认为6个' '?
                    if x not in ['deadline']:
                        if data_row.get(x).strip() is '':
                            flash('导入失败:有不完整或格式不对的数据,请修改后再导入')
                            print('导入失败:有不完整或格式不对的数据,请修改后再导入')
                            return False
                data.append(data_row)
        if (from_url == "stuList"):
            col_name = ['stuId', 'stuName', 'teaName']
            for col in range(sh.ncols):
                # 如果template里面没找到对应的key,则为None. 所在列的数据也不会录入
                temp = template.get(sh.cell_value(rowx=0, colx=col))
                if temp in excel_import_Student.values() and temp in col_name:
                    flash('导入失败: 部分信息有重复, 请使用提供的模板来写入数据')
                    print('导入失败: 部分信息有重复, 请使用提供的模板来写入数据')
                    return False
                col_name.append(temp)
            print("555555")
            # 检查列名是否有错
            for x in check_template:
                # print ('template[x]', template[x])
                if x not in col_name:
                    flash('导入失败: 部分必需信息缺失,请使用提供的模板来写入数据')
                    print('导入失败: 部分必需信息缺失,请使用提供的模板来写入数据' + x)
                    # return redirect('/')
                    return False
            for row in range(sh.nrows - 1):
                # 导入数据
                data_row = {}
                for col in range(sh.ncols):
                    if col_name[col]:
                        # excel的日期类型数据会返回float, 此处修改为string
                        if col_name[col] == 'deadline':
                            data_row[col_name[col]] = datetime(
                                *xlrd.xldate_as_tuple(sh.cell_value(rowx=row + 1, colx=col), book.datemode)).date()
                            print(data_row[col_name[col]])
                            # data_row[col_name[col]] = str(datetime(*xlrd.xldate_as_tuple(sh.cell_value(rowx=row + 1, colx=col), book.datemode)).date())
                        else:
                            data_row[col_name[col]] = str(sh.cell_value(rowx=row + 1, colx=col))

                # 检查每行的必要数据是否存在
                for x in check_template:
                    # excel的空白默认为6个' '?
                    if x not in ['deadline']:
                        if data_row.get(x).strip() is '':
                            flash('导入失败:有不完整或格式不对的数据,请修改后再导入')
                            print('导入失败:有不完整或格式不对的数据,请修改后再导入')
                            return False
                data.append(data_row)
    return data


# 导入的Excel中, 统一将长串的float类型改为str
# 适用于学号,电话号码
def float2str(float_id):
    print (float_id)
    if re.match(r'.*\..*', float_id):
        str_id = str(float_id[:-2])
        print ('1', str_id)
    else:
        str_id = float_id
        print ('2', str_id)
    return str_id






