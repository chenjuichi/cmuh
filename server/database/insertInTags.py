from tables import User, Setting, InTag, Session

import pymysql
from sqlalchemy import exc

from werkzeug.security import generate_password_hash

# --------------------------
user = [2,   2,  3,   3,  4, 5, 6, 7,   7, 7]
reagent = [14, 12, 13,   9, 11, 5, 6, 7,   8, 1]
grid = [9,   1,  1,   2,  4, 5, 6,  7,  7, 8]
count = [6,   6,  6,   5,  5, 5, 2, 10,  2, 2]
temp_cnt = [1,   1,  1,   1,  2, 5, 2,  0,  0, 0]
batch = ['1110012345A123400001', '1110012345A123400002', '1110012345A123400003',
         '1110012345A123400011', '1110012345A123400012', '1110012345A123400013',
         '1110012345A123400021', '1110012345A123400022', '1110012345A123400023',
         '1110012345A123400050'
         ]
intag_date = ['111/06/01', '111/05/01', '111/05/01', '111/04/01', '111/04/01',
              '111/03/01', '111/06/01', '111/06/01', '111/07/01', '111/08/01',
              ]


s = Session()
_results = []

for i in range(10):
    _obj = InTag(user_id=user[i], reagent_id=reagent[i],
                 grid_id=grid[i], count=count[i],
                 stockOut_temp_count=temp_cnt[i], batch=batch[i], intag_date=intag_date[i])
    _results.append(_obj)

s.bulk_save_objects(_results)

try:
    s.commit()
except pymysql.err.IntegrityError as e:
    s.rollback()
except exc.IntegrityError as e:
    s.rollback()
except Exception as e:
    s.rollback()

s.close()

print("insert 10 inTag data is ok...")
