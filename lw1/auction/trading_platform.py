from transitions import Machine
from typing import List, Union

import threading
import json

from .utils import STATE_FILE, ensure_state, save
from . import Timer
from . import Lot
from . import AuctionParticipant
from . import Bid

class StateMachine:
    """
    A class representing a state machine for managing auction states.

    States:
        - preparing_for_auction: The auction is being prepared.
        - accepting_bids: The auction is accepting bids.
    """
    states = ['preparing_for_auction', 'accepting_bids']

    def __init__(self):
        """Initializes the state machine."""
        self.machine = Machine(model=self, states=StateMachine.states, initial='preparing_for_auction')
        # Define state transitions
        self.machine.add_transition(trigger='on_start_auction', source='preparing_for_auction', dest='accepting_bids')
        self.machine.add_transition(trigger='on_stop_auction', source='accepting_bids', dest='preparing_for_auction')


class TradingPlatform(StateMachine):
    """
    Class for managing an auction trading platform.

    This class handles auction lifecycle, including adding participants and lots,
    starting and stopping auctions, placing bids, and managing state persistence.

    Attributes:
        _participants (List[AuctionParticipant]): List of auction participants.
        _lots (List[Lot]): List of lots available for auction.
        _sold_lots (List[Lot]): List of lots that have been sold in auctions.
        _current_bid (Bid): The current highest bid in the active auction.
        _current_lot (Lot): The lot currently being auctioned.
        _timer (Timer): Timer for automatically stopping the auction.
        _timeout (int): Timeout duration in seconds for automatic auction stop.
        _lock (threading.Lock): Lock to ensure thread safety for state modifications.
    """

    def __init__(self, load_on_init=False):
        """
        Initializes the TradingPlatform.

        Args:
            load_on_init (bool, optional): If True, loads state from file on initialization. Defaults to False.
        """
        super().__init__()
        self._participants = []
        self._lots = []
        self._sold_lots = []
        self._current_bid = None
        self._current_lot = None
        self._timer = None
        self._timeout = 60
        self._lock = threading.Lock()
        self._timer_expired = False  # Add a flag to indicate timer expiration

        if load_on_init:
            self._load_state()

    @ensure_state('preparing_for_auction')
    @save
    def start_auction(self):
        """
        Starts a new auction.

        Transitions the state from 'preparing_for_auction' to 'accepting_bids'.
        Sets the first available lot as the current lot and starts the auction timer.

        Raises:
            ValueError: If there are no lots available to start the auction.
        """
        with self._lock:
            if not self._lots:
                raise ValueError("No lots available to start the auction")
            self.on_start_auction()
            self._current_lot = self._lots.pop(0)
            self._current_bid = Bid(self._current_lot)
            self._timer_expired = False  # Reset the flag when starting a new auction
            self._timer = Timer(timeout=self._timeout, callback=self._timer_callback)
            self._timer.start()

    @ensure_state('accepting_bids')
    @save
    def stop_auction(self):
        """
        Stops the current auction.

        Transitions the state from 'accepting_bids' to 'preparing_for_auction'.
        Determines the winner based on the current bid, transfers the lot,
        and resets the current bid and lot. Auto-saves the state after stopping.
        """
        with self._lock:
            self.on_stop_auction()
            if self._current_bid and self._current_bid.participant:
                self._current_bid.participant.lots.append(self._current_lot)
                self._current_bid.participant.balance -= self._current_bid.amount
                self._sold_lots.append(self._current_lot)
            else:
                self._lots.append(self._current_lot)
            self._current_bid = None
            self._current_lot = None
            if self._timer:
                self._timer.cancel()
            return True

    @ensure_state('preparing_for_auction')
    @save
    def add(self, *args: Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]):
        """
        Adds participants or lots to the trading platform.

        Can add single items or lists of items. Autosaves state after adding.

        Args:
            *args: Variable number of AuctionParticipant, Lot objects, or lists of these.

        Raises:
            TypeError: If an argument is of an unsupported type.
        """
        with self._lock:
            for arg in args:
                if isinstance(arg, (AuctionParticipant, Lot)):
                    self._add_single(arg)
                elif isinstance(arg, list):
                    for item in arg:
                        self._add_single(item)
                else:
                    raise TypeError(f"Unsupported type: {type(arg)}. Expected AuctionParticipant, Lot, or List")

    def _add_single(self, item: Union[AuctionParticipant, Lot]):
        """
        Adds a single participant or lot to the platform.

        Args:
            item (Union[AuctionParticipant, Lot]): The item to add.

        Raises:
            TypeError: If the item is not an AuctionParticipant or Lot.
            ValueError: If the lot is already sold.
        """
        if isinstance(item, AuctionParticipant):
            if item not in self._participants:
                self._participants.append(item)
        elif isinstance(item, Lot):
            if item in self._sold_lots:
                raise ValueError(f"Lot '{item.name}' is already sold and cannot be added again")
            if item not in self._lots:
                self._lots.append(item)
        else:
            raise TypeError(f"Unsupported type: {type(item)}. Expected AuctionParticipant or Lot")

    @ensure_state('preparing_for_auction')
    @save
    def remove(self, *args: Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]):
        """
        Removes participants and/or lots from the platform. Autosaves state after removal.

        Handles individual items or lists. If a participant is removed, their owned lots
        that are already sold are also removed from sold lots.

        Args:
            *args: Variable number of AuctionParticipant, Lot objects, or lists of these.

        Raises:
            ValueError: If a participant or lot is not found.
            TypeError: If an argument is of an unsupported type.
        """
        with self._lock:
            for arg in args:
                if isinstance(arg, (list, tuple, set)):  # Handle lists, tuples or sets
                    self.remove(*arg)  # Recursively process each element
                elif isinstance(arg, AuctionParticipant):
                    if arg not in self._participants:
                        raise ValueError(f"Participant '{arg}' not found")
                    # Remove sold lots owned by the participant
                    for lot in arg.lots:
                        if lot in self._sold_lots:
                            self._sold_lots.remove(lot)
                    self._participants.remove(arg)
                elif isinstance(arg, Lot):
                    if arg not in self._lots:
                        raise ValueError(f"Lot '{arg}' not found")
                    self._lots.remove(arg)
                else:
                    raise TypeError(f"Unsupported type: {type(arg)}. Expected AuctionParticipant, Lot, or an iterable of these types.")

    @ensure_state('accepting_bids')
    def _timer_callback(self):
        self._timer_expired = True
        self.stop_auction()

    @property
    def participants(self) -> List[AuctionParticipant]:
        """
        Returns the list of participants in the auction platform.
        """
        return self._participants

    @property
    def lots(self) -> List[Lot]:
        """
        Returns the list of lots available for auction.
        """
        return self._lots

    @property
    def sold_lots(self) -> List[Lot]:
        """
        Returns the list of lots that have been sold.
        """
        return self._sold_lots

    @property
    @ensure_state('preparing_for_auction')
    def timeout(self) -> int:
        """
        Returns the timeout duration for the auction timer in seconds.
        """
        return self._timeout

    @timeout.setter
    @ensure_state('preparing_for_auction')
    @save
    def timeout(self, value: int):
        """
        Sets the timeout duration for the auction timer and autosaves state.

        Args:
            value (int): The new timeout duration in seconds.
        """
        self._timeout = value

    @property
    @ensure_state('accepting_bids')
    def current_lot(self) -> Lot:
        """
        Returns the current lot being auctioned.
        """
        return self._current_lot

    @property
    @ensure_state('accepting_bids')
    def current_bid(self) -> Bid:
        """
        Returns the current highest bid.
        """
        return self._current_bid

    @ensure_state('accepting_bids')
    def place_bid(self, participant: AuctionParticipant, amount: float):
        """
        Places a bid for the current lot.

        Validates the bid amount and participant's balance, increases the current bid,
        and restarts the auction timer.

        Args:
            participant (AuctionParticipant): The participant placing the bid.
            amount (float): The bid amount.

        Raises:
            RuntimeError: If no current bid is available (auction not active).
            ValueError: If the bid amount is not higher than the current bid or exceeds balance.
        """
        with self._lock:
            if not self._current_bid:
                raise RuntimeError("No current bid available. Auction may not be active.")
            if amount <= self._current_bid.amount:
                raise ValueError("Bid amount must be greater than the current bid")
            if amount > participant.balance:
                raise ValueError("Bid amount exceeds participant balance")
            self._current_bid.increase_bid(amount, participant)  # Increase bid amount
            if self._timer:
                self._timer.cancel()  # Reset timer
            self._timer = Timer(timeout=self._timeout, callback=self.stop_auction)  # Start new timer
            self._timer.start()  # Start the timer

    def _save_state(self):
        """
        Saves the current state of the TradingPlatform to a JSON file.

        Includes participants, lots, sold lots, counters, and timeout settings.
        """
        state_data = {
            'participants_counter': AuctionParticipant._participants_counter,  # Changed to class variable
            'anonymous_counter': AuctionParticipant._anonymous_counter,  # Changed to class variable
            'lot_counter': Lot._lot_counter,  # Changed to class variable
            'timeout': self._timeout,
            'participants': [p._to_dict() for p in self._participants],
            'lots': [lot._to_dict() for lot in self._lots],
            'sold_lots': [lot._to_dict() for lot in self._sold_lots]
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=4)

    def _load_state(self):
        """
        Loads the state of the TradingPlatform from a JSON file.

        Restores participants, lots, sold lots, counters, and timeout settings
        from the saved state. Handles cases where the state file is not found or is corrupted.
        """
        try:
            with open(STATE_FILE, 'r') as f:
                state_data = json.load(f)

            max_lot_ID = 0
            max_participant_ID = 0

            loaded_lots_data = state_data.get('lots', [])
            loaded_lots = []
            for lot_data in loaded_lots_data:
                lot = Lot._from_dict(lot_data)
                max_lot_ID = max(max_lot_ID, lot.lot_id)
                loaded_lots.append(lot)
            self._lots = loaded_lots

            sold_lot_map = {}
            sold_lots_data = state_data.get('sold_lots', [])
            loaded_sold_lots = []
            for lot_data in sold_lots_data:
                lot = Lot._from_dict(lot_data)
                max_lot_ID = max(max_lot_ID, lot.lot_id)
                loaded_sold_lots.append(lot)
                sold_lot_map[lot.lot_id] = lot
            self._sold_lots = loaded_sold_lots

            loaded_participants_data = state_data.get('participants', [])
            loaded_participants = []
            for participant_data in loaded_participants_data:
                participant = AuctionParticipant._from_dict(participant_data, sold_lot_map)
                max_participant_ID = max(max_participant_ID, participant.participant_id)
                loaded_participants.append(participant)
            self._participants = loaded_participants

            AuctionParticipant._participants_counter = max(state_data.get('participants_counter', 0), max_participant_ID + 1)
            AuctionParticipant._anonymous_counter = state_data.get('anonymous_counter', 0)

            Lot._lot_counter = max(state_data.get('lot_counter', 0), max_lot_ID + 1)
            self._timeout = state_data.get('timeout', 60)

            print(f"State loaded from {STATE_FILE}")

        except FileNotFoundError:
            print(f"State file {STATE_FILE} not found. Starting with default state.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {STATE_FILE}. Starting with default state.")