import unittest

from auction import Bid, Lot, AuctionParticipant

class TestBid(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test."""
        self.lot = Lot("Painting", "A beautiful landscape painting.", minimum_bid=100)
        self.participant1 = AuctionParticipant("Alice", balance=500)
        self.participant2 = AuctionParticipant("Bob", balance=200)

    def test_bid_creation_valid(self):
        """Test creating a valid bid."""
        bid = Bid(self.lot, 150, self.participant1)
        self.assertEqual(bid.amount, 150)
        self.assertEqual(bid.participant, self.participant1)
        self.assertEqual(bid.lot, self.lot)

    def test_bid_creation_below_minimum(self):
        """Test that creating a bid below the minimum raises an error."""
        with self.assertRaises(ValueError) as context:
            Bid(self.lot, 50, self.participant1)
        self.assertEqual(str(context.exception), "Bid amount is less than the minimum bid")

    def test_bid_creation_exceeds_balance(self):
        """Test that creating a bid exceeding the participant's balance raises an error."""
        with self.assertRaises(ValueError) as context:
            Bid(self.lot, 600, self.participant1)
        self.assertEqual(str(context.exception), "Bid amount exceeds participant balance")

    def test_increase_bid_valid(self):
        """Test increasing the bid with a valid higher amount."""
        bid = Bid(self.lot, 150, self.participant1)
        bid.increase_bid(200, self.participant2)
        self.assertEqual(bid.amount, 200)
        self.assertEqual(bid.participant, self.participant2)

    def test_increase_bid_lower_amount(self):
        """Test that increasing the bid with a lower or equal amount raises an error."""
        bid = Bid(self.lot, 150, self.participant1)
        with self.assertRaises(ValueError) as context:
            bid.increase_bid(150, self.participant2)
        self.assertEqual(str(context.exception), "New bid amount must be greater than the current bid")

        with self.assertRaises(ValueError) as context:
            bid.increase_bid(100, self.participant2)
        self.assertEqual(str(context.exception), "New bid amount must be greater than the current bid")

    def test_increase_bid_exceeds_balance(self):
        """Test that increasing the bid beyond the participant's balance raises an error."""
        bid = Bid(self.lot, 150, self.participant1)
        with self.assertRaises(ValueError) as context:
            bid.increase_bid(300, self.participant2)  # Bob only has 200 balance
        self.assertEqual(str(context.exception), "Bid amount exceeds participant balance")

    def test_bid_equality(self):
        """Test bid equality comparison."""
        bid1 = Bid(self.lot, 150, self.participant1)
        bid2 = Bid(self.lot, 150, self.participant1)
        bid3 = Bid(self.lot, 200, self.participant1)

        self.assertEqual(bid1, bid2)
        self.assertNotEqual(bid1, bid3)

if __name__ == "__main__":
    unittest.main()
