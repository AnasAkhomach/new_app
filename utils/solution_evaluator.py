from equipment_utilization_calculator import EquipmentUtilizationCalculator
from equipment_utilization_efficiency_calculator import EquipmentUtilizationEfficiencyCalculator
from resource_utilization_efficiency_calculator import ResourceUtilizationEfficiencyCalculator
from room_utilization_calculator import RoomUtilizationCalculator
from workload_balance_calculator import WorkloadBalanceCalculator

class SolutionEvaluator:
    def __init__(self, db):
        self.db = db
        self.equipment_utilization_calculator = EquipmentUtilizationCalculator(db)
        self.equipment_utilization_efficiency_calculator = EquipmentUtilizationEfficiencyCalculator(db)
        self.resource_utilization_efficiency_calculator = ResourceUtilizationEfficiencyCalculator(db)
        self.room_utilization_calculator = RoomUtilizationCalculator(db)
        self.workload_balance_calculator = WorkloadBalanceCalculator(db)

    def evaluate_solution(self, solution):
        equipment_utilization_score = self.equipment_utilization_calculator.calculate(solution)
        equipment_efficiency_score = self.equipment_utilization_efficiency_calculator.calculate(solution)
        resource_efficiency_score = self.resource_utilization_efficiency_calculator.calculate(solution)
        room_utilization_score = self.room_utilization_calculator.calculate(solution)
        workload_balance_score = self.workload_balance_calculator.calculate(solution)

        # Combine scores into a comprehensive evaluation, potentially weighted
        overall_score = (equipment_utilization_score + equipment_efficiency_score + 
                         resource_efficiency_score + room_utilization_score + 
                         workload_balance_score) / 5  # Example averaging method

        return overall_score
