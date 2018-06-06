from crud import settings

from rest_framework.response import Response

ERROR_CODES = {
    "IMDV000": "Internal Server Error",
}


class AdminAccessException(Exception):
    pass


def make_exc_response(
        request, error_code, status_code, excpetion=None, reason=""):
    response = {
        "success": False,
        "error_code": error_code,
        "error_message": (
            str(excpetion) if settings.DEBUG and status_code == 500 and excpetion else ERROR_CODES[error_code] + reason  # noqa
        )
    }
    if request.data.get('reference_no'):
        response['reference_no'] = request.data.get('reference_no')
    else:
        response['reference_no'] = "Invalid"
    return Response((response), status=status_code)


def make_success_response(request, data, status):
    data.update({
        "success_message": "Request processed successfully!"
    })
    if request.data.get('reference_no'):
        data['reference_no'] = request.data.get('reference_no')
    else:
        data['reference_no'] = "Invalid"
    return Response(data, status)
