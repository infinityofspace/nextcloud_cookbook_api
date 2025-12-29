Usage
=====

Module
++++++

The module provides the :class:`CookbookClient <nextcloud_cookbook_api.client.CookbookClient>` class, which is used to interact with the Nextcloud Cookbook app API.
To use the client, you need to create an instance of the :class:`CookbookClient <nextcloud_cookbook_api.client.CookbookClient>` class:

.. code-block:: python

    from nextcloud_cookbook_api.client import CookbookClient

    client = CookbookClient(
        username="<your-nextcloud-username>",
        password="<your-nextcloud-password>",
        base_url="https://your-nextcloud-instance.com"
    )

You can find all available methods in the :class:`CookbookClient <nextcloud_cookbook_api.client.CookbookClient>` class documentation.

Examples
++++++

Here are some examples of how to use the :class:`CookbookClient <nextcloud_cookbook_api.client.CookbookClient>` class:

- Fetching all recipes:

  .. code-block:: python

    recipes = client.get_all_recipes()
    for recipe in recipes:
        print(recipe.name)

- Adding a new recipe from url:

  .. code-block:: python

    new_recipe = client.import_recipe(
        url="https://example.com/recipe-url"
    ))
    print(new_recipe.id)
    print(new_recipe.name)
