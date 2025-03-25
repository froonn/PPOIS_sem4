import unittest

from auction import AuctionParticipant, Lot

class TestAuctionParticipant(unittest.TestCase):
    def test_participant_creation_with_default_values(self):
        participant = AuctionParticipant()
        self.assertTrue(participant.nickname.startswith("anonymous_"))
        self.assertEqual(participant.balance, 0.0)
        self.assertEqual(participant.lots, [])

    def test_participant_creation_with_custom_values(self):
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        self.assertEqual(participant.nickname, "Alice")
        self.assertEqual(participant.balance, 100.0)
        self.assertEqual(participant.lots, [])

    def test_participant_equality_with_same_id(self):
        participant1 = AuctionParticipant(nickname="Alice", balance=100.0)
        participant2 = AuctionParticipant(nickname="Bob", balance=200.0)
        participant2._participant_id = participant1.participant_id
        self.assertEqual(participant1, participant2)

    def test_participant_inequality_with_different_ids(self):
        participant1 = AuctionParticipant(nickname="Alice", balance=100.0)
        participant2 = AuctionParticipant(nickname="Bob", balance=200.0)
        self.assertNotEqual(participant1, participant2)

    def test_participant_to_dict_representation(self):
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        participant.lots = [lot]
        expected_dict = {
            'nickname': "Alice",
            'balance': 100.0,
            'participant_id': participant.participant_id,
            'lots': [lot._to_dict()]
        }
        self.assertEqual(participant._to_dict(), expected_dict)

    def test_participant_from_dict_creation(self):
        lot = Lot(name="Painting", description="A beautiful painting", minimum_bid=100.0)
        lot_map = {lot.lot_id: lot}
        data = {
            'nickname': "Alice",
            'balance': 100.0,
            'participant_id': 1,
            'lots': [lot._to_dict()]
        }
        participant = AuctionParticipant._from_dict(data, lot_map)
        self.assertEqual(participant.nickname, "Alice")
        self.assertEqual(participant.balance, 100.0)
        self.assertEqual(participant.participant_id, 1)
        self.assertEqual(participant.lots, [lot])

if __name__ == "__main__":
    unittest.main()