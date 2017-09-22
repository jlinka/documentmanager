from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, DateTimeField, SelectField, BooleanField, DateField, \
    validators, FileField
from wtforms.validators import Required, URL, Email
from .. import db



class searchForm(Form):
    key = StringField(validators=[Required(message='请先输入搜索内容')])
    submit = SubmitField('搜索')

class permissionForm(Form):
    roleName = StringField('角色名称', validators=[Required(message='此项不能为空')])
    roleDescribe = TextAreaField('角色描述')
    COM_INFOR_SEARCH = BooleanField('企业信息查看', default=False, description='0X0000009', false_values='0x11')
    COM_INFOR_EDIT = BooleanField('企业信息编辑', default=False, description='0X000000B')
    COM_INFOR_CHECK = BooleanField('企业信息审核', default=False, description='0X000000F')
    INTERNCOMPANY_LIST = BooleanField('实习企业信息列表', default=False, description='0X0000008')
    STU_INTERN_LIST = BooleanField('学生实习信息列表', default=False, description='0X0000010')
    STU_INTERN_SEARCH = BooleanField('学生实习信息查看', default=False, description='0X0000030')
    STU_INTERN_EDIT = BooleanField('学生实习信息编辑', default=False, description='0X0000070')
    STU_INTERN_CHECK = BooleanField('学生实习信息审核', default=False, description='0X00000F0')
    STU_JOUR_SEARCH = BooleanField('学生实习日志查看', default=False, description='0X0000210')
    STU_JOUR_EDIT = BooleanField('学生实习日志编辑', default=False, description='0X0000610')
    STU_JOUR_CHECK = BooleanField('学生实习日志审核', default=False, description='0X0000E10')
    STU_SUM_SEARCH = BooleanField('学生实习总结与成果查看', default=False, description='0X0001010')
    STU_SUM_EDIT = BooleanField('学生实习总结与成果编辑', default=False, description='0X0003010')
    STU_SUM_SCO_CHECK = BooleanField('学生实习总结和成果审核', default=False, description='0X0007010')
    STU_INTERN_MANAGE = BooleanField('学生信息管理', default=False, description='0X0010000')
    TEA_INFOR_MANAGE = BooleanField('老师信息管理', default=False, description='0X0020000')
    PERMIS_MANAGE = BooleanField('权限管理', default=False, description='0X0040000')
    SELECT_MANAGE=BooleanField('下拉框管理',default=False,description='0X0080000')
    UPLOAD_VISIT= BooleanField('上传探访记录',default=False,description='0X0100030')
    submit = SubmitField('提交')



class teaForm(Form):
    teaId = StringField('教工号', validators=[Required(message='此项不能为空')])
    teaName = StringField('姓名', validators=[Required(message='此项不能为空')])
    teaSex = SelectField('性别', choices=[('男', '男'), ('女', '女')], default=' ')
    teaPosition = StringField('职称')
    teaPhone = StringField('联系电话')
    teaEmail = StringField('邮箱')
    submit = SubmitField('提交')

class taskForm(Form):
    taskId = StringField('任务ID', validators=[Required(message='此项不能为空')])
    taskName = StringField('任务名字', validators=[Required(message='此项不能为空')])
    taskTeaId = StringField('任务所属教师ID', validators=[Required(message='此项不能为空')])
    taskTeaName = StringField('任务所属教师名字', validators=[Required(message='此项不能为空')])
    taskDeadline = DateTimeField('任务截至日期', format='%Y-%m-%d', validators=[Required(message='请按 年-月-日 的格式输入正确的日期')])
    taskType = StringField('任务类型', validators=[Required(message='此项不能为空')])
    taskflag = SelectField('任务完成标记', choices=[('已完成', '已完成'), ('未完成', '未完成')], default='未完成')
    taskFile = FileField('批量上传任务列表')
    submit = SubmitField('上传任务')

