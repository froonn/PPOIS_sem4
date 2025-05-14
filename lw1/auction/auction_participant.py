from typing import List

from . import Lot

class AuctionParticipant:
    """
    Class representing an auction participant.

    Args:
        nickname (str, optional): The participant's nickname. Defaults to 'anonymous' with a unique ID.
        balance (int, optional): The participant's initial balance. Defaults to 0.
    """
    _participants_counter = 0

    def __init__(self, nickname: str, balance: int = 0):
        self._nickname = nickname
        self._balance = balance
        self._lots = []
        self._participant_id = AuctionParticipant._participants_counter
        AuctionParticipant._participants_counter += 1

    def __repr__(self):
        return (f"AuctionParticipant(ID={self._participant_id}, "
                f"nickname='{self._nickname if self._nickname else f'anonymous_{self._participant_id}'}', balance={self._balance})")

    def __str__(self):
        return (f"ID: {self._participant_id:<3} nickname: {self._nickname if self._nickname else f'anonymous_{self._participant_id}':<15} "
                f"balance: {self._balance}")

    def __eq__(self, other) -> bool:
        """
        Compares two auction participants for equality.

        Args:
            other: Another AuctionParticipant object.

        Returns:
            bool: True if the participants' IDs are equal, otherwise False.
        """
        if isinstance(other, AuctionParticipant):
            return self._participant_id == other._participant_id
        return False

    @property
    def nickname(self) -> str:
        """
        Returns the participant's nickname.
        """
        return self._nickname if self._nickname else f'anonymous_{self._participant_id}'

    @nickname.setter
    def nickname(self, value: str):
        """
        Sets the participant's nickname.

        Args:
            value (str): The new nickname for the participant.
        """
        self._nickname = value

    @property
    def balance(self) -> int:
        """
        Returns the participant's balance.
        """
        return self._balance

    @balance.setter
    def balance(self, value: int):
        """
        Sets the participant's balance.

        Args:
            value (int): The new balance for the participant.
        """
        self._balance = value

    @property
    def lots(self) -> List[Lot]:
        """
        Returns the list of lots owned by the participant.
        """
        return self._lots

    @lots.setter
    def lots(self, value: List[Lot]):
        """
        Sets the list of lots owned by the participant.

        Args:
            value (List[Lot]): The new list of lots for the participant.
        """
        self._lots = value

    @property
    def participant_id(self) -> int:
        """
        Returns the unique ID of the participant.
        """
        return self._participant_id

    def _to_dict(self) -> dict:
        """
        Returns a dictionary representation of the AuctionParticipant.
        """
        return {
            'nickname': self._nickname,
            'balance': self._balance,
            'participant_id': self._participant_id,
            'lots': [lot._to_dict() for lot in self._lots]
        }

    @classmethod
    def _from_dict(cls, data, lot_map) -> 'AuctionParticipant':
        """
        Creates an AuctionParticipant object from a dictionary, using provided lot_map to resolve lot IDs.

        Args:
            data (dict): Dictionary containing participant data.
            lot_map (dict): Dictionary mapping lot IDs to Lot objects.

        Returns:
            AuctionParticipant: An AuctionParticipant object.
        """
        participant = cls(nickname=data['nickname'], balance=data['balance'])
        participant._lots = [lot_map[lot_data['lot_id']] for lot_data in data['lots']]
        participant._participant_id = data['participant_id']
        if participant._participant_id >= cls._participants_counter:
            cls._participants_counter = participant._participant_id + 1
        return participant

    @classmethod
    def participants_counter(cls) -> int:
        return AuctionParticipant._participants_counter