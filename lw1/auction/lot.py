class Lot:
    """
    Class representing an auction lot.

    Args:
        name (str, optional): The name of the lot. Defaults to None.
        description (str, optional): The description of the lot. Defaults to None.
        minimum_bid (float, optional): The minimum bid for the lot. Defaults to 0.
    """
    _lot_counter = 0

    def __init__(self, name: str = None, description: str = None, minimum_bid: float = 0):
        """
        Initializes a new Lot instance.

        Args:
            name (str, optional): The name of the lot. Defaults to None.
            description (str, optional): The description of the lot. Defaults to None.
            minimum_bid (float, optional): The minimum bid for the lot. Defaults to 0.
        """
        self._name = name
        self._description = description
        self._minimum_bid = minimum_bid
        self._lot_id = Lot._lot_counter
        Lot._lot_counter += 1

    def __repr__(self):
        """
        Returns a string representation of the Lot.

        Returns:
            str: A string representation of the Lot.
        """
        return (f"Lot(ID={self._lot_id}, name='{self._name}', "
                f"description='{self._description}', minimum_bid={self._minimum_bid})")

    def __str__(self):
        return (f"ID: {self._lot_id:<3} name: {self._name:<10} "
                f"min bid: {self._minimum_bid:<10} description: {self._description} ")

    def __eq__(self, other) -> bool:
        """
        Compares two lots for equality.

        Args:
            other: Another Lot object.

        Returns:
            bool: True if the lots' IDs are equal, otherwise False.
        """
        if not isinstance(other, Lot):
            return False
        return self._lot_id == other._lot_id

    @property
    def name(self) -> str:
        """
        Returns the name of the lot.

        Returns:
            str: The name of the lot.
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Returns the description of the lot.

        Returns:
            str: The description of the lot.
        """
        return self._description

    @property
    def minimum_bid(self) -> float:
        """
        Returns the minimum bid for the lot.

        Returns:
            float: The minimum bid for the lot.
        """
        return self._minimum_bid

    @property
    def lot_id(self) -> int:
        """
        Returns the unique ID of the lot.

        Returns:
            int: The unique ID of the lot.
        """
        return self._lot_id

    def _to_dict(self) -> dict:
        """
        Returns a dictionary representation of the Lot.

        Returns:
            dict: A dictionary representation of the Lot.
        """
        return {
            'name': self._name,
            'description': self._description,
            'minimum_bid': self._minimum_bid,
            'lot_id': self._lot_id
        }

    @classmethod
    def _from_dict(cls, data: dict) -> 'Lot':
        """
        Creates a Lot object from a dictionary.

        Args:
            data (dict): A dictionary containing the lot data.

        Returns:
            Lot: A Lot object created from the dictionary.
        """
        lot = cls(name=data['name'], description=data['description'],
                  minimum_bid=data['minimum_bid'])
        lot._lot_id = data['lot_id']
        if lot._lot_id >= cls._lot_counter:
            cls._lot_counter = lot._lot_id + 1
        return lot

    @classmethod
    def lot_counter(cls) -> int:
        """
        Returns the current lot counter.

        Returns:
            int: The current lot counter.
        """
        return Lot._lot_counter