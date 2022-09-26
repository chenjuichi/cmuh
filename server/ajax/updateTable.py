from flask import Blueprint, jsonify, request
from sqlalchemy import func

from database.tables import User, Department, OutTag, InTag, Setting, Session

from werkzeug.security import generate_password_hash

updateTable = Blueprint('updateTable', __name__)


# ------------------------------------------------------------------


# update password from user table some data
@updateTable.route("/updatePassword", methods=['POST'])
def update_password():
    print("updatePassword....")
    request_data = request.get_json()
    userID = (request_data['empID'] or '')
    newPassword = (request_data['newPassword'] or '')

    return_value = True  # true: 資料正確, 註冊成功
    if userID == "" or newPassword == "":
        return_value = False  # false: 資料不完全 註冊失敗

    s = Session()
    s.query(User).filter(User.emp_id == userID).update(
        {'password': generate_password_hash(
            newPassword, method='sha256')})
    s.commit()
    s.close()

    return jsonify({
        'status': return_value,
    })


# update user's setting from user table some data
@updateTable.route("/updateSetting", methods=['POST'])
def update_setting():
    print("updateSetting....")
    request_data = request.get_json()
    userID = (request_data['empID'] or '')
    newSetting = (request_data['setting'] or '')

    return_value = True  # true: 資料正確, 註冊成功
    if userID == "" or newSetting == "":
        return_value = False  # false: 資料不完全 註冊失敗
    print("update setting value: ", newSetting, type(newSetting))
    s = Session()
    # 修改user的設定資料
    _user = s.query(User).filter_by(emp_id=userID).first()
    s.query(Setting).filter(Setting.id == _user.setting_id).update(
        {'items_per_page': newSetting})

    s.query(User).filter(User.emp_id == userID).update(
        {'isOnline': False})  # false:user已經登出(logout)

    s.commit()
    s.close()

    return jsonify({
        'status': return_value,
    })


@updateTable.route("/updateUser", methods=['POST'])
def update_user():
    print("register....")
    request_data = request.get_json()

    _emp_id = request_data['emp_id']
    _emp_name = request_data['emp_name']

    return_value = True  # true: 資料正確, 註冊成功
    if _emp_id == "" or _emp_name == "":
        return_value = False  # false: 資料不完全 註冊失敗

    dep = (request_data['dep'] or '')  # convert null into empty string

    s = Session()

    department = s.query(Department).filter_by(dep_name=dep).first()
    if not department:
        return_value = False  # if the user's department does not exist

    if return_value:
        s.query(User).filter(User.emp_id == _emp_id).update(
            {"emp_name": _emp_name, "dep_id": department.id})
        s.commit()

    s.close()

    return jsonify({
        'status': return_value
    })


@updateTable.route("/updateDepartment", methods=['POST'])
def update_department():
    print("updateDepartment....")
    request_data = request.get_json()

    _id = int(request_data['id'])  # convert string into integer
    _emp_dep = request_data['emp_dep']

    return_value = True  # true: 資料正確, 註冊成功
    if _id == "" or _emp_dep == "":
        return_value = False  # false: 資料不完全 註冊失敗

    s = Session()

    if return_value:
        s.query(Department).filter(Department.id == _id).update(
            {"dep_name": _emp_dep})
        s.commit()

    s.close()

    return jsonify({
        'status': return_value
    })


# update intag's stockOut_temp_count and outtag's count data
@updateTable.route("/updateStockOutAndStockInData", methods=['POST'])
def update_StockOut_and_StockIn_data():
    print("updateStockOutAndStockInData....")
    request_data = request.get_json()

    _data = request_data['stockOut_array']
    _count = request_data['stockOut_count']
    print("_data, _count: ", _data, _count)

    return_value = True  # true: 資料正確
    if not _data or len(_data) != _count:
        return_value = False  # false: 資料不完全

    s = Session()

    outtag = s.query(OutTag).filter_by(id=_data['stockOutTag_ID']).first()
    intag = s.query(InTag).filter_by(id=_data['stockOutTag_InID']).first()

    outtag.count = _data['stockOutTag_cnt']   # 修改出庫資料
    # intag.count = intag.count - int(_data['stockOutTag_cnt'])  # 修改入庫資料
    # intag.stockOut_temp_count = intag.stockOut_temp_count + \
    #    int(_data['stockOutTag_cnt'])  # 修改入庫資料
    cursor = s.query(func.sum(OutTag.count)).filter(
        OutTag.intag_id == _data['stockOutTag_InID']).filter(
        OutTag.isRemoved == True)
    total = cursor.scalar()

    intag.stockOut_temp_count = total  # 修改入庫資料

    s.commit()

    s.close()

    return jsonify({
        'status': return_value,
    })
