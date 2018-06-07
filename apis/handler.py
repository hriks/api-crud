from crud import settings

from django.http import JsonResponse
from django.contrib.auth.models import User

ERROR_CODES = {
    "INVN000": "Internal Server Error",
    "INVN001": "Username or Password not provided.",
    "INVN002": "User Doesnot Exists",
    "INVN003": "Invalid password provided",
    "INVN004": "Unable to process request. user is not staff",
    "INVN005": "Either height, width or length not provided.",
    "INVN006": "No fields are provided to update",
    "INVN007": "No Box found in Inventory with reference_no or reference_no not provided!",  # noqa
    "INVN008": "Invalid value for fields are provided",
    "INVN009": "Invalid Filter provided",
    "INVN010": "Invalid Filter method. This should be less or greater",
    "INVN011": "Filter method not provided"
}


class AdminAccessException(Exception):
    pass


def make_exc_response(
        data, error_code, status_code, excpetion=None, reason=""):
    response = {
        "success": False,
        "error_code": error_code,
        "error_message": (
            str(excpetion) if settings.DEBUG and status_code == 500 and excpetion else ERROR_CODES[error_code] + reason  # noqa
        )
    }
    if data.get('reference_no'):
        response['reference_no'] = data.get('reference_no')
    return JsonResponse(response, status=status_code)


def make_success_response(data, response, status):
    response.update({
        "success_message": "Request processed successfully!"
    })
    if data.get('reference_no'):
        response['reference_no'] = data.get('reference_no')
    return JsonResponse(response, status=status)


def auth_required(f, methods={
        "GET": 0, "POST": 0, "PUT": 0, "DELETE": 0}):
    def wrap(request, *args, **kwargs):
        try:
            if request.method == 'GET':
                data = request.GET.dict()
            else:
                data = request.POST.dict()
            username = data['username']
            user = User.objects.get(username=username)
            validated = user.check_password(data['password'])
            if not validated:
                return make_exc_response(
                    data, "INVN003", 428
                )
        except KeyError:
            return make_exc_response(
                data, "INVN001", 403)
        except User.DoesNotExist:
            return make_exc_response(
                data, "INVN002", 403)
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, e
            )
        return f(request, user, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
