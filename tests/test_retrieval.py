"""
tests/test_retrieval.py
Tests for the TF-IDF retrieval engine.
Run with: python tests/test_retrieval.py
or: python -m pytest tests/test_retrieval.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest


class TestRetrieval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Build the retriever index once for all tests."""
        from src.data_loader import load_all_chunks
        from src.retrieval import KnowledgeRetriever
        cls.chunks = load_all_chunks()
        cls.retriever = KnowledgeRetriever()
        cls.retriever.build_index(cls.chunks)

    def test_retriever_is_ready(self):
        self.assertTrue(self.retriever.is_ready)
        self.assertGreater(self.retriever.chunk_count, 0)
        print(f"\n  Retriever ready with {self.retriever.chunk_count} chunks")

    def test_search_returns_results_for_known_topic(self):
        results = self.retriever.search("rice paddy sowing season")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Should return results for 'rice paddy sowing'")
        print(f"\n  'rice paddy sowing' -> {len(results)} results, top score: {results[0]['score']:.4f}")

    def test_search_result_fields(self):
        results = self.retriever.search("wheat irrigation stages")
        if results:
            top = results[0]
            self.assertIn("text", top)
            self.assertIn("score", top)
            self.assertIn("source", top)
            self.assertGreater(top["score"], 0)

    def test_search_relevance_rice_stage(self):
        results = self.retriever.search("rice transplanting stage paddy nursery seedling")
        self.assertGreater(len(results), 0)
        # Top result should be from crop_roadmaps or crops
        top_sources = [r.get("source", "") for r in results[:3]]
        relevant_sources = {"crop_roadmaps.json", "crops.json"}
        self.assertTrue(
            any(s in relevant_sources for s in top_sources),
            f"Top sources {top_sources} should include a crop-related source"
        )

    def test_safety_keyword_detection(self):
        self.assertTrue(self.retriever.is_safety_query("What to do during cyclone?"))
        self.assertTrue(self.retriever.is_safety_query("lightning danger in field"))
        self.assertTrue(self.retriever.is_safety_query("electric shock from water pump"))
        self.assertFalse(self.retriever.is_safety_query("how to irrigate wheat"))
        self.assertFalse(self.retriever.is_safety_query("best variety of rice"))

    def test_safety_search_returns_safety_chunks(self):
        results = self.retriever.search_safety("cyclone warning")
        self.assertIsInstance(results, list)
        if results:
            for r in results:
                self.assertEqual(r.get("topic"), "safety",
                                 "Safety search should only return safety-topic chunks")

    def test_crop_filter_narrows_results(self):
        results_filtered = self.retriever.search("pest disease symptoms", crop_filter="tomato")
        results_unfiltered = self.retriever.search("pest disease symptoms")
        # Filtered results should all be tomato-related or empty
        for r in results_filtered:
            crop = r.get("crop_id", "") or r.get("crop_name", "")
            self.assertTrue(
                "tomato" in crop.lower() or r.get("crop_id") == "general",
                f"Filtered result has unexpected crop: {crop}"
            )
        print(f"\n  Unfiltered: {len(results_unfiltered)}, tomato-filtered: {len(results_filtered)}")

    def test_empty_query_returns_empty(self):
        results = self.retriever.search("")
        self.assertEqual(results, [])
        results2 = self.retriever.search("   ")
        self.assertEqual(results2, [])

    def test_minimum_score_filters_irrelevant(self):
        # A query with no relevance should return fewer or zero results
        results = self.retriever.search("xyzzzzz nonsense random noise 12345", min_score=0.5)
        self.assertEqual(len(results), 0, "High min_score should filter out irrelevant results")

    def test_top_k_respected(self):
        results = self.retriever.search("crop farming India", top_k=3)
        self.assertLessEqual(len(results), 3)

    def test_search_natural_farming_topic(self):
        results = self.retriever.search("compost preparation cow dung organic matter")
        self.assertGreater(len(results), 0)
        sources = [r.get("source", "") for r in results[:3]]
        self.assertTrue(
            any("natural_farming" in s for s in sources),
            f"Expected natural_farming.json in top sources, got: {sources}"
        )

    def test_domain_queries_do_not_mix_unrelated_topics_or_crops(self):
        cases = [
            (
                "How should I manage pests in cotton organically?",
                "pest_disease",
                "cotton",
            ),
            (
                "What are the stages of the rice crop lifecycle?",
                "crop_lifecycle",
                "rice",
            ),
            (
                "Electrical safety during irrigation with a water pump",
                "safety",
                None,
            ),
            (
                "What are natural farming practices for soil health?",
                "natural_farming",
                None,
            ),
        ]
        for query, expected_topic, expected_crop in cases:
            with self.subTest(query=query):
                results = self.retriever.search(query, top_k=12)
                self.assertTrue(results, f"Expected relevant matches for: {query}")
                self.assertTrue(
                    all(chunk.get("topic") == expected_topic for chunk in results),
                    f"Unexpected topics for {query}: {[c.get('topic') for c in results]}",
                )
                if expected_crop:
                    self.assertTrue(
                        all(chunk.get("crop_id") == expected_crop for chunk in results),
                        f"Unexpected crops for {query}: {[c.get('crop_id') for c in results]}",
                    )
                if expected_topic == "safety":
                    self.assertTrue(
                        all(chunk.get("safety_id") == "electrical_safety" for chunk in results),
                        "Electrical queries should not include unrelated hazard advice",
                    )

    def test_strict_metadata_filters_never_fall_back_to_global_results(self):
        self.assertEqual(
            self.retriever.search(
                "rice lifecycle stages",
                crop_filter="unknown-crop",
                topic_filter="crop_lifecycle",
            ),
            [],
        )

    def test_search_market_info_not_in_knowledge(self):
        """Market prices are in market_service, not in the retrieval knowledge base."""
        results = self.retriever.search("live mandi price today onion nashik")
        # This should return low-relevance results or nothing
        # The important thing is it does NOT invent a price
        # (actual price invention prevention is in the LLM prompt layer)
        print(f"\n  Market query results: {len(results)}")


class TestRetrieverSingleton(unittest.TestCase):

    def test_get_retriever_singleton(self):
        from src.retrieval import get_retriever
        from src.data_loader import load_all_chunks
        chunks = load_all_chunks()
        r1 = get_retriever(chunks)
        r2 = get_retriever()  # no chunks — should return same instance
        self.assertIs(r1, r2, "get_retriever should return the same singleton")


if __name__ == "__main__":
    print("Running retrieval tests...")
    unittest.main(verbosity=2)
