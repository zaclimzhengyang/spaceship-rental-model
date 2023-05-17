from typing import NewType

from pydantic import BaseModel

from models.contract import Contract

ContractName = NewType("ContractName", str)


class SlimSolution(BaseModel):
    income: int
    path: list[ContractName]

    def add_contract(self, contract: Contract) -> "SlimSolution":
        """
        used to add a contract to a solution

        let's say at time 1, our best max profit is

        Solution(
            income=10,
            path=["Contract1"]
        )

        where we have taken Contract1 from time 0 to time 1 for an income of 10
        and at time 2, our best (un-updated max profit) is

        Solution(
            income=0,
            path=[]
        )

        and we encounter a new contract from time 1 to time 2 for an income of 20
        this is used to add the new contract to the solution, and update the new max profit
        """
        self.income += contract.price
        self.path.append(ContractName(contract.name))
        return self

    @staticmethod
    def empty() -> "SlimSolution":
        """
        helper smart constructor;
        specifically, to return an empty Solution object
        """
        return SlimSolution(income=0, path=[])

    @property
    def is_empty(self) -> bool:
        """
        helper method to check if a solution is empty
        """
        return self.income == 0 and len(self.path) == 0
