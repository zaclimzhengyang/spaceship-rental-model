from abc import abstractmethod, ABC

from models.contract import Contract
from models.solution import Solution


class ContractSelectorService(ABC):
    """
    represent a service, responsible for selecting from a list of contracts

    we are choosing from a list of spaceship contracts to take with the following constraints:
        - each contract can only be taken at the contract start hour
        - we only have 1 spaceship; we cannot take multiple contracts at the same time

    and our objective is to maximize profit
    """
    @abstractmethod
    def select_contracts(self, contracts: list[Contract]) -> Solution:
        pass