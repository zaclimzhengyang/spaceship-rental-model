from sortedcontainers import SortedDict

from models.contract import Contract


class ContractPruningService:
    @staticmethod
    def should_prune_contract(
            prune_candidate: Contract, next_best_contract: Contract
    ) -> bool:
        """
        given two contracts;
        - a contract to prune at start time X
        - the next best contract to prune at the same start time X

        checks if we should prune a contract

        prune prune_candidate when
        1. if the candidate has start time and duration, but equal or lower profit than next_best_contract

        e.g.
        Contract 1, start time  0 hrs, duration 3 hrs, profit = 3
        (Prune) Contract 2, start time 0 hrs, duration 3 hrs, profit = 2

        2. if the candidate has same start time, but equal or longer duration than another contract with the same profit

        e.g.
        Contract 1, start time 0 hrs, duration 3 hrs, profit = 5
        Contract 2, start time 0 hrs, duration 4 hrs, profit = 6
        (Prune) Contract 3, start time 0 hrs, duration 5 hrs, profit = 6
        """
        if prune_candidate.start != next_best_contract.start:
            return False
        return (
            prune_candidate.price <= next_best_contract.price
            and prune_candidate.duration >= next_best_contract.duration
        )

    @staticmethod
    def prune_contracts(contracts: list[Contract]) -> list[Contract]:
        """
        by pruning N, the number of contracts, this optimizes our bottom-up dynamic programming implementation

        which has a time complexity of O(TN)
        where T is the number of unique start hours
        and N is the number of contracts

        worst case time complexity: O(LogN)
        - NLogN: sort the contracts according to the start, duration
        - NLogN: iterate each contract, grouping each contract by start time into a SortedDict (Balanced BST implementation)
            the key is the start time
            for a given contract, check if there is a contract with the same start time
            - with the same duration, but higher profits
            - with a shorter duration and higher profits

            if so, prune it by skipping it. else, add it as an unpruned contract
            - using SortedDict as a Balanced BST imeplemented list, keep the search and insertion to LogN time
        - worst case happens when all contracts have the same start time
        - all contracts end up being stored in the same BST, giving a high base for LogN search and insertion

        worst case space complexity: O(N), in the worst case, we don't prune any contracts
        - this happens when all the contracts have unique start time
        - worst case for memory specifically happens when all provided contracts have unique start time and duration
        - we end up storing all contracts' start and duration (as the key) into the dictionary


        start time to a priority queue of contracts which start at that time
        the priority queue orders the contract by duration
        """
        pruned_contracts_dict: SortedDict[int, SortedDict[int, Contract]] = SortedDict()

        """
        O(NLogN)
        sort the contracts by ascending start, tie break by ascending duration, descending price
        this makes it easier for pruning
        by processing contracts in ascending duration for each start time, and the more promising contracts first
        we won't encounter a contract with shorter duration after processing contracts with longer durations
        in short, we don't have to worry about removing existing sub-par contracts from the final result
        """
        contracts.sort(key=lambda x: (x.start, x.duration, -x.price))

        # O(NLogN)
        for contract in contracts:
            """
            the SortedList is implemented with a self balancing binary search tree
            
            Q: why do we use a binary search tree here?
            A: we will be inserting a contract into it, and searching for the next shortest contract often
            it has a O(LogN) time complexity for both operations
            """
            existing_contracts_at_start: SortedDict[int, Contract] = pruned_contracts_dict.get(contract.start, SortedDict())

            """
            find a contract with the same duration
            
            if we already have a contract which have the same duration,
            check if the current contract has a better profit
            if yes, prune the old contract
            
            O(LogN)
            """
            if (contract.duration in existing_contracts_at_start and
                    contract.price > existing_contracts_at_start[contract.duration].price):
                # O(LogN) to replace the existing contract with a new one
                existing_contracts_at_start[contract.duration] = contract
                # update the top-level pruned_contracts_dict
                pruned_contracts_dict[contract.start] = existing_contracts_at_start
            elif (contract.duration not in existing_contracts_at_start
                    and len(existing_contracts_at_start) > 0):
                """
                find a contract with the longest duration, just slightly less than the current contract's duration
                {
                    1: Contract(start=0, duration=2, price=10)
                }
                given a new contract: Contract(start=0, duration=3, price=20)
                index_to_insert_contract = 1

                given a new contract: Contract(start=0, duration=1, price=20)
                index_to_insert_contract = 0

                O(LogN)
                """
                index_to_insert_contract: int = existing_contracts_at_start.bisect_left(contract.duration)
                if index_to_insert_contract > 0:
                    # there is a contract with a duration shorter than it
                    index_to_contract_with_shorter_duration = index_to_insert_contract - 1
                    next_best_contract_candidate: Contract = existing_contracts_at_start.peekitem(index_to_contract_with_shorter_duration)[1]
                    if next_best_contract_candidate.duration < contract.duration:
                        """
                        prune the current contract (e.g. skip it)
                        if the existing contract's price with shorter duration is equal or more than the current contract
                        """
                        if contract.price > next_best_contract_candidate.price:
                            existing_contracts_at_start[contract.duration] = contract
                            # update the top-level pruned_contracts_dict
                            pruned_contracts_dict[contract.start] = existing_contracts_at_start
                else:
                    # there is no contract with shorter duration, insert the contract
                    existing_contracts_at_start[contract.duration] = contract
                    # update the top-level pruned_contracts_dict
                    pruned_contracts_dict[contract.start] = existing_contracts_at_start
            elif len(existing_contracts_at_start) == 0:
                """
                there is no existing contract at this start time
                add the contract in
                """
                existing_contracts_at_start[contract.duration] = contract
                # update the top-level pruned_contracts_dict
                pruned_contracts_dict[contract.start] = existing_contracts_at_start

        """
        iterate through the remaining pruned contracts in pruned_contracts_dict, and flatten them into a list
        the flattened list should be ordered such that the contracts are ordered by (start time, duration)
        this is easily done, as we are using SortedDict (a BST)
        
        worst case:
        - all contracts are all of the same start time.
        
        given N is the number of contracts, and all N contracts have the same start time
        - all contracts are in the same SortedDict (binary tree)
        
        time Complexity: O(NLogN)
        """
        final_result: list[Contract] = []
        for _, duration_to_contract_bst in pruned_contracts_dict.items():
            for _, contract in duration_to_contract_bst.items():
                final_result.append(contract)

        return final_result

if __name__ == "__main__":
    contract_pruning_service = ContractPruningService()
    contract1 = Contract(name="Contract1",start=0,duration=3,price=5)
    contract2 = Contract(name="Contract2",start=0,duration=6,price=4)
    should_prune = contract_pruning_service.should_prune_contract(contract1, contract2)
    print(should_prune)