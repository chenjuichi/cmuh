from flask import Blueprint, jsonify, request
from sqlalchemy import func

from database.tables import User, OutTag, InTag, Session

#from werkzeug.security import generate_password_hash

deleteTable = Blueprint('deleteTable', __name__)


# ------------------------------------------------------------------


@deleteTable.route("/removeUser", methods=['POST'])
def remove_user():
    print("remove user....")
    request_data = request.get_json()
    userID = request_data['empID']

    return_value = True  # true: 資料正確, 註冊成功
    if userID == "":
        return_value = False  # false: 資料不完全 註冊失敗

    s = Session()
    s.query(User).filter(User.emp_id == userID).update({'isRemoved': False})
    s.commit()
    s.close()

    return jsonify({
        'status': return_value,
    })

# delete outtag item and update intag's stockOut_temp_count


@deleteTable.route("/deleteStockOutAndStockInData", methods=['POST'])
def delete_StockOut_and_StockIn_data():
    print("deleteStockOutAndStockInData....")
    request_data = request.get_json()

    _data = request_data['stockOut_array']
    _count = request_data['stockOut_count']
    print("_data, _count: ", _data, _count)

    return_value = True  # true: 資料正確
    if not _data or len(_data) != _count:
        return_value = False  # false: 資料不完全

    s = Session()
    outtag = s.query(OutTag).filter_by(id=_data['stockOutTag_ID']).first()
    s.delete(outtag)

    intag = s.query(InTag).filter_by(id=_data['stockOutTag_InID']).first()

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
