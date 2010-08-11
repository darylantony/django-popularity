# This file is part of django-popularity.
# 
# django-popularity: A generic view- and popularity tracking pluggable for Django. 
# Copyright (C) 2008-2010 Mathijs de Bruin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseGone
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist

from models import ViewTracker

def view_for(request, content_type_id, object_id, force_add=False):
    """ Add or request view tracking information for an object 
        through a POST or AJAX GET request, respectively. 

        Use as follows:
        GET /<content_type_id>/<object_id>/ -> View count
        POST /<content_type_id>/<object_id>/ -> Increment view count and
                                                yield view count

        If the request is an AJAX request, the viewcount is
        returned in a JSON object as 'views'.
    """

    # Get the object from request parameters
    try:
        ct = ContentType.objects.get(pk=content_type_id)
        myobject = ct.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        return HttpResponseGone()
    
    # Do we add a view?
    if force_add or request.method == "POST":
        logging.debug('Adding view for %s through web.', myobject)
        ViewTracker.add_view_for(myobject)

    # Get response data
    tracker = ViewTracker.get_views_for(myobject)
    response_dict = {'views': tracker}

    # AJAX request? Return JSON views
    if request.is_ajax():
        return HttpResponse(simplejson.dumps(response_dict), 
                            mimetype='application/javascript')

    # Not AJAX? Return plaintext view count
    return HttpResponse(response_dict['views'])

def add_view_for(request, content_type_id, object_id):
    """ Wrapper around view_for for backwards incompatibility
        which always adds a view. """

    return view_for(request, content_type_id, object_id, force_add=True)

