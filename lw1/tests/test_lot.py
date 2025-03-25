import unittest

from auction import Lot

class TestLot(unittest.TestCase):
    def test_lot_creation_with_default_values(self):
        lot = Lot()
        self.assertIsNone(lot.name)
        self.assertIsNone(lot.description)
        self.assertEqual(lot.minimum_bid, 0.0)

    def test_lot_equality_with_same_id(self):
        lot1 = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        lot2 = Lot(name="Sculpture", description="A stunning sculpture", minimum_bid=200.0)
        lot2._lot_id = lot1.lot_id
        self.assertEqual(lot1, lot2)

    def test_lot_inequality_with_different_ids(self):
        lot1 = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        lot2 = Lot(name="Sculpture", description="A stunning sculpture", minimum_bid=200.0)
        self.assertNotEqual(lot1, lot2)

    def test_lot_to_dict_representation(self):
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        expected_dict = {
            'name': "Painting",
            'description': "A beautiful painting",
            'minimum_bid': 100.0,
            'lot_id': lot.lot_id
        }
        self.assertEqual(lot._to_dict(), expected_dict)

    def test_lot_from_dict_creation(self):
        data = {
            'name': "Painting",
            'description': "A beautiful painting",
            'minimum_bid': 100.0,
            'lot_id': 1
        }
        lot = Lot._from_dict(data)
        self.assertEqual(lot.name, "Painting")
        self.assertEqual(lot.description, "A beautiful painting")
        self.assertEqual(lot.minimum_bid, 100.0)
        self.assertEqual(lot.lot_id, 1)

if __name__ == "__main__":
    unittest.main()