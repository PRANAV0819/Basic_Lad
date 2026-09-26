# core/views.py
#
# WHAT: This file contains the "view" functions for the core app.
#       A view is simply a Python function that receives a web request
#       and returns a web response (usually an HTML page).
#
# WHY:  In Django, views are the "brain" of each page.
#       They decide WHAT data to prepare and WHICH template to render.
#       Right now our landing page has no dynamic data, so the view
#       is minimal — it just renders the HTML template.
#
# WHERE: This file lives at core/views.py.
#        Django automatically looks for views inside each app.
#
# HOW Django uses it:
#       1. A browser makes a GET request to "/"
#       2. config/urls.py receives it and delegates to core/urls.py
#       3. core/urls.py matches the URL pattern and calls home_view
#       4. home_view asks Django to render home.html and return it as HTTP response


from django.shortcuts import render


def home_view(request):
    """
    View for the landing page (home page).

    `request` is the HttpRequest object Django passes automatically.
    It contains information like the HTTP method (GET/POST), user agent,
    cookies, session data, etc.

    `render(request, template_name)` does three things:
        1. Loads the template from core/templates/core/home.html
        2. Builds an HttpResponse with the rendered HTML
        3. Returns it to the browser

    The empty dict {} is the "context" — data we would pass to the template.
    Since the landing page is static, we pass nothing for now.
    """
    return render(request, 'core/home.html', {})
