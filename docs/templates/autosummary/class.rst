{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block attributes %}
    {% if attributes %}
    .. rubric:: {{ _('Attributes') }}

    .. autosummary::
    {% for item in attributes %}
      ~{{ name }}.{{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}


    {% block methods %}

    {% if methods %}
    .. rubric:: {{ _('Methods') }}

    {% for item in methods %}
    {% if item != '__init__' %}.. automethod:: {{ item }} {% endif %}
    {%- endfor %}
    {% endif %}
    {% endblock %}
