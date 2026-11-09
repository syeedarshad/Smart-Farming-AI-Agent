"""
tests/test_data_loader.py
Tests for data loading and chunk generation.
Run with: python tests/test_data_loader.py
or: python -m pytest tests/test_data_loader.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest


class TestDataLoader(unittest.TestCase):

    def test_load_crops_returns_list(self):
        from src.data_loader import load_crops
        chunks = load_crops()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0, "load_crops should return at least 1 chunk")

    def test_crops_have_required_fields(self):
        from src.data_loader import load_crops
        chunks = load_crops()
        for chunk in chunks:
            self.assertIn("text", chunk, "Every chunk must have 'text'")
            self.assertIn("source", chunk, "Every chunk must have 'source'")
            self.assertIn("topic", chunk, "Every chunk must have 'topic'")
            self.assertIn("crop_id", chunk, "Crop chunks must have 'crop_id'")
            self.assertGreater(len(chunk["text"]), 10, "Chunk text should be non-trivial")

    def test_load_state_mapping(self):
        from src.data_loader import load_state_crop_mapping
        chunks = load_state_crop_mapping()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        # Check Tamil Nadu is present
        states_in_chunks = [c.get("state", "") for c in chunks]
        self.assertIn("Tamil Nadu", states_in_chunks, "Tamil Nadu should be in state mapping")
        self.assertIn("Maharashtra", states_in_chunks)

    def test_load_crop_roadmaps(self):
        from src.data_loader import load_crop_roadmaps
        chunks = load_crop_roadmaps()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        # Should have rice roadmap
        rice_chunks = [c for c in chunks if c.get("crop_id") == "rice"]
        self.assertGreater(len(rice_chunks), 0, "Rice roadmap chunks should be present")

    def test_load_natural_farming(self):
        from src.data_loader import load_natural_farming
        chunks = load_natural_farming()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        # Check for compost
        topics = [c.get("practice_name", "") for c in chunks]
        compost_present = any("compost" in t.lower() for t in topics)
        self.assertTrue(compost_present, "Compost practice should be in natural farming data")

    def test_load_pest_management(self):
        from src.data_loader import load_pest_management
        chunks = load_pest_management()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

    def test_load_farmer_safety(self):
        from src.data_loader import load_farmer_safety
        chunks = load_farmer_safety()
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        # Safety chunks should have safety topic
        safety_topics = [c.get("topic", "") for c in chunks]
        self.assertTrue(all(t == "safety" for t in safety_topics))

    def test_load_all_chunks(self):
        from src.data_loader import load_all_chunks
        all_chunks = load_all_chunks()
        self.assertIsInstance(all_chunks, list)
        self.assertGreater(len(all_chunks), 50, "Should have at least 50 chunks total")
        print(f"\n  Total chunks loaded: {len(all_chunks)}")

    def test_chunk_text_field_not_empty(self):
        from src.data_loader import load_all_chunks
        all_chunks = load_all_chunks()
        empty = [i for i, c in enumerate(all_chunks) if not c.get("text", "").strip()]
        self.assertEqual(len(empty), 0, f"Found {len(empty)} chunks with empty text")

    def test_data_summary(self):
        from src.data_loader import get_data_summary
        summary = get_data_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("crops", summary)
        self.assertIn("safety", summary)
        for key, count in summary.items():
            self.assertGreater(count, 0, f"Section '{key}' has 0 chunks")
        print(f"\n  Data summary: {summary}")


if __name__ == "__main__":
    print("Running data loader tests...")
    unittest.main(verbosity=2)
