import unittest

from auction import AuctionParticipant, Lot


class TestAuctionParticipant(unittest.TestCase):
    def test_participant_creation_with_empty_nickname(self):
        participant = AuctionParticipant(nickname="", balance=50.0)
        self.assertTrue(participant.nickname.startswith("anonymous_"))
        self.assertEqual(participant.balance, 50.0)

    def test_participant_creation_with_negative_balance(self):
        participant = AuctionParticipant(nickname="NegativeBalance", balance=-100.0)
        self.assertEqual(participant.nickname, "NegativeBalance")
        self.assertEqual(participant.balance, -100.0)

    def test_participant_lots_assignment_with_empty_list(self):
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        participant.lots = []
        self.assertEqual(participant.lots, [])

    def test_participant_to_dict_with_no_lots(self):
        participant = AuctionParticipant(nickname="Alice", balance=100.0)
        expected_dict = {
            'nickname': "Alice",
            'balance': 100.0,
            'participant_id': participant.participant_id,
            'lots': []
        }
        self.assertEqual(participant._to_dict(), expected_dict)

    def test_participant_from_dict_with_empty_lots(self):
        data = {
            'nickname': "Alice",
            'balance': 100.0,
            'participant_id': 1,
            'lots': []
        }
        participant = AuctionParticipant._from_dict(data, lot_map={})
        self.assertEqual(participant.nickname, "Alice")
        self.assertEqual(participant.balance, 100.0)
        self.assertEqual(participant.participant_id, 1)
        self.assertEqual(participant.lots, [])


if __name__ == "__main__":
    unittest.main()
