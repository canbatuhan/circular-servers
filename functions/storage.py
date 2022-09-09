import time
from typing import List


def load(storage:List[dict], data:dict, is_success:bool):
    is_success = False
    for each in storage:
        if each.get("name") == data.get("name"):
            is_success = True
            time.sleep(each.get("size")/1000)
            break
    return {"is_success": is_success}


def store(storage:List[dict], data:dict, capacity:int, in_use:int, is_success:bool):
    is_success = False
    for each in storage:
        if each.get("name") == data.get("name"):
            is_success = True
            return {"is_success": is_success}

    if data.get("size") + in_use <= capacity:
        storage.append(data)
        in_use += data.get("size")
        is_success = True
        time.sleep(data.get("size")/1000)
    
    return {"storage": storage, "in_use": in_use, "is_success": is_success}