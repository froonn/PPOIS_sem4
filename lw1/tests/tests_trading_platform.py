import unittest

from auction import TradingPlatform, AuctionParticipant, Lot, Bid

class TestTradingPlatform(unittest.TestCase):

    def test_platform_add_single_participant(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        platform.add(participant)
        self.assertIn(participant, platform.participants)

    def test_platform_add_single_lot(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        self.assertIn(lot, platform.lots)

    def test_platform_add_multiple_participants_and_lots(self):
        platform = TradingPlatform()
        participant1 = AuctionParticipant(nickname="Alice", balance=100.0)
        participant2 = AuctionParticipant(nickname="Bob", balance=200.0)
        lot1 = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        lot2 = Lot(name="Sculpture", description="A stunning sculpture", minimum_bid=200.0)
        platform.add(participant1, participant2, lot1, lot2)
        self.assertIn(participant1, platform.participants)
        self.assertIn(participant2, platform.participants)
        self.assertIn(lot1, platform.lots)
        self.assertIn(lot2, platform.lots)

    def test_platform_remove_participant(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        platform.add(participant)
        platform.remove(participant)
        self.assertNotIn(participant, platform.participants)

    def test_platform_remove_lot(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.remove(lot)
        self.assertNotIn(lot, platform.lots)

    def test_platform_start_auction_with_no_lots(self):
        platform = TradingPlatform()
        with self.assertRaises(ValueError):
            platform.start_auction()

    def test_platform_place_invalid_bid_exceeding_balance(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(participant, lot)
        platform.start_auction()
        with self.assertRaises(ValueError):
            platform.place_bid(participant, 150.0)
        platform.stop_auction()

    def test_save_and_load(self):
        platform = TradingPlatform()
        participant1 = AuctionParticipant(nickname="Alice", balance=100.0)
        participant2 = AuctionParticipant(nickname="Bob", balance=200.0)
        lot1 = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        lot2 = Lot(name="Sculpture", description="A stunning sculpture", minimum_bid=200.0)
        platform.add(participant1, participant2, lot1, lot2)
        platform2 = TradingPlatform(load_on_init=True)
        self.assertEqual(platform.participants, platform2.participants)
        self.assertEqual(platform.lots, platform2.lots)


if __name__ == "__main__":
    unittest.main()