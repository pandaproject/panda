#!/usr/bin/env python

from django.middleware.csrf import get_token 

class CsrfCookieUsedMiddleware(object): 
    """ 
    Simple middleware that ensures Django's CSRF middleware will 
    always include the CSRF cookie on outgoing responses. 

    See: https://groups.google.com/d/msg/django-developers/Zi9_AyfBd_0/t_TlsL8-CHMJ
    """ 
    def process_request(self, request): 
        get_token(request)

