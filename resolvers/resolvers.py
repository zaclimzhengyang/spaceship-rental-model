from models.contract import Contract
from models.slim_solution import SlimSolution
from services.definite_solutions.definite_contract_selector_service import DefiniteContractSelectorService

DEFINITE_CONTRACT_SELECTOR_SERVICE: DefiniteContractSelectorService = DefiniteContractSelectorService()


def resolve_optimize_contracts(contracts: list[Contract]) -> SlimSolution:
    """
    given a list of contracts, return the optimal contracts
    """
    return DEFINITE_CONTRACT_SELECTOR_SERVICE.select_contracts(contracts).to_slim()