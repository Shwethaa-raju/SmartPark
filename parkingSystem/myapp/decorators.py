from django.contrib.auth.decorators import user_passes_test, login_required

active_required = user_passes_test(lambda u: u.is_active,
                                   login_url='/')

def active_and_login_required(view_func):
    decorated_view_func = login_required(active_required(view_func))
    return decorated_view_func
