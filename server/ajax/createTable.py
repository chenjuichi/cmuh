from flask import Blueprint, jsonify, request
from sqlalchemy import func
from database.tables import User, Permission, Department, OutTag, InTag, Setting, Session

from werkzeug.security import generate_password_hash

createTable = Blueprint('createTable', __name__)


# ------------------------------------------------------------------

# create user data and perm.id=1 into table
@createTable.route("/register", methods=['POST'])
def register():
    print("register....")
    request_data = request.get_json()

    emp_id = (request_data['emp_id'] or '')
    emp_name = (request_data['emp_name'] or '')
    sPWD = (request_data['password'] or '')  # convert null into empty string

    return_value = True  # true: 資料正確, 註冊成功
    if emp_id == "" or emp_name == "" or sPWD == "":
        return_value = False  # false: 資料不完全 註冊失敗

    dep = (request_data['dep'] or '')  # convert null into empty string
    #code = request_data['perm_id']

    s = Session()
    department = s.query(Department).filter_by(dep_name=dep).first()
    if not department:
        return_value = False  # if the user's department does not exist

    #permission = s.query(Permission).filter_by(auth_code=code).first()
    # if not permission:
    #    return_value = False  # if the user's permission does not exist

    old_user = s.query(User).filter_by(emp_id=emp_id).first()
    if old_user:
        return_value = False  # if the user exist

    if return_value:
        #kk_setting = Setting(message='hello ' + emp_name)
        new_user_setting = Setting(
            message='hello ' + emp_name,)
        s.add(new_user_setting)
        s.flush()
        new_user = User(emp_id=emp_id,
                        emp_name=emp_name,
                        password=generate_password_hash(sPWD, method='sha256'),
                        dep_id=department.id,
                        # perm_id=permission.id,
                        perm_id=1,  # first permission,auth_code=0:none
                        setting_id=new_user_setting.id,)
        s.add(new_user)

        s.commit()

    s.close()

    return jsonify({
        'status': return_value,
    })

# create user data and perm.id=4 into table


@createTable.route("/createUser", methods=['POST'])
def createUser():
    print("createUser....")
    request_data = request.get_json()

    emp_id = (request_data['emp_id'] or '')
    emp_name = (request_data['emp_name'] or '')
    sPWD = (request_data['password'] or '')  # convert null into empty string

    return_value = True  # true: 資料正確, 註冊成功
    if emp_id == "" or emp_name == "" or sPWD == "":
        return_value = False  # false: 資料不完全 註冊失敗

    dep = (request_data['dep'] or '')  # convert null into empty string
    #code = request_data['perm_id']

    s = Session()
    department = s.query(Department).filter_by(dep_name=dep).first()
    if not department:
        return_value = False  # if the user's department does not exist

    #permission = s.query(Permission).filter_by(auth_code=code).first()
    # if not permission:
    #    return_value = False  # if the user's permission does not exist

    old_user = s.query(User).filter_by(emp_id=emp_id).first()
    if old_user:
        return_value = False  # if the user exist

    if return_value:
        new_user_setting = Setting(
            message='add ' + emp_name,)
        s.add(new_user_setting)
        s.flush()
        new_user = User(emp_id=emp_id,
                        emp_name=emp_name,
                        password=generate_password_hash(sPWD, method='sha256'),
                        dep_id=department.id,
                        # perm_id=permission.id,
                        perm_id=4,  # first permission,auth_code=0:none
                        setting_id=new_user_setting.id,)
        s.add(new_user)
        s.commit()

    s.close()

    return jsonify({
        'status': return_value,
    })


# create department data into table
@createTable.route("/createDepartment", methods=['POST'])
def create_department():
    print("createDepartment....")
    request_data = request.get_json()

    _emp_dep = (request_data['emp_dep'] or '')

    return_value = True  # true: 資料正確, 註冊成功
    if _emp_dep == "":
        return_value = False  # false: 資料不完全 註冊失敗

    s = Session()
    if return_value:
        new_department = Department(dep_name=_emp_dep)
        s.add(new_department)
        s.commit()

    s.close()

    return jsonify({
        'status': return_value
    })


# create stockout data into table
@createTable.route("/createStockOut", methods=['POST'])
def create_stockOut():
    print("createStockOut....")
    request_data = request.get_json()

    _data = request_data['stockOut_array']
    _count = request_data['stockOut_count']

    # print("_data, _count: ", _data, _count)
    return_array = []
    return_value = True  # true: 資料正確
    if not _data or len(_data) != _count:
        return_value = False  # false: 資料不完全

    s = Session()

    # _objects = s.query(OutTag).all()
    # _outtags = [u.__dict__ for u in _objects]
    # print("_objects, _outtags: ", type(_objects), type(_outtags))
    # cnt1 = len(_objects)
    # cnt2 = len(_data)
    # print("cnt1, cnt2: ", cnt1, cnt2)
    '''
    for i in range(cnt1):
        result1 = list(_outtags[i].keys())
        for j in range(cnt2):
            result2 = list(_data[j].keys())
            # if outtagKey in _data.keys():
            print("compare Key1: ", result1)
            print("compare Key2: ", result2)
    '''
    _user = s.query(User).filter_by(
        emp_name=_data[0]['stockOutTag_Employer']).first()

    for i in range(_count):
        new_outtag = OutTag(intag_id=_data[i]['stockOutTag_InID'],
                            user_id=_user.id,
                            count=_data[i]['stockOutTag_cnt'],
                            unit=_data[i]['stockOutTag_unit'],
                            outtag_date=_data[i]['stockOutTag_Date'],
                            )
        s.add(new_outtag)  # 新增一筆出庫資料
        s.flush()
        # print("outtag add, id: ", new_outtag.id)
        return_array.append(new_outtag.id)

        cursor = s.query(func.sum(OutTag.count)).filter(
            OutTag.intag_id == _data[i]['stockOutTag_InID']).filter(
            OutTag.isRemoved == True)
        total = cursor.scalar()
        #print("total: ", total)

        intag = s.query(InTag).filter_by(
            id=_data[i]['stockOutTag_InID']).first()
        # intag.count = intag.count - _data[i]['stockOutTag_cnt']  # 修改入庫資料
        # intag.stockOut_temp_count = intag.stockOut_temp_count + \
        #    _data[i]['stockOutTag_cnt']  # 修改入庫資料
        intag.stockOut_temp_count = total  # 修改入庫資料

        s.commit()
    s.close()

    return jsonify({
        'status': return_value,
        'return_outTag_ID': return_array,
    })


'''
for key in Boys.keys():
    if key in Dict.keys():
        print True
    else:
        print False

    s = Session()
    if return_value:
        _objects = s.query(OutTag).all()
        for outtagKey in _objects.keys():
            if outtagKey in _data.keys():

            new_department = OutTag(dep_name=_emp_dep)
            s.add(new_department)
            s.commit()

    s.close()

    return jsonify({
        'status': return_value
    })
'''
