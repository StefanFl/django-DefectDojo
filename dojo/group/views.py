import logging
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import urlencode
from django.db import DEFAULT_DB_ALIAS
from rest_framework.authtoken.models import Token

from dojo.filters import GroupFilter
from dojo.forms import DojoUserForm, AddDojoUserForm, DeleteUserForm, APIKeyForm, UserContactInfoForm, \
    Add_Product_Type_Member_UserForm, Add_Product_Member_UserForm
from dojo.models import Product, Product_Type, Dojo_User, Alerts, Product_Member, Product_Type_Member, Dojo_Group
from dojo.utils import get_page_items, add_breadcrumb
from dojo.product.queries import get_authorized_product_members_for_user
from dojo.product_type.queries import get_authorized_product_type_members_for_user
from dojo.authorization.roles_permissions import Permissions
from dojo.group.queries import get_authorized_products_for_group, get_authorized_product_types_for_group

logger = logging.getLogger(__name__)

@user_passes_test(lambda u: u.is_staff)
def group(request):
    groups = Dojo_Group.objects.order_by('name')
    groups = GroupFilter(request.GET, queryset=groups)
    paged_groups = get_page_items(request, groups.qs, 25)
    add_breadcrumb(title="All Groups", top_level=True, request=request)
    return render(request,
                  'dojo/groups.html',
                  {'groups': paged_groups,
                   'filtered': groups,
                   'name': 'All Groups',
                  })


@user_passes_test(lambda u: u.is_staff)
def view_group(request, gid):
    group = get_object_or_404(Dojo_Group, id=gid)
    products = get_authorized_products_for_group(group)
    product_types = get_authorized_product_types_for_group(group)

    add_breadcrumb(title="View Group", top_level=False, request=request)
    return render(request, 'dojo/view_group.html', {
        'group': group,
        'products': products,
        'product_types': product_types
    })


@user_passes_test(lambda u: u.is_superuser)
def edit_group(request, gid):
    print("placeholder")


@user_passes_test(lambda u: u.is_superuser)
def delete_group(request, gid):
    print("placeholder")


@user_passes_test(lambda u: u.is_superuser)
def add_group(request):
    print("placeholder")

@user_passes_test(lambda u: u.is_superuser)
def add_product_group(request):
    print("placeholder")

@user_passes_test(lambda u: u.is_superuser)
def add_product_type_group(request):
    print("placeholder")