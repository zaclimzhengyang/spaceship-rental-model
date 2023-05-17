import bisect

from models.contract import Contract
from models.solution import Solution
from services.contract_pruning_service import ContractPruningService
from services.contractor_selector_service import ContractSelectorService


class DefiniteContractSelectorService(ContractSelectorService):
    """
    implementation 1: responsible for selecting the best contracts from a set of contracts,
    to maximize profit at the end of time

    drawback:
        - our graph of scenarios (considering we do not employ pruning, or memoization yet)
          will be a tree with 2^N nodes, where N is the number of contracts
        - even with pruning and memoization, it will still be pretty expensive to calculate:
          it has a worst case time complexity of O(TN),
          where T is the number of unique start time, N is the number of contractor

          Q: if it is so inefficient, why are we still implementing this?
          A: we will be using this to get the global minima / definite solution,
             this let us cross validate which is the best one.

    implementation: bottom-up dynamic programming with memoization
        - to be specific, we will be calculating the max profit solution for specifically the earlier
          end time belonging to each contract before we continue to calculate that for the later time frames

         e.g. we will calculate the best profit from t=0 to t=10,
         before we continue to calculate that for the later time frames

        specifically, we will be using a 1D dict[int, Solution] dp dictionary,
        where dp[0] represents the smaller solution of max profit at time 0

        Q: why not use a list[int]?
        A: the time range can be quite large
        if we use a list[int], this 1D array risks being sparsely populated,
        and use up unnecessary memory
        - specifically, start_time - 1 is the index, and if it does not correspond with any start time
          of a contract, it will be empty

        so we use a dictionary to only use the memory we need
    """

    def select_contracts(self, contracts: list[Contract]) -> Solution:
        """
        N is the number of contacts
        worst case time complexity: O(N + NlogN + TN) = O(TN)

        technically, the worst case time complexity for key-value access is O(N),
        specifically for a dictionary with a high load factor
        but, lets keep it simple for the worst case time complexity, and say it is O(1)

        step 1: sort the contract in ascending order, smaller start time first
            - invitation: we need the smaller sub problem of max profit at an earlier time
            - to calculate the solution of max profit at a later time

        step 2: iterate through all the sorted contracts to calculate the solution of max profit
                at a given end time of a contract
            - use a DP dictionary table, with the bottom solution; the best profit from t=0 to t=contract.duration
            - adjacency list, with the best contract from t=0 to t=contract.duration

        Q: lets say we have the following contracts
            [ (0,1), (2,3), (4,5), (0,12) ]
        do we really need to calculate the best solution from t=0 to t=12?
        A: no, when calculating the solution of max profits at a given end time of a contract...
           we need the smaller sub problem of max profits at the given start time of the contract

           specifically, we have a contract from (2,3) we update the max profit at end time 3 as follows

        dp_dict[3] = max(dp_dict[3], dp_dict[2] + contract_price)

        this means, we can keep track of the unique start timings that appeared using a list
        { 0, 2, 4 }

        and only iterate these to update all solutions for start timings greater than
        - dp_dict[4] = max(dp_dict[4], dp_dict[3])

        memoizes the solutions to the smaller sub problems
        the maximum profit up till time t, where t is of type 'int', and is the key of the dictionary
        """
        if len(contracts) == 0:
            return Solution.empty()

        dp: dict[int, Solution] = {}

        """
        N is the number of contracts
        prune contracts, and then sort them by ascending start and duration
        time complexity: O(LogN)
        """
        pruned_contracts: list[Contract] = ContractPruningService.prune_contracts(contracts)
        end_of_duration: int = max(
            map(lambda x: x.start + x.duration, pruned_contracts)
        )

        """        
        time Complexity: O(N)

        get the unique start hours in the contracts; 

        this is sorted ascending, and used for binary searching the earliest contract start time / latest contract end time, after a given contract end time

        intuition:

        lets say we have the following contracts
        [(1, 2), (3, 4), (4, 5)]

        after we calculate the max profits at contract end time 2, 
        we will be using this to update the max profits at contract start time 3 and 4, and end time 5

        these updated max profits at contract start time 3 and 4 will be used to calculate the max profits at contract end time 4 and 5.
        """
        start_hours: list[int] = list(
            sorted(set([contract.start for contract in pruned_contracts]))
        )

        """
        add the latest contract end time too, so we update the max profits solution at the end of time 
        every time we calculate the max profits at a given contract end time. 
        """
        start_hours.append(end_of_duration)

        """
        time complexity: O(T * N)
        iterate through all contracts to populate the DP table
        """
        for contract in pruned_contracts:
            curr_contract_end_hour: int = contract.start + contract.duration
            solution_at_end_hour: Solution = dp.get(
                curr_contract_end_hour, Solution.empty()
            )
            """
            we use the smaller solution of max profits at the start hour of each contract
            to calculate the max profits at the end hour of each contract
            after we calculate a new solution at e.g t = 10...
            we should use it to update all solutions at the unique start hour of each contracts, which comes after t = 10
            """
            solution_at_start_hour: Solution = dp.get(contract.start, Solution.empty())

            # candidate best profits at end hour
            candidate_best_profits_at_end_hour: int = (
                    solution_at_start_hour.income + contract.price
            )

            if candidate_best_profits_at_end_hour > solution_at_end_hour.income:
                """
                form of pruning:
                - we only use the current contract if it can improve the current max profits at the contract's end hour

                this update is expensive:
                - we also use this new solution to update the max profits for all start hours after this contract's end hour
                and the max profits at the latest contract end time.
                """
                new_solution_at_contract_end_hour: Solution = (
                    solution_at_start_hour.add_contract(contract)
                )
                # update the dp table with the better solution
                dp[curr_contract_end_hour] = new_solution_at_contract_end_hour

                """
                time Complexity: O(LogN), where N is the number of contracts
                specifically, worse case happens when all contracts have a unique start time

                use binary search to find the index of the earliest start hour after the end hour, in start_hours
                """
                earliest_start_hour_index: int = bisect.bisect_left(
                    start_hours, curr_contract_end_hour
                )

                """
                time Complexity: O(T), where T is the number of unique start times after the current contract end time
                for all start hours that occur after the contract end hour, update their max profits with the new solution
                """
                for start_hour_index in range(
                        earliest_start_hour_index, len(start_hours)
                ):
                    next_start_hour: int = start_hours[start_hour_index]
                    if next_start_hour <= curr_contract_end_hour:
                        continue

                    if (
                            dp.get(start_hours[start_hour_index], Solution.empty()).income
                            < new_solution_at_contract_end_hour.income
                    ):
                        # create a separate new solution
                        # this prevents the bug where dp dictionary at different start hours
                        # to point to the same solution, for different
                        # update the max profit at this start hour
                        new_solution: Solution = (
                            new_solution_at_contract_end_hour.copy()
                        )
                        dp[start_hours[start_hour_index]] = new_solution

        """
        if no contracts are passed back to us (e.g. end_of_duration = 0, and dp doesn't have end_of_duration)
        return an empty solution
        """
        return dp.get(end_of_duration, Solution.empty())
