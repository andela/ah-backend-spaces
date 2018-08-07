import json

from rest_framework.renderers import JSONRenderer


class AHJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'

    def render(self, data, media_type=None, renderer_context=None):
        # check for any errors
        errors = data.get('errors', None)

        if errors is not None:
            return super(AHJSONRenderer, self).render(data)

        return json.dumps({
            self.object_label: data
        })
