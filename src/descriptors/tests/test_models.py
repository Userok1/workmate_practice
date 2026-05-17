import pytest

from src.descriptors import models


class Model(models.Model):
    name = models.Field(path="name")
    slug = models.Field(path="meta.slug")
    href = models.Field(path="meta.remote.href")


class TestModel:
    @pytest.fixture
    def payload(self):
        return {
            "name": "model-name",
            "meta": {"slug": "model-slug"},
        }

    @pytest.fixture
    def model(self, payload):
        return Model(payload)

    @pytest.mark.parametrize(
        "field_name, field_value",
        [("name", "model-name"), ("slug", "model-slug"), ("href", None)],
    )
    def test_get(self, model, field_name, field_value):
        assert getattr(model, field_name) == field_value

    def test_set__exists(self, model):
        model.name = "new-name"
        assert model.name == "new-name"
        assert model.payload["name"] == "new-name"

    def test_set__exists_nested(self, model):
        model.slug = "new-slug"
        assert model.slug == "new-slug"
        assert model.payload["meta"]["slug"] == "new-slug"

    # @pytest.mark.skip("no need to implement")
    def test_set__empty_nested(self, model):
        model.href = "new-href"
        assert model.href == "new-href"
        reference = {
            "name": "model-name",
            "meta": {"slug": "model-slug", "remote": {"href": "new-href"}},
        }
        assert model.payload == reference
