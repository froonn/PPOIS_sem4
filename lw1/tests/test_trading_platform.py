import unittest

from auction import TradingPlatform, AuctionParticipant, Lot, Bid

class TestTradingPlatform(unittest.TestCase):

    def test_start_auction_with_no_lots_raises_error(self):
        platform = TradingPlatform()
        with self.assertRaises(ValueError):
            platform.start_auction()

    def test_start_auction_initializes_first_lot_and_bid(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.timeout = 0.1
        platform.start_auction()
        self.assertEqual(platform.current_lot, lot)
        self.assertIsNotNone(platform.current_bid)

    def test_end_auction_processes_current_bid(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=200.0)
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(participant, lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.place_bid(participant, 150.0)
        platform.end_auction()
        self.assertIn(lot, participant.lots)
        self.assertEqual(participant.balance, 50.0)
        self.assertIn(lot, platform.sold_lots)

    def test_pause_auction_stops_timer(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.pause_auction()
        self.assertEqual(platform.state, 'auction_paused')

    def test_resume_auction_restarts_timer(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.pause_auction()
        platform.resume_auction()
        self.assertEqual(platform.state, 'accepting_bids')

    def test_restart_auction_resets_current_bid(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.pause_auction()
        platform.restart_auction()
        self.assertIsNotNone(platform.current_bid)

    def test_resume_auction_resets_current_lot_and_bid(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.pause_auction()
        platform.resume_auction()
        self.assertEqual(platform.current_lot, lot)
        self.assertIsNone(platform.current_bid.participant)

    def test_add_participant_to_auction(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=200.0)
        platform.add(participant)
        self.assertIn(participant, platform.participants)

    def test_add_lot_to_auction(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        self.assertIn(lot, platform.lots)

    def test_remove_participant_from_auction(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=200.0)
        platform.add(participant)
        platform.remove(participant)
        self.assertNotIn(participant, platform.participants)

    def test_remove_lot_from_auction(self):
        platform = TradingPlatform()
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(lot)
        platform.remove(lot)
        self.assertNotIn(lot, platform.lots)

    def test_place_bid_with_insufficient_balance_raises_error(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=50.0)
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(participant, lot)
        platform.timeout = 0.1
        platform.start_auction()
        with self.assertRaises(ValueError):
            platform.place_bid(participant, 150.0)

    def test_place_bid_with_lower_amount_raises_error(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=200.0)
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(participant, lot)
        platform.timeout = 0.1
        platform.start_auction()
        platform.place_bid(participant, 150.0)
        with self.assertRaises(ValueError):
            platform.place_bid(participant, 100.0)

    def test_save_and_load(self):
        platform = TradingPlatform()
        participant = AuctionParticipant(nickname="Alice", balance=200.0)
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        platform.add(participant, lot)
        platform.timeout = 0.1

        platform2 = TradingPlatform(load_on_init=True)
        self.assertEqual(platform2.participants[0].nickname, "Alice")
        self.assertEqual(platform2.lots[0].name, "Painting")

if __name__ == "__main__":
    unittest.main()