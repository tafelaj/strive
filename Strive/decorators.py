from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def user_is_investor(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if not user.loans_admin:
            return function(request, *args, **kwargs)
        else:
            return redirect('loans_admin:loans_admin_home')
    wrap.__doc__ = function.__doc__
    return wrap


def user_is_loans_admin(function):
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.loans_admin:
            return function(request, *args, **kwargs)
        else:
            return redirect('investor:home')
    wrap.__doc__ = function.__doc__
    return wrap
