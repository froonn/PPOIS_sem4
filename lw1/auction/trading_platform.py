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
        - auction_paused: The auction is temporarily paused.
        - auction_ended: The auction has ended.
    """
    states = ['preparing_for_auction', 'accepting_bids', 'auction_paused']

    def __init__(self) -> None:
        """
        Initializes the state machine with the initial state 'preparing_for_auction'.
        """
        self.machine = Machine(model=self, states=StateMachine.states, initial='preparing_for_auction')

        self.machine.add_transition(trigger='on_start_auction', source='preparing_for_auction', dest='accepting_bids')
        self.machine.add_transition(trigger='on_end_auction', source='accepting_bids', dest='preparing_for_auction')
        self.machine.add_transition(trigger='on_end_auction', source='auction_paused', dest='preparing_for_auction')
        self.machine.add_transition(trigger='on_pause_auction', source='accepting_bids', dest='auction_paused')
        self.machine.add_transition(trigger='on_resume_auction', source='auction_paused', dest='accepting_bids')
        self.machine.add_transition(trigger='on_restart_auction', source='auction_paused', dest='accepting_bids')
        self.machine.add_transition(trigger='on_abort_auction', source='auction_paused', dest='preparing_for_auction')


class TradingPlatform(StateMachine):
    """
    A class representing a trading platform for managing auctions, inheriting from StateMachine.

    Attributes:
        _participants (List[AuctionParticipant]): List of auction participants.
        _lots (List[Lot]): List of lots available for auction.
        _sold_lots (List[Lot]): List of sold lots.
        _current_bid (Bid): The current bid in the auction.
        _current_lot (Lot): The current lot being auctioned.
        _timer (Timer): Timer for managing auction timeouts.
        _timeout (int): Timeout duration for the auction.
        _lock (threading.Lock): Lock for thread-safe operations.
    """

    def __init__(self, load_on_init: bool = False) -> None:
        """
        Initializes the trading platform and optionally loads the state from a file.

        Args:
            load_on_init (bool): Whether to load the state on initialization.
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

        if load_on_init:
            self._load_state()

    @ensure_state('preparing_for_auction')
    @save
    def start_auction(self) -> None:
        """
        Starts the auction by transitioning to the 'accepting_bids' state and initializing the first lot and bid.
        """
        if not self._lots:
            raise ValueError("No lots available to start the auction")
        if not self._participants:
            raise ValueError("No participants available to start the auction")
        self.on_start_auction()
        self._current_lot = self._lots.pop(0)
        self._current_bid = Bid(self._current_lot)
        self._timer = Timer(timeout=self._timeout, callback=self._timer_callback)
        self._timer.start()

    @ensure_state('accepting_bids', 'auction_paused')
    @save
    def end_auction(self) -> None:
        """
        Stops the auction by transitioning to the 'preparing_for_auction' state and processing the current bid.
        """
        self.on_end_auction()
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

    @ensure_state('accepting_bids')
    def pause_auction(self) -> None:
        self.on_pause_auction()
        if self._timer:
            self._timer.cancel()

    @ensure_state('auction_paused')
    def resume_auction(self) -> None:
        self.on_resume_auction()
        self._timer = Timer(timeout=self._timeout, callback=self._timer_callback)
        self._timer.start()

    @ensure_state('auction_paused')
    def restart_auction(self) -> None:
        self.on_restart_auction()
        self._current_bid = Bid(self._current_lot)
        self._timer = Timer(timeout=self._timeout, callback=self._timer_callback)
        self._timer.start()

    @ensure_state('auction_paused')
    @save
    def abort_auction(self) -> None:
        self.on_abort_auction()
        self.add(self._current_lot)
        self._current_bid = None
        self._current_lot = None
        if self._timer:
            self._timer.cancel()

    @ensure_state('preparing_for_auction')
    @save
    def add(self, *args: Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]) -> None:
        """
        Adds participants or lots to the auction.

        Args:
            *args (Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]): Participants or lots to add.
        """
        for arg in args:
            if isinstance(arg, (AuctionParticipant, Lot)):
                self._add_single(arg)
            elif isinstance(arg, list):
                for item in arg:
                    self._add_single(item)
            else:
                raise TypeError(f"Unsupported type: {type(arg)}. Expected AuctionParticipant, Lot, or List")

    def _add_single(self, item: Union[AuctionParticipant, Lot]) -> None:
        """
        Adds a single participant or lot to the auction.

        Args:
            item (Union[AuctionParticipant, Lot]): Participant or lot to add.
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
    def remove(self, *args: Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]) -> None:
        """
        Removes participants or lots from the auction.

        Args:
            *args (Union[AuctionParticipant, Lot, List[Union[AuctionParticipant, Lot]]]): Participants or lots to remove.
        """
        for arg in args:
            if isinstance(arg, (list, tuple, set)):
                self.remove(*arg)
            elif isinstance(arg, AuctionParticipant):
                if arg not in self._participants:
                    raise ValueError(f"Participant '{arg}' not found")
                for lot in arg.lots:
                    if lot in self._sold_lots:
                        self._sold_lots.remove(lot)
                self._participants.remove(arg)
            elif isinstance(arg, Lot):
                if arg not in self._lots:
                    raise ValueError(f"Lot '{arg}' not found")
                self._lots.remove(arg)
            else:
                raise TypeError(
                    f"Unsupported type: {type(arg)}. Expected AuctionParticipant, Lot, or an iterable of these types.")

    @ensure_state('accepting_bids')
    def _timer_callback(self) -> None:
        """
        Callback function for the timer, stops the auction when the timer expires.
        """
        self.end_auction()

    @property
    def participants(self) -> List[AuctionParticipant]:
        """
        Returns the list of auction participants.

        Returns:
            List[AuctionParticipant]: List of auction participants.
        """
        return self._participants

    @property
    def lots(self) -> List[Lot]:
        """
        Returns the list of lots available for auction.

        Returns:
            List[Lot]: List of lots available for auction.
        """
        return self._lots

    @property
    def sold_lots(self) -> List[Lot]:
        """
        Returns the list of sold lots.

        Returns:
            List[Lot]: List of sold lots.
        """
        return self._sold_lots

    @property
    @ensure_state('preparing_for_auction')
    def timeout(self) -> int:
        """
        Returns the timeout duration for the auction.

        Returns:
            int: Timeout duration for the auction.
        """
        return self._timeout

    @timeout.setter
    @ensure_state('preparing_for_auction')
    @save
    def timeout(self, value: int) -> None:
        """
        Sets the timeout duration for the auction.

        Args:
            value (int): Timeout duration for the auction.
        """
        self._timeout = value

    @property
    @ensure_state('accepting_bids')
    def current_lot(self) -> Lot:
        """
        Returns the current lot being auctioned.

        Returns:
            Lot: The current lot being auctioned.
        """
        return self._current_lot

    @property
    @ensure_state('accepting_bids')
    def current_bid(self) -> Bid:
        """
        Returns the current bid in the auction.

        Returns:
            Bid: The current bid in the auction.
        """
        return self._current_bid

    @ensure_state('accepting_bids')
    def place_bid(self, participant: AuctionParticipant, amount: int) -> None:
        """
        Places a bid on the current lot.

        Args:
            participant (AuctionParticipant): The participant placing the bid.
            amount (int): The bid amount.

        Raises:
            RuntimeError: If no current bid is available (auction not active).
            ValueError: If the bid amount is not higher than the current bid or exceeds balance.
        """
        if not self._current_bid:
            raise RuntimeError("No current bid available. Auction may not be active.")
        if amount <= self._current_bid.amount:
            raise ValueError("Bid amount must be greater than the current bid")
        if amount > participant.balance:
            raise ValueError("Bid amount exceeds participant balance")
        if amount < self._current_lot.minimum_bid:
            raise ValueError("")
        self._current_bid.increase_bid(amount, participant)
        if self._timer:
            self._timer.cancel()
        self._timer = Timer(timeout=self._timeout, callback=self.end_auction)
        self._timer.start()

    def _save_state(self) -> None:
        """
        Saves the current state of the auction to a file.
        """
        state_data = {
            'participants_counter': AuctionParticipant._participants_counter,
            'lot_counter': Lot._lot_counter,
            'timeout': self._timeout,
            'participants': [p._to_dict() for p in self._participants],
            'lots': [lot._to_dict() for lot in self._lots],
            'sold_lots': [lot._to_dict() for lot in self._sold_lots]
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state_data, f, indent=4)

    def _load_state(self) -> None:
        """
        Loads the state of the auction from a file.
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

            AuctionParticipant._participants_counter = max(state_data.get('participants_counter', 0),
                                                           max_participant_ID + 1)

            Lot._lot_counter = max(state_data.get('lot_counter', 0), max_lot_ID + 1)
            self._timeout = state_data.get('timeout', 60)

            print(f"State loaded from {STATE_FILE}")

        except FileNotFoundError:
            print(f"State file {STATE_FILE} not found. Starting with default state.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {STATE_FILE}. Starting with default state.")
