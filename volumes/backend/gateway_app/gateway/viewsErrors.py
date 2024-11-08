import os
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

def get_404(request, exception):
    logger.debug("")
    logger.debug("get_404")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug("get_404 XMLHttpRequest")
        html = render_to_string('fragments/404_fragment.html', context={}, request=request)
        return JsonResponse({'html': html}, status=404)
    return render(request, 'partials/404.html', status=404)
