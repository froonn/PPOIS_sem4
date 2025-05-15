from auction import *


def get_positive_int(prompt):
    value = int(input(prompt))
    if value >= 0:
        return value
    else:
        raise ValueError('Value must be positive')


class MainMenu:
    def __init__(self):
        self._auction = TradingPlatform(load_on_init=True)

    def _preparing_for_auction_menu(self):
        while True:
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
                break

    def _add_participant(self):
        nickname = input('Enter the participant`s nickname (default: anonymous_<ID>): ')
        try:
            balance = get_positive_int('Enter the participant`s balance (default: 0): ')
        except ValueError as e:
            print(e)
            return
        participant = AuctionParticipant(nickname=nickname, balance=balance)
        self._auction.add(participant)

    def _del_participant(self):
        try:
            ID = get_positive_int('Enter the participant`s ID to delete: ')
        except ValueError as e:
            print(e)
            return
        participant = next((p for p in self._auction.participants if p.participant_id == ID), None)
        if participant:
            self._auction.remove(participant)
        else:
            print(f"Participant with ID {ID} not found.")

    def _add_lot(self):
        name = input('Enter the name of the lot: ')
        if not name:
            print("Lot name cannot be empty.")
            return
        description = input('Enter the description of the lot (default: None): ')
        try:
            minimum_bid = get_positive_int('Enter the minimum_bid of the lot (default: 0): ')
        except ValueError as e:
            print(e)
            return
        if minimum_bid == -1:
            return
        lot = Lot(name=name, description=description, minimum_bid=minimum_bid)
        self._auction.add(lot)

    def _del_lot(self):
        try:
            ID = get_positive_int('Enter the lot ID to delete: ')
        except ValueError as e:
            print(e)
            return
        lot = next((l for l in self._auction.lots if l.lot_id == ID), None)
        if lot:
            self._auction.remove(lot)
        else:
            print(f"Lot with ID {ID} not found.")

    def _change_timeout(self):
        try:
            new_timeout = get_positive_int('Enter the new timeout in seconds: ')
        except ValueError as e:
            print(e)
            return
        if new_timeout > 10000:
            print(f"Timeout cannot be greater than 10000.")
        self._auction.timeout = new_timeout

    def _participants_info(self):
        if len(self._auction.participants) == 0:
            print("No participants found.")
            return
        for i in self._auction.participants:
            print(i)

    def _lots_info(self):
        if len(self._auction.lots) == 0:
            print("No lots found.")
            return
        for i in self._auction.lots:
            print(i)

    def _accepting_bids_menu(self):

        print(f"Current lot: {self._auction.current_lot}")

        print('Participants info:')
        self._participants_info()
        winner = None

        try:
            while True:
                try:
                    ID = get_positive_int('Enter the ID of the participant who want to increase the bid: ')
                except ValueError as e:
                    print(e)
                    return

                participant = next((p for p in self._auction.participants if p.participant_id == ID), None)
                if not participant:
                    print(f"Participant with ID {ID} not found.")
                    continue

                try:
                    bid = get_positive_int('Enter the desired bid: ')
                except ValueError as e:
                    print(e)
                    return

                if bid == -1:
                    continue

                try:
                    self._auction.place_bid(participant, bid)
                except ValueError as e:
                    print(e)

                user_choice = input('Choose an action: (c)ontinue bidding, (p)ause auction, (e)nd auction: ').lower()

                if user_choice == 'c':
                    continue
                elif user_choice == 'p':
                    self._auction.pause_auction()

                    user_choice = input(
                        'Choose an action: (c)ontinue auction, (r)estart auction, (a)bort auction, (e)nd auction: ').lower()
                    if user_choice == 'c':
                        self._auction.resume_auction()
                    elif user_choice == 'r':
                        self._auction.restart_auction()
                    elif user_choice == 'a':
                        self._auction.abort_auction()
                        break
                    else:
                        winner = self._auction.end_auction()
                        break
                else:
                    winner = self._auction.end_auction()
                    break
        except RuntimeError:
            print('Timer expired. Auction ended!')
        if self._auction.winner:
            print(f"Winner: {self._auction.winner.nickname}")
        else:
            print("Auction ended without a winner.")

    def start(self):
        self._preparing_for_auction_menu()


if __name__ == '__main__':
    main_menu = MainMenu()
    main_menu.start()
