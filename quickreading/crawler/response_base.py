"""
 Created by Yan Liu at 2019-1-20.
 reference https://github.com/howie6879/owllook/blob/master/owllook/fetcher/response_base.py
"""


class ResponseField():
    """
    Define the response field
    """
    MESSAGE = 'info'
    STATUS = 'state'
    DATA = 'data'
    FINISH_AT = 'finished_at'


class ResponseReply():
    """
    Define field description
    """
    # ERROR
    UNKNOWN_ERR = 'error'
    PARAM_ERR = 'param error!'
    PARAM_PARSE_ERR = "param fail to parse!"
    DB_ERROR = "database error"
    # FORBIDDEN
    IP_FORBIDDEN = "ip is forbidden"
    # NOT AUTHORIZED
    NOT_AUTHORIZED = "not authorized"
    # SUCCESS
    SUCCESS = 'ok'


# set the response status
class ResponseCode():
    """
    Define the response code
    """
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_AUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERR = 500


class UniResponse():
    NOT_AUTHORIZED = {ResponseField.MESSAGE: ResponseReply.NOT_AUTHORIZED,
                      ResponseField.STATUS: ResponseCode.NOT_AUTHORIZED}
    PARAM_PARSE_ERR = {ResponseField.MESSAGE: ResponseReply.PARAM_PARSE_ERR,
                       ResponseField.STATUS: ResponseCode.BAD_REQUEST}
    PARAM_ERR = {ResponseField.MESSAGE: ResponseReply.PARAM_ERR,
                 ResponseField.STATUS: ResponseCode.BAD_REQUEST}
    PARAM_UNKNOWN_ERR = {ResponseField.MESSAGE: ResponseReply.UNKNOWN_ERR,
                         ResponseField.STATUS: ResponseCode.BAD_REQUEST}
    IP_FORBIDDEN = {ResponseField.MESSAGE: ResponseReply.IP_FORBIDDEN,
                    ResponseField.STATUS: ResponseCode.FORBIDDEN}
    SERVER_DB_ERR = {ResponseField.MESSAGE: ResponseReply.DB_ERROR,
                     ResponseField.STATUS: ResponseCode.SERVER_ERR}
    SERVER_UNKNOWN_ERR = {ResponseField.MESSAGE: ResponseReply.UNKNOWN_ERR,
                          ResponseField.STATUS: ResponseCode.SERVER_ERR}
    SUCCESS = {ResponseField.MESSAGE: ResponseReply.SUCCESS,
               ResponseField.STATUS: ResponseCode.SUCCESS}

