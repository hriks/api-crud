from __future__ import unicode_literals

from .handler import (
    AdminAccessException, make_exc_response,
    make_success_response, auth_required,
    InventoryAccessException
)
from django.utils.decorators import method_decorator
from django import views

from .models import Inventory
from django.db.models import F

UPDATE_FIELDS = ['height', 'width', 'length']
COMMON_FILTERS = ['length', 'width', 'height', 'area', 'volume']
FILTERS = COMMON_FILTERS + ['created_by', 'created']


class ADD(views.View):

    @method_decorator(views.decorators.csrf.csrf_exempt)
    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(ADD, self).dispatch(request, user, *args, **kwargs)

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
                'height': float(height), 'width': float(width),
                'length': float(length), 'created_by': user
            })
            response = {
                "reference_no": inventory.reference_no,
                "created_by": inventory.created_by.username
            }
            return make_success_response(data, response, 200)
        except AssertionError as e:
            return make_exc_response(data, str(e), 403)
        except AdminAccessException:
            return make_exc_response(data, "INVN004", 403)
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, e
            )


class Update(views.View):

    @method_decorator(views.decorators.csrf.csrf_exempt)
    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(Update, self).dispatch(request, user, *args, **kwargs)

    def post(self, request, user):
        try:
            data = request.POST.dict()
            if not user.is_staff:
                raise AdminAccessException("User must be staff to add box")
            inventory = Inventory.objects.get(
                reference_no=data.get("reference_no"))
            assert True in [
                field in UPDATE_FIELDS for field, value in data.items()
            ], "INVN006"
            update_fields = list(
                set(data.keys()).intersection(set(UPDATE_FIELDS)))
            for field in update_fields:
                assert data.get(field).isdigit(), "INVN008"
            inventory.update(data)
            response = {
                "reference_no": inventory.reference_no,
                "created_by": inventory.created_by.username,
                "last_modified_time": inventory.modified,
                "updated_fields": update_fields
            }
            return make_success_response(
                data, response, 200)
        except Inventory.DoesNotExist:
            return make_exc_response(data, "INVN007", 403)
        except AssertionError as e:
            return make_exc_response(data, str(e), 403)
        except AdminAccessException as e:
            return make_exc_response(data, "INVN004", 403, str(e))
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, str(e)
            )


class All(views.View):

    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(All, self).dispatch(request, user, *args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        try:
            data = request.GET.dict()
            inventories = Inventory.objects.all()
            params = dict()
            for field in data.keys():
                if field.split("__")[0] in FILTERS:
                    params.update(
                        {'{0}'.format(field): float(data.get(field))}
                    )
            inventories = inventories.filter(**params)
            if user.is_staff:
                inventories = inventories.annotate(
                    created_by_user=F('created_by__username')
                ).values(
                    'created_by_user', 'length', 'height', 'width', 'volume',
                    'area', 'modified', 'reference_no'
                )
            else:
                inventories = inventories.values(
                    'length', 'height', 'width', 'volume', 'area'
                )
            return make_success_response(
                data, {'inventories': list(inventories)}, 200)
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, str(e)
            )


class MyBoxes(views.View):

    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(MyBoxes, self).dispatch(request, user, *args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        try:
            data = request.GET.dict()
            if not user.is_staff:
                raise AdminAccessException("User must be staff to add box")
            inventories = Inventory.objects.filter(created_by=user)
            params = dict()
            for field in data.keys():
                if field.split("__")[0] in FILTERS:
                    params.update(
                        {'{0}'.format(field): float(data.get(field))}
                    )
                inventories = inventories.filter(**params)
            inventories = inventories.annotate(
                created_by_user=F('created_by__username')
            ).values(
                'created_by_user', 'length', 'height', 'width', 'volume',
                'area', 'modified', 'reference_no'
            )
            return make_success_response(
                data, {'inventories': list(inventories)}, 200)
        except AdminAccessException as e:
            return make_exc_response(data, "INVN004", 403, str(e))
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, str(e)
            )


class Delete(views.View):

    @method_decorator(views.decorators.csrf.csrf_exempt)
    @method_decorator(auth_required)
    def dispatch(self, request, user, *args, **kwargs):
        return super(Delete, self).dispatch(request, user, *args, **kwargs)

    def post(self, request, user, *args, **kwargs):
        try:
            data = request.POST.dict()
            inventory = Inventory.objects.get(
                reference_no=data.get('reference_no'))
            if not inventory.created_by == user:
                raise InventoryAccessException(
                    "Box creator Exception")
            inventory.delete()
            return make_success_response(
                data, {
                    "status": "Deleted Successfully!"
                }, 200)
        except InventoryAccessException as e:
            return make_exc_response(data, "INVN009", 403, str(e))
        except Inventory.DoesNotExist:
            return make_exc_response(data, "INVN007", 403)
        except AdminAccessException:
            return make_exc_response(data, "INVN004", 403, str(e))
        except Exception as e:
            return make_exc_response(
                data, "INVN000", 500, str(e)
            )
