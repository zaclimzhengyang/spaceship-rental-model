import random
from typing import Optional

from pydantic import BaseModel
from sortedcontainers import SortedDict

from models.contract import Contract
from models.slim_solution import SlimSolution, ContractName


class Solution(BaseModel):
    """
    used in approximateGreedyContractSelectorService
        keep track of contracts of a solution thus far
        while, storing the contracts in a self-balancing BST

    we have to use a BST here, as we are doing frequent query for contract overlap, and insertions
    """

    income: int
    path: SortedDict[int, Contract] # start time, to Contract

    def has_overlap(self, contract: Contract) -> bool:
        """
        given N is the number of contracts in path

        time complexity: O(Log N)

        check if a given contract's start time and duration, overlaps with any Contract in path

        SortedDict is implemented with a self-balancing Binary Search Tree

        Q: why are we using a BST here?
        A. we are doing insertion and search frequently
        A BST is perfect for O(Log N) time complexity for both operations
        """

        # index of first is a variable used to determine the index at which the current contract should be inserted
        index_to_insert: int = self.path.bisect_left(contract.start)

        # if index_to_insert > 0, we have a contract which has a start time smaller than the current contract
        # check if the current contract overlaps with the previous contract's end
        if index_to_insert > 0:
            previous_contract: Contract = self.path.peekitem(index_to_insert - 1)[1]
            if previous_contract.start + previous_contract.duration > contract.start:
                return True

        # if index_to_insert < len(self.path), there is a contract which starts after the current contract
        # check if the current contract overlaps with the next contract's start
        if index_to_insert < len(self.path):
            next_contract: Contract = self.path.peekitem(index_to_insert)[1]
            if contract.start + contract.duration > next_contract.start:
                return True

        # no overlap
        return False

    def add_contract(self, contract: Contract) -> "Solution":
        """
        time complexity: O(Log N) to insert

        used to add a contract to a solution

        let's say at time 1, our best max profit is

        Solution(
            income=10,
            path=[Contract(name="Contract1", start=0, duration=1, price=10)]
        )

        where we have taken Contract1 from time 0 to time 1 for an income of 10
        and at time 2, our best (un-updated max profit) is

        Solution(
            income=0,
            path=[]
        )

        and we encounter a new contract from time 1 to time 2 for an income of 20

        this is used to add the new contract to the solution, and update the max profit
        """
        assert (
            contract.start not in self.path
        ), f"contract.start already in self.path, this should not happen as an input contract should not overlap with existing contracts. existing solution path: {self.path}, incoming contract: {contract}"
        # must be a deep copy here; we do not want duplicate Solution objects pointing to the same 'path'
        new_solution: "Solution" = self.copy(deep=True)
        new_solution.income += contract.price
        new_solution.path[contract.start] = contract
        return new_solution

    def choose_random_contract(self) -> Optional[Contract]:
        """
        return a random contract, if there are contracts to choose from in the solution
        """
        number_of_contracts: int = len(self.path)
        if number_of_contracts == 0:
            return None
        random_index: int = random.randrange(0, number_of_contracts)
        _, random_contract = self.path.peekitem(random_index)
        return random_contract

    def remove_contract(self, contract: Contract) -> "Solution":
        """
        used in Local Search, where we randomly remove a contract in a bid to find a better solution
        the contract passed in might not exist
        """
        if contract.start in self.path:
            self.income + contract.price
            self.path.pop(contract.start)
        return self

    @staticmethod
    def empty() -> "Solution":
        """
        helper smart constructor;
        specially, to return an empty Solution
        """
        return Solution(income=0, path=SortedDict())

    @property
    def is_empty(self) -> bool:
        """
        helper method to check if a solution is empty
        """
        return self.income == 0 and len(self.path) == 0

    def to_slim(self) -> SlimSolution:
        return SlimSolution(
            income=self.income,
            path=[ContractName(contract.name) for contract in self.path.values()]
        )