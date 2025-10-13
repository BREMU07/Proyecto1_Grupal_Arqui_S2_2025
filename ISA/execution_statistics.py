class ExecutionStatistics:
    def __init__(self):
        self.history = []

    def add_execution(self, num_cycles, num_instructions, cycle_time_ns, stage):
        cpi = num_cycles / num_instructions
        execution_time_ns = num_cycles * cycle_time_ns
        stats = {
            "num_cycles": num_cycles,
            "num_instructions": num_instructions,
            "cpi": cpi,
            "execution_time_ns": execution_time_ns,
            "stage": stage
        }
        self.history.append(stats)
        if len(self.history) > 5:
            self.history.pop(0)

    def get_statistics(self):
        return self.history
