from . import Lot
from . import AuctionParticipant


class Bid:
    """
    Class representing a bid in an auction.

    Args:
        lot (Lot): The auction lot for which the bid is placed.
        amount (float, optional): The bid amount. Defaults to 0.
        participant (AuctionParticipant, optional): The auction participant making the bid. Defaults to None.

    Raises:
        ValueError: If the bid amount is below the lot's minimum bid.
        ValueError: If the bid amount exceeds the participant's balance.
    """

    def __init__(self, lot: Lot, amount: float = 0, participant: AuctionParticipant = None):
        if participant and amount < lot.minimum_bid:
            raise ValueError("Bid amount is less than the minimum bid")
        if participant and amount > participant.balance:
            raise ValueError("Bid amount exceeds participant balance")
        self._amount = amount if participant else 0
        self._lot = lot
        self._participant = participant

    def __repr__(self):
        return f"Bid(lot={self._lot}, participant={self._participant}, amount={self._amount})"

    def __eq__(self, other) -> bool:
        """
        Checks if two bids are equal.

        Args:
            other: Another Bid object.

        Returns:
            bool: True if the bids have the same lot, participant, and amount; otherwise, False.
        """
        if not isinstance(other, Bid):
            return False
        return (self._lot == other._lot and
                self._participant == other._participant and
                self._amount == other._amount)

    def increase_bid(self, new_amount: float, participant: AuctionParticipant):
        """
        Increases the current bid amount if the new bid is valid.

        Args:
            new_amount (float): The new bid amount, which must be greater than the current bid.
            participant (AuctionParticipant): The auction participant placing the new bid.

        Raises:
            ValueError: If the new bid amount is not higher than the current bid.
            ValueError: If the new bid amount exceeds the participant's balance.
        """
        if new_amount <= self._amount:
            raise ValueError("New bid amount must be greater than the current bid")
        if new_amount > participant.balance:
            raise ValueError("Bid amount exceeds participant balance")
        self._amount = new_amount
        self._participant = participant

    @property
    def lot(self) -> Lot:
        """
        Returns the auction lot associated with this bid.
        """
        return self._lot

    @property
    def participant(self) -> AuctionParticipant:
        """
        Returns the participant who placed the bid.
        """
        return self._participant

    @property
    def amount(self) -> float:
        """
        Returns the current bid amount.
        """
        return self._amount