===========================
Managing dataset categories
===========================

PANDA allows you to organize your datasets into categories that you define. By default it comes configured with a small handful of categories we imagine everyone will need, but you will almost certainly want to add your own.

.. note::

    Categories are intended to be used as **broad** groupings of datasets ("Crime" or "Education"), not projects ("Medicaid Investigation 2012") or tags ("president"). Trying to use them in these latter ways is strongly discouraged.

Categories can be maintained by visiting the categories section of the admin::

    http://localhost:8000/admin/redd/category/

This interface should be largely self-explanatory. When creating a new category a url slug will automatically be generated based on the name you provide. In less you feel the need to edit them for brevity, these default slugs are usually fine.

