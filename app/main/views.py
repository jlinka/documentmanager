# -*- coding: utf-8 -*-

from flask import render_template, url_for, flash, redirect, request, session, send_file
from .form import searchForm, permissionForm
from . import main
from ..models import Permission,  Student, Role, Teacher, \
    not_student_login,Grade

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



