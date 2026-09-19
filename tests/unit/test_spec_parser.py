"""Unit tests for the API specification parser."""

import json

import pytest
import yaml

from app.services.spec_parser import (
    EndpointInfo,
    ParsedSpec,
    SpecParserError,
    parse_spec,
)


class TestParseRawFormats:
    """Test JSON and YAML format detection."""

    def test_parse_json_spec(self):
        spec = json.dumps({"openapi": "3.0.0", "info": {"title": "Test"}, "paths": {}})
        result = parse_spec(spec)
        assert isinstance(result, ParsedSpec)
        assert result.title == "Test"

    def test_parse_yaml_spec(self):
        spec = yaml.dump({"openapi": "3.0.0", "info": {"title": "YAML Test"}, "paths": {}})
        result = parse_spec(spec)
        assert isinstance(result, ParsedSpec)
        assert result.title == "YAML Test"

    def test_empty_spec_raises_error(self):
        with pytest.raises(SpecParserError, match="Empty specification"):
            parse_spec("")

    def test_whitespace_only_raises_error(self):
        with pytest.raises(SpecParserError, match="Empty specification"):
            parse_spec("   ")

    def test_invalid_format_raises_error(self):
        with pytest.raises(SpecParserError):
            parse_spec("<<<not valid json or yaml>>>")

    def test_array_spec_raises_error(self):
        with pytest.raises(SpecParserError, match="must be a JSON/YAML object"):
            parse_spec('[1, 2, 3]')


class TestOpenAPIParsing:
    """Test OpenAPI specification extraction."""

    @pytest.fixture
    def sample_openapi_spec(self) -> str:
        return json.dumps({
            "openapi": "3.0.3",
            "info": {
                "title": "Sample API",
                "description": "A test API",
                "version": "1.0.0"
            },
            "servers": [{"url": "http://localhost:8001"}],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "array"}
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create user",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Created"},
                            "400": {"description": "Bad request"}
                        }
                    }
                },
                "/users/{user_id}": {
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "get": {
                        "summary": "Get user",
                        "responses": {
                            "200": {"description": "Success"},
                            "404": {"description": "Not found"}
                        }
                    },
                    "delete": {
                        "summary": "Delete user",
                        "responses": {
                            "204": {"description": "Deleted"}
                        }
                    }
                }
            }
        })

    def test_extracts_title_and_version(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        assert result.title == "Sample API"
        assert result.version == "1.0.0"
        assert result.description == "A test API"

    def test_extracts_base_url(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        assert result.base_url == "http://localhost:8001"

    def test_extracts_correct_endpoint_count(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        assert result.endpoint_count == 4  # GET /users, POST /users, GET /users/{id}, DELETE /users/{id}

    def test_extracts_methods(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        assert result.available_methods == {"GET", "POST", "DELETE"}

    def test_extracts_paths(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        assert result.available_paths == {"/users", "/users/{user_id}"}

    def test_extracts_query_parameters(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        get_users = [ep for ep in result.endpoints if ep.path == "/users" and ep.method == "GET"][0]
        assert len(get_users.parameters) == 1
        assert get_users.parameters[0].name == "limit"
        assert get_users.parameters[0].location == "query"

    def test_extracts_path_parameters(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        get_user = [ep for ep in result.endpoints if ep.path == "/users/{user_id}" and ep.method == "GET"][0]
        # Path-level params should be inherited
        assert any(p.name == "user_id" and p.location == "path" for p in get_user.parameters)

    def test_extracts_request_body(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        post_users = [ep for ep in result.endpoints if ep.path == "/users" and ep.method == "POST"][0]
        assert post_users.request_body is not None
        assert post_users.request_body.required is True
        assert "properties" in post_users.request_body.schema

    def test_extracts_response_codes(self, sample_openapi_spec):
        result = parse_spec(sample_openapi_spec)
        get_user = [ep for ep in result.endpoints if ep.path == "/users/{user_id}" and ep.method == "GET"][0]
        response_codes = {r.status_code for r in get_user.responses}
        assert 200 in response_codes
        assert 404 in response_codes

    def test_no_servers_gives_empty_base_url(self):
        spec = json.dumps({"openapi": "3.0.0", "info": {"title": "No Server"}, "paths": {}})
        result = parse_spec(spec)
        assert result.base_url == ""


class TestGenericParsing:
    """Test non-OpenAPI spec parsing."""

    def test_generic_spec_with_paths(self):
        spec = json.dumps({
            "title": "My API",
            "paths": {
                "/items": {"get": {}, "post": {}},
                "/items/{id}": {"get": {}, "delete": {}}
            }
        })
        result = parse_spec(spec)
        assert result.title == "My API"
        assert result.endpoint_count == 4

    def test_generic_spec_without_paths(self):
        spec = json.dumps({"name": "Simple", "version": "1.0"})
        result = parse_spec(spec)
        assert result.endpoint_count == 0
        assert result.raw_spec["name"] == "Simple"
