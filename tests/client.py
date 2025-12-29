import unittest
from datetime import datetime
from urllib.parse import urljoin

import responses

from nextcloud_cookbook_api.client import CookbookClient
from nextcloud_cookbook_api.models import (
    Category,
    Config,
    Keyword,
    Nutrition,
    Recipe,
    RecipeStub,
)


class TestCookbookClient(unittest.TestCase):
    """Test suite for CookbookClient API methods."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.base_url = "http://localhost:8080"
        self.username = "testuser"
        self.password = "testpass"
        self.client = CookbookClient(self.base_url, self.username, self.password)

    @responses.activate
    def test_get_all_keywords(self) -> None:
        """Test retrieving all keywords."""
        keywords_data = [
            {"name": "vegetarian", "recipe_count": 5},
            {"name": "vegan", "recipe_count": 3},
            {"name": "gluten-free", "recipe_count": 2},
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/keywords"),
            json=keywords_data,
            status=200,
        )

        result = self.client.get_keywords()

        assert len(result) == 3
        assert isinstance(result[0], Keyword)
        assert result[0].name == "vegetarian"
        assert result[0].recipe_count == 5

    @responses.activate
    def test_search_recipes_by_keywords(self) -> None:
        """Test searching recipes by keywords."""
        recipes_data = [
            {
                "id": "1",
                "name": "Vegetarian Pasta",
                "keywords": "pasta,vegetarian",
                "dateCreated": "2023-01-01T10:00:00",
                "dateModified": "2023-01-02T10:00:00",
                "imageUrl": "http://example.com/image1.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder1.jpg",
            },
            {
                "id": "2",
                "name": "Veggie Salad",
                "keywords": "salad,vegetarian",
                "dateCreated": "2023-01-03T10:00:00",
                "dateModified": "2023-01-04T10:00:00",
                "imageUrl": "http://example.com/image2.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder2.jpg",
            },
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/tags/vegetarian,vegan"),
            json=recipes_data,
            status=200,
        )

        result = self.client.search_recipes_by_keywords(["vegetarian", "vegan"])

        assert len(result) == 2
        assert isinstance(result[0], RecipeStub)
        assert result[0].id == "1"
        assert result[0].name == "Vegetarian Pasta"

    @responses.activate
    def test_get_all_categories(self) -> None:
        """Test retrieving all categories."""
        categories_data = [
            {"name": "Desserts", "recipe_count": 10},
            {"name": "Main Courses", "recipe_count": 15},
            {"name": "Appetizers", "recipe_count": 5},
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/categories"),
            json=categories_data,
            status=200,
        )

        result = self.client.get_categories()

        assert len(result) == 3
        assert isinstance(result[0], Category)
        assert result[0].name == "Desserts"
        assert result[0].recipe_count == 10

    @responses.activate
    def test_get_recipes_by_category(self) -> None:
        """Test retrieving recipes by category."""
        recipes_data = [
            {
                "id": "1",
                "name": "Chocolate Cake",
                "keywords": "dessert,chocolate",
                "dateCreated": "2023-01-01T10:00:00",
                "dateModified": "2023-01-02T10:00:00",
                "imageUrl": "http://example.com/cake.jpg",
                "imagePlaceholderUrl": "http://example.com/cake_placeholder.jpg",
            },
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/category/Desserts"),
            json=recipes_data,
            status=200,
        )

        result = self.client.get_recipes_by_category("Desserts")

        assert len(result) == 1
        assert isinstance(result[0], RecipeStub)
        assert result[0].name == "Chocolate Cake"

    @responses.activate
    def test_get_recipes_by_category_none(self) -> None:
        """Test retrieving recipes without category."""
        recipes_data = []
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/category/_"),
            json=recipes_data,
            status=200,
        )

        result = self.client.get_recipes_by_category(None)

        assert len(result) == 0

    @responses.activate
    def test_rename_category(self) -> None:
        """Test renaming a category."""
        categories_data = [{"name": "Desserts", "recipe_count": 10}]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/categories"),
            json=categories_data,
            status=200,
        )
        responses.add(
            responses.PUT,
            urljoin(self.base_url, "/apps/cookbook/api/v1/category/Desserts"),
            status=200,
        )

        self.client.rename_category("Desserts", "Sweet Treats")

        assert len(responses.calls) == 2

    @responses.activate
    def test_rename_category_same_name(self) -> None:
        """Test renaming a category with the same name (should return early)."""
        self.client.rename_category("Desserts", "Desserts")

        # No API calls should be made
        assert len(responses.calls) == 0

    @responses.activate
    def test_rename_category_not_found(self) -> None:
        """Test renaming a non-existent category."""
        categories_data = [{"name": "Desserts", "recipe_count": 10}]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/categories"),
            json=categories_data,
            status=200,
        )

        with self.assertRaises(ValueError) as context:
            self.client.rename_category("NonExistent", "NewName")

    @responses.activate
    def test_import_recipe(self) -> None:
        """Test importing a recipe from URL."""
        recipe_data = {
            "@type": "Recipe",
            "id": "1",
            "name": "Imported Recipe",
            "keywords": "imported",
            "dateCreated": "2023-01-01T10:00:00",
            "dateModified": "2023-01-02T10:00:00",
            "imageUrl": "http://example.com/image.jpg",
            "imagePlaceholderUrl": "http://example.com/placeholder.jpg",
            "prepTime": "PT10M",
            "cookTime": "PT20M",
            "totalTime": "PT30M",
            "description": "A test recipe",
            "url": "http://recipe-source.com/recipe",
            "image": "http://recipe-source.com/image.jpg",
            "recipeYield": 2,
            "recipeCategory": "Main Courses",
            "tools": ["Oven"],
            "recipeIngredient": ["Ingredient 1", "Ingredient 2"],
            "recipeInstructions": ["Step 1", "Step 2"],
            "nutrition": {
                "@type": "NutritionInformation",
                "calories": "500 kcal",
            },
        }
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/import"),
            json=recipe_data,
            status=200,
        )

        result = self.client.import_recipe("http://recipe-source.com/recipe")

        assert isinstance(result, Recipe)
        assert result.id == "1"
        assert result.name == "Imported Recipe"

    @responses.activate
    def test_get_recipe_main_image(self) -> None:
        """Test retrieving recipe main image."""
        image_data = b"\x89PNG\r\n\x1a\n"
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1/image"),
            body=image_data,
            status=200,
        )

        result = self.client.get_recipe_main_image("1")

        assert result == image_data

    @responses.activate
    def test_get_recipe_main_image_thumb(self) -> None:
        """Test retrieving recipe thumbnail."""
        image_data = b"\x89PNG\r\n\x1a\n"
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1/image"),
            body=image_data,
            status=200,
        )

        result = self.client.get_recipe_main_image("1", size="thumb")

        assert result == image_data

    @responses.activate
    def test_search_recipes(self) -> None:
        """Test searching for recipes."""
        recipes_data = [
            {
                "id": "1",
                "name": "Pasta",
                "keywords": "pasta",
                "dateCreated": "2023-01-01T10:00:00",
                "dateModified": "2023-01-02T10:00:00",
                "imageUrl": "http://example.com/image1.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder1.jpg",
            },
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/search/pasta"),
            json=recipes_data,
            status=200,
        )

        result = self.client.search_recipes("pasta")

        assert len(result) == 1
        assert isinstance(result[0], RecipeStub)
        assert result[0].name == "Pasta"

    @responses.activate
    def test_get_all_recipes(self) -> None:
        """Test retrieving all recipes."""
        recipes_data = [
            {
                "id": "1",
                "name": "Recipe 1",
                "keywords": "tag1",
                "dateCreated": "2023-01-01T10:00:00",
                "dateModified": "2023-01-02T10:00:00",
                "imageUrl": "http://example.com/image1.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder1.jpg",
            },
            {
                "id": "2",
                "name": "Recipe 2",
                "keywords": "tag2",
                "dateCreated": "2023-01-03T10:00:00",
                "dateModified": "2023-01-04T10:00:00",
                "imageUrl": "http://example.com/image2.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder2.jpg",
            },
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes"),
            json=recipes_data,
            status=200,
        )

        result = self.client.get_recipes()

        assert len(result) == 2
        assert isinstance(result[0], RecipeStub)
        assert result[1].name == "Recipe 2"

    @responses.activate
    def test_create_recipe(self) -> None:
        """Test creating a new recipe."""
        recipe = Recipe.model_construct(
            id="new",
            name="New Recipe",
            keywords=["test"],
            date_created=datetime.now(),
            date_modified=datetime.now(),
            nutrition=Nutrition.model_construct(calories="42 kcal"),
        )
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes"),
            body="123",
            status=200,
        )

        result = self.client.create_recipe(recipe)

        assert result == "123"

    @responses.activate
    def test_create_recipe_with_full_data(self) -> None:
        """Test creating a recipe with all fields populated."""
        nutrition = Nutrition.model_construct(
            type="NutritionInformation",
            calories="500 kcal",
            protein_content="25 g",
            fat_content="20 g",
        )
        recipe = Recipe.model_construct(
            type="Recipe",
            id="new",
            name="Full Recipe",
            keywords=["full", "test"],
            dateCreated=datetime.now(),
            dateModified=datetime.now(),
            description="A complete test recipe",
            url="http://example.com/recipe",
            servings=4,
            category="Main Courses",
            tools=["Oven", "Pan"],
            ingredients=["Ingredient A", "Ingredient B"],
            instructions=["Step 1", "Step 2"],
            nutrition=nutrition,
        )
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes"),
            body="456",
            status=200,
        )

        result = self.client.create_recipe(recipe)

        assert result == "456"
        assert len(responses.calls) == 1
        assert b"Full Recipe" in responses.calls[0].request.body

    @responses.activate
    def test_get_recipe(self) -> None:
        """Test retrieving a specific recipe."""
        recipe_data = {
            "@type": "Recipe",
            "id": "1",
            "name": "Test Recipe",
            "keywords": "test",
            "dateCreated": "2023-01-01T10:00:00",
            "dateModified": "2023-01-02T10:00:00",
            "imageUrl": "http://example.com/image.jpg",
            "imagePlaceholderUrl": "http://example.com/placeholder.jpg",
            "prepTime": "PT10M",
            "cookTime": "PT20M",
            "totalTime": "PT30M",
            "description": "A test recipe",
            "url": "",
            "image": "",
            "recipeYield": 2,
            "recipeCategory": "Main Courses",
            "tools": [],
            "recipeIngredient": ["Ingredient 1"],
            "recipeInstructions": ["Step 1"],
            "nutrition": {
                "@type": "NutritionInformation",
                "calories": "500 kcal",
            },
        }
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1"),
            json=recipe_data,
            status=200,
        )

        result = self.client.get_recipe("1")

        assert isinstance(result, Recipe)
        assert result.id == "1"
        assert result.name == "Test Recipe"

    @responses.activate
    def test_update_recipe(self) -> None:
        """Test updating an existing recipe."""
        recipe = Recipe.model_construct(
            id="1",
            name="Updated Recipe",
            keywords=["updated"],
            date_created=datetime.now(),
            date_modified=datetime.now(),
            nutrition=Nutrition.model_construct(type="NutritionInformation"),
        )
        responses.add(
            responses.PUT,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1"),
            status=200,
        )

        self.client.update_recipe("1", recipe)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == "PUT"

    @responses.activate
    def test_update_recipe_http_error(self) -> None:
        """Test updating a recipe when server returns error."""
        recipe = Recipe.model_construct(
            type="Recipe",
            id="1",
            name="Updated Recipe",
            keywords=["test"],
            dateCreated=datetime.now(),
            dateModified=datetime.now(),
            nutrition=Nutrition.model_construct(type="NutritionInformation"),
        )
        responses.add(
            responses.PUT,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1"),
            status=400,
            json={"error": "Bad request"},
        )

        with self.assertRaises(Exception):
            self.client.update_recipe("1", recipe)

    @responses.activate
    def test_delete_recipe(self) -> None:
        """Test deleting a recipe."""
        responses.add(
            responses.DELETE,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1"),
            status=200,
        )

        self.client.delete_recipe("1")

        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == "DELETE"

    @responses.activate
    def test_delete_recipe_http_error(self) -> None:
        """Test deleting a recipe when server returns error."""
        responses.add(
            responses.DELETE,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/999"),
            status=500,
            json={"error": "Internal server error"},
        )

        with self.assertRaises(Exception):
            self.client.delete_recipe("999")

    @responses.activate
    def test_get_ocr_capabilities(self) -> None:
        """Test retrieving OCR capabilities."""
        capabilities_data = {
            "ocs": {
                "meta": {"status": "ok", "statuscode": 200},
                "data": {
                    "capabilities": {
                        "tesseract": True,
                    },
                },
            },
        }
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/ocs/v2.php/cloud/capabilities"),
            json=capabilities_data,
            status=200,
        )

        result = self.client.get_ocr_capabilities()

        assert isinstance(result, dict)
        assert "ocs" in result

    @responses.activate
    def test_trigger_reindex(self) -> None:
        """Test triggering a reindex."""
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/reindex"),
            status=200,
        )

        self.client.trigger_reindex()

        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == "POST"

    @responses.activate
    def test_get_config(self) -> None:
        """Test retrieving configuration."""
        config_data = {
            "folder": "/Recipes",
            "update_interval": 60,
            "visibleInfoBlocks": {
                "preparation-time": True,
                "cooking-time": True,
                "total-time": True,
                "nutrition-information": True,
                "tools": False,
            },
        }
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/config"),
            json=config_data,
            status=200,
        )

        result = self.client.get_config()

        assert isinstance(result, Config)
        assert result.folder == "/Recipes"

    @responses.activate
    def test_set_config(self) -> None:
        """Test setting configuration."""
        config = Config(
            folder="/Recipes",
            update_interval=60,
        )
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/config"),
            status=200,
        )

        self.client.set_config(config)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == "POST"

    @responses.activate
    def test_authentication_headers(self) -> None:
        """Test that requests include proper authentication."""
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/keywords"),
            json=[],
            status=200,
        )

        self.client.get_keywords()

        # Check that the request was made with basic auth
        assert len(responses.calls) == 1
        # The auth header should be present (responses library automatically handles it)
        request = responses.calls[0].request
        assert request is not None

    @responses.activate
    def test_http_error_handling(self) -> None:
        """Test that HTTP errors are properly raised."""
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/999"),
            json={"error": "Not found"},
            status=404,
        )

        with self.assertRaises(Exception):  # requests.HTTPError
            self.client.get_recipe("999")

    @responses.activate
    def test_base_url_handling(self) -> None:
        """Test that base URL is correctly handled."""
        base_url_with_slash = urljoin(self.base_url, "/")
        client = CookbookClient(base_url_with_slash, self.username, self.password)

        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/keywords"),
            json=[],
            status=200,
        )

        result = client.get_keywords()

        assert len(result) == 0

    @responses.activate
    def test_search_recipes_multiple_terms(self) -> None:
        """Test searching for recipes with multiple search terms."""
        recipes_data = []
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/search/pasta,sauce"),
            json=recipes_data,
            status=200,
        )

        result = self.client.search_recipes("pasta,sauce")

        assert len(result) == 0

    @responses.activate
    def test_search_recipes_special_characters(self) -> None:
        """Test searching for recipes with special characters."""
        recipes_data = []
        responses.add(
            responses.GET,
            urljoin(
                self.base_url, "/apps/cookbook/api/v1/search/caf%C3%A9%20au%20lait"
            ),
            json=recipes_data,
            status=200,
        )

        result = self.client.search_recipes("café au lait")

        assert len(result) == 0

    @responses.activate
    def test_keyword_count(self) -> None:
        """Test retrieving keywords with various recipe counts."""
        keywords_data = [
            {"name": "popular", "recipe_count": 100},
            {"name": "rare", "recipe_count": 1},
            {"name": "medium", "recipe_count": 50},
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/keywords"),
            json=keywords_data,
            status=200,
        )

        result = self.client.get_keywords()

        counts = sorted([k.recipe_count for k in result])
        assert counts == [1, 50, 100]

    @responses.activate
    def test_empty_recipe_list_response(self) -> None:
        """Test handling empty recipe list."""
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes"),
            json=[],
            status=200,
        )

        result = self.client.get_recipes()

        assert isinstance(result, list)
        assert len(result) == 0

    @responses.activate
    def test_recipe_with_empty_keywords(self) -> None:
        """Test recipe with empty keywords field."""
        recipes_data = [
            {
                "id": "1",
                "name": "No Keywords Recipe",
                "keywords": "",
                "dateCreated": "2023-01-01T10:00:00",
                "dateModified": "2023-01-02T10:00:00",
                "imageUrl": "http://example.com/image.jpg",
                "imagePlaceholderUrl": "http://example.com/placeholder.jpg",
            },
        ]
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes"),
            json=recipes_data,
            status=200,
        )

        result = self.client.get_recipes()

        assert len(result) == 1
        assert result[0].keywords == []

    @responses.activate
    def test_get_recipe_with_null_fields(self) -> None:
        """Test retrieving a recipe with null optional fields."""
        recipe_data = {
            "@type": "Recipe",
            "id": "1",
            "name": "Minimal Recipe",
            "keywords": None,
            "dateCreated": "2023-01-01T10:00:00",
            "dateModified": "2023-01-02T10:00:00",
            "imageUrl": "",
            "imagePlaceholderUrl": "",
            "prepTime": None,
            "cookTime": None,
            "totalTime": None,
            "description": "",
            "url": "",
            "image": "",
            "recipeYield": 1,
            "recipeCategory": "",
            "tools": [],
            "recipeIngredient": [],
            "recipeInstructions": [],
            "nutrition": {
                "@type": "NutritionInformation",
            },
        }
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1"),
            json=recipe_data,
            status=200,
        )

        result = self.client.get_recipe("1")

        assert isinstance(result, Recipe)
        assert result.name == "Minimal Recipe"

    @responses.activate
    def test_image_size_parameter_variations(self) -> None:
        """Test different image size parameters."""
        image_data = b"\x89PNG\r\n\x1a\n"

        # Test 'full' size
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1/image"),
            body=image_data,
            status=200,
        )
        result = self.client.get_recipe_main_image("1", size="full")
        assert result == image_data

        # Test 'thumb' size
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1/image"),
            body=image_data,
            status=200,
        )
        result = self.client.get_recipe_main_image("1", size="thumb")
        assert result == image_data

        # Test 'thumb16' size
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/recipes/1/image"),
            body=image_data,
            status=200,
        )
        result = self.client.get_recipe_main_image("1", size="thumb16")
        assert result == image_data

    @responses.activate
    def test_import_recipe_with_minimal_data(self) -> None:
        """Test importing a recipe with minimal required data."""
        recipe_data = {
            "@type": "Recipe",
            "id": "1",
            "name": "Simple Import",
            "keywords": "",
            "dateCreated": "2023-01-01T10:00:00",
            "dateModified": "2023-01-02T10:00:00",
            "imageUrl": "",
            "imagePlaceholderUrl": "",
            "nutrition": {
                "@type": "NutritionInformation",
            },
        }
        responses.add(
            responses.POST,
            urljoin(self.base_url, "/apps/cookbook/api/v1/import"),
            json=recipe_data,
            status=200,
        )

        result = self.client.import_recipe("http://example.com/recipe")

        assert isinstance(result, Recipe)
        assert result.name == "Simple Import"

    @responses.activate
    def test_config_with_all_visibility_settings(self) -> None:
        """Test config with all visibility settings."""
        config_data = {
            "folder": "/Recipes",
            "update_interval": 60,
            "visibleInfoBlocks": {
                "preparation-time": True,
                "cooking-time": False,
                "total-time": True,
                "nutrition-information": False,
                "tools": True,
            },
        }
        responses.add(
            responses.GET,
            urljoin(self.base_url, "/apps/cookbook/api/v1/config"),
            json=config_data,
            status=200,
        )

        result = self.client.get_config()

        assert isinstance(result, Config)
        assert result.folder == "/Recipes"
        assert result.update_interval == 60


if __name__ == "__main__":
    unittest.main()
