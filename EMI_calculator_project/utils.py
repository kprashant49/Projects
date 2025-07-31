# utils.py

def Errorapiresponse(code: str, custom_msg: str = None) -> dict:
    from Errorstring import Error

    return {
        "Success": False,
        "Errorcode": code,
        "Message": custom_msg if custom_msg else Error.get(code, "Unknown error occurred")
    }
