"""Configuration regression tests; no live credentials or network calls."""
import os
import unittest
from unittest.mock import patch


class TestConfigurationSources(unittest.TestCase):
    def test_environment_value_takes_precedence_over_streamlit_secret(self):
        from src import config

        with patch.dict(os.environ, {"TEST_WATSONX_VALUE": "from-env"}, clear=True), \
             patch("src.config._streamlit_secret", return_value="from-cloud"):
            self.assertEqual(config._setting("TEST_WATSONX_VALUE"), "from-env")

    def test_streamlit_secret_is_used_when_environment_is_missing(self):
        from src import config

        with patch.dict(os.environ, {}, clear=True), \
             patch("src.config._streamlit_secret", return_value="from-cloud"):
            self.assertEqual(config._setting("TEST_WATSONX_VALUE"), "from-cloud")

    def test_provider_auto_selects_granite_only_when_credentials_exist(self):
        from src.config import _resolve_provider

        self.assertEqual(_resolve_provider("", "key", "project"), "ibm_granite")
        self.assertEqual(_resolve_provider("", "key", ""), "demo")
        self.assertEqual(_resolve_provider("demo", "key", "project"), "demo")


class TestGraniteRestRequest(unittest.TestCase):
    def test_chat_request_uses_project_model_bearer_and_parses_answer(self):
        from src.llm import ibm_granite_provider as provider_module

        class Response:
            status_code = 200
            ok = True

            @staticmethod
            def json():
                return {"choices": [{"message": {"content": "Grounded answer."}}]}

        with patch.object(provider_module, "IBM_WATSONX_API_KEY", "test-api-key"), \
             patch.object(provider_module, "IBM_WATSONX_PROJECT_ID", "test-project"), \
             patch.object(provider_module, "IBM_WATSONX_URL", "https://example.ibm.test"), \
             patch.object(provider_module, "IBM_GRANITE_MODEL_ID", "ibm/granite-test"), \
             patch.object(provider_module._token_cache, "get_token", return_value="test-bearer"), \
             patch.object(provider_module.requests, "post", return_value=Response()) as post:
            answer = provider_module._call_watsonx_rest("test prompt", 64)

        self.assertEqual(answer, "Grounded answer.")
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://example.ibm.test/ml/v1/text/chat?version=2023-05-29")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-bearer")
        self.assertEqual(kwargs["json"]["project_id"], "test-project")
        self.assertEqual(kwargs["json"]["model_id"], "ibm/granite-test")

    def test_expired_bearer_is_refreshed_once_after_401(self):
        from src.llm import ibm_granite_provider as provider_module

        class Response:
            ok = True

            def __init__(self, status_code, body=None):
                self.status_code = status_code
                self._body = body or {}

            def json(self):
                return self._body

        responses = [Response(401), Response(200, {"choices": [{"message": {"content": "Retried."}}]})]
        with patch.object(provider_module, "IBM_WATSONX_API_KEY", "test-api-key"), \
             patch.object(provider_module, "IBM_WATSONX_PROJECT_ID", "test-project"), \
             patch.object(provider_module, "IBM_WATSONX_URL", "https://example.ibm.test"), \
             patch.object(provider_module, "IBM_GRANITE_MODEL_ID", "ibm/granite-test"), \
             patch.object(provider_module._token_cache, "get_token", side_effect=["expired", "refreshed"]), \
             patch.object(provider_module._token_cache, "invalidate") as invalidate, \
             patch.object(provider_module.requests, "post", side_effect=responses) as post:
            answer = provider_module._call_watsonx_rest("test prompt", 64)

        self.assertEqual(answer, "Retried.")
        self.assertEqual(post.call_count, 2)
        invalidate.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
