from auction import *

class MainMenu:
    def __init__(self):
        self._auction = TradingPlatform(load_on_init=True)

    def _preparing_for_auction_menu(self):
        print(('Select an action: '
               '1 - add participant, '
               '2 - del participant, '
               '3 - add lot, '
               '4 - del lot, '
               '5 - change timeout, '
               '6 - participants info, '
               '7 - lots info, '
               '8 - start auction, '
               'other - EXIT'))

        choice = input('[prep]: ')
        if choice == '1':
            self._add_participant()
        elif choice == '2':
            self._del_participant()
        elif choice == '3':
            self._add_lot()
        elif choice == '4':
            self._del_lot()
        elif choice == '5':
            self._change_timeout()
        elif choice == '6':
            self._participants_info()
        elif choice == '7':
            self._lots_info()
        elif choice == '8':
            try:
                self._auction.start_auction()
                self._accepting_bids_menu()
            except ValueError as e:
                print(e)
        else:
            return

        self._preparing_for_auction_menu()

    def _add_participant(self):
        nickname = input('Enter the participant`s nickname (default: anonymous_<ID>): ')
        balance = self._get_positive_float('Enter the participant`s balance (default: 0): ')
        if balance == -1:
            return
        participant = AuctionParticipant(nickname=nickname, balance=balance)
        self._auction.add(participant)

    def _del_participant(self):
        ID = self._get_positive_int('Enter the participant`s ID to delete: ')
        if ID == -1:
            return
        participant = next((p for p in self._auction.participants if p.participant_id == ID), None)
        if participant:
            self._auction.remove(participant)
        else:
            print(f"Participant with ID {ID} not found.")

    def _add_lot(self):
        name = input('Enter the name of the lot: ')
        description = input('Enter the description of the lot (default: None): ')
        minimum_bid = self._get_positive_float('Enter the minimum_bid of the lot (default: 0): ')
        if minimum_bid == -1:
            return
        lot = Lot(name=name, description=description, minimum_bid=minimum_bid)
        self._auction.add(lot)

    def _del_lot(self):
        ID = self._get_positive_int('Enter the lot ID to delete: ')
        if ID == -1:
            return
        lot = next((l for l in self._auction.lots if l.lot_id == ID), None)
        if lot:
            self._auction.remove(lot)
        else:
            print(f"Lot with ID {ID} not found.")

    def _change_timeout(self):
        new_timeout = self._get_positive_int('Enter the new timeout in seconds: ')
        if new_timeout == -1:
            return
        self._auction.timeout = new_timeout

    def _participants_info(self):
        for i in self._auction.participants:
            print(i)

    def _lots_info(self):
        for i in self._auction.lots:
            print(i)

    def _accepting_bids_menu(self):
        print(f"Current lot: {self._auction.current_lot}")
        while self._auction.state == 'accepting_bids':
            if self._auction._timer_expired:
                print("Timer expired. Auction stopped.")
                break
            ID = self._get_positive_int('Enter the ID of the participant who want to increase the bid: ')
            if self._auction._timer_expired:
                print("Timer expired. Auction stopped.")
                break
            if ID == -1:
                continue
            bid = self._get_positive_float('Enter the desired bid: ')
            if self._auction._timer_expired:
                print("Timer expired. Auction stopped.")
                break
            if bid == -1:
                continue
            participant = next((p for p in self._auction.participants if p.participant_id == ID), None)
            if participant:
                try:
                    self._auction.place_bid(participant, bid)
                except ValueError as e:
                    print(e)
            else:
                print(f"Participant with ID {ID} not found.")
            if input('Continue bidding? (y/n): ').lower() != 'y':
                self._auction.stop_auction()
                break

    def _get_positive_int(self, prompt):
        try:
            value = int(input(prompt))
            if value >= 0:
                return value
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")
        return -1

    def _get_positive_float(self, prompt):
        try:
            value = float(input(prompt))
            if value >= 0:
                return value
            else:
                print("Invalid input.")
        except ValueError:
            print("Invalid input.")
        return -1

    def start(self):
        self._preparing_for_auction_menu()


if __name__ == '__main__':
    main_menu = MainMenu()
    main_menu.start()
