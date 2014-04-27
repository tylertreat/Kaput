import unittest

from kaput import utils


class TestChunk(unittest.TestCase):

    def test_empty_list(self):
        """Ensure an empty list is returned when an empty list is passed."""

        self.assertEqual([], utils.chunk([], 10).next())

    def test_bad_chunk_size(self):
        """Ensure an empty list is returned when a bad chunk size is passed."""

        self.assertEqual([], utils.chunk([1, 2, 3, 4, 5], 0).next())

    def test_chunking_equal_groups(self):
        """Ensure the list is chunked properly into equal groups when it can be
        evenly divided.
        """

        the_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        chunk_size = 3
        full = []

        for group in utils.chunk(the_list, chunk_size):
            self.assertEqual(chunk_size, len(group))
            full.extend(group)

        self.assertEqual(the_list, full)

    def test_chunking_equal_groups_but_one(self):
        """Ensure the list is chunked properly into equal groups except for the
        last when it cannot be evenly divided.
        """

        the_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        chunk_size = 3
        full = []

        for i, group in enumerate(utils.chunk(the_list, chunk_size)):
            if i == 3:
                self.assertEqual(1, len(group))
            else:
                self.assertEqual(chunk_size, len(group))
            full.extend(group)

        self.assertEqual(the_list, full)

