import yaml

from config import EXERCISES_CONFIG_PATH


class WorkoutManager:
    
    def __init__(self) -> None:
        self.exercises = self._load_exercises(EXERCISES_CONFIG_PATH)

    def get_all_exercises(self) -> list[str]:
        return list(self.exercises.keys())
    
    def get_burned_calories(
        self,
        exercise_name: str,
        duration_minutes: float
    ) -> float:
        calories_per_minute = self.exercises.get(exercise_name)
        if not calories_per_minute:
            return 0.0
        return calories_per_minute * duration_minutes

    def _load_exercises(self, config_path: str) -> dict:
        try:
            with open(config_path, 'r') as file:
                exercises = yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading exercises configuration: {e}")
            exercises = {}
        return exercises
