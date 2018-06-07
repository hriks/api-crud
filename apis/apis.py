from __future__ import unicode_literals

from .handler import (
    AdminAccessException, make_exc_response,
    make_success_response, auth_required
)
from django.utils.decorators import method_decorator
from django import views

from .models import Inventory


class Box(views.View):

    @method_decorator(views.decorators.csrf.csrf_exempt)
    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(Box, self).dispatch(request, user, *args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        try:
            data = request.GET.dict()
            return make_success_response(
                data, {}, 200)
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, e
            )

    def post(self, request, user):
        try:
            data = request.POST.dict()
            if not user.is_staff:
                raise AdminAccessException("User must be staff to add box")
            height = data.get('height')
            width = data.get('width')
            length = data.get('length')
            assert height.isdigit() and height is not None, "INVN005"
            assert width.isdigit() and width is not None, "INVN005"
            assert length.isdigit() and length is not None, "INVN005"
            inventory = Inventory.addBox(**{
                'height': height, 'width': width, 'length': length,
                'created_by': user
            })
            response = {
                "reference_no": inventory.reference_no,
                "created_by": inventory.created_by.username
            }
            return make_success_response(
                data, response, 200)
        except AssertionError as e:
            return make_exc_response(
                data, str(e), 403
            )
        except AdminAccessException:
            return make_exc_response(
                data, "INVN004", 403
            )
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, e
            )
