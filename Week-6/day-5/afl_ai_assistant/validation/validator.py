class Validator:
    @staticmethod
    def validate_response(response: str) -> bool:
        # Simple heuristic to ensure the response isn't empty or totally nonsensical
        if not response or len(response.strip()) < 5:
            return False
        return True

validator = Validator()
