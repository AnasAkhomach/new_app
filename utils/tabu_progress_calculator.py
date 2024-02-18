class ProgressCalculator:
    def __init__(self, initial_score, improvement_threshold):
        self.initial_score = initial_score
        self.improvement_threshold = improvement_threshold
        self.best_score = initial_score
        self.iterations_since_last_improvement = 0

    def update_progress(self, current_score):
        if current_score < self.best_score - self.improvement_threshold:  # Assuming lower scores are better
            self.best_score = current_score
            self.iterations_since_last_improvement = 0
        else:
            self.iterations_since_last_improvement += 1

    def calculate_progress(self):
        # Calculate progress as a function of iterations without improvement
        progress = min(1.0, self.iterations_since_last_improvement / 100.0)
        # Incorporate improvement rate; adjust formula as needed for your context
        improvement_rate = (self.initial_score - self.best_score) / self.initial_score
        # Combine metrics for a comprehensive progress measure
        combined_progress = (progress + improvement_rate) / 2
        return combined_progress

# Example usage
# Initialize with the initial solution score and a threshold for what you consider an improvement
progress_calculator = ProgressCalculator(initial_score=1000, improvement_threshold=10)
# Update progress with new scores obtained after each optimization iteration
progress_calculator.update_progress(current_score=995)  # Example score after an iteration
# Calculate current progress
progress = progress_calculator.calculate_progress()
