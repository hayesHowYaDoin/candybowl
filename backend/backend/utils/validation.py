from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError
from typing import TypeVar, Callable, Any

T = TypeVar("T", bound=BaseModel)


def validate_json(model: type[T]) -> Callable:
    """
    Decorator to validate JSON request body using Pydantic models.

    Args:
        model: Pydantic model class to validate against

    Returns:
        Decorated function that validates request JSON
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                if request.json is None:
                    return jsonify({"error": "Invalid request format"}), 400

                # Validate and parse the request data
                validated_data = model.model_validate(request.json)

                # Add validated data to request context
                setattr(request, "validated_data", validated_data)

                return f(*args, **kwargs)

            except ValidationError as e:
                errors = []
                for error in e.errors():
                    field = ".".join(str(x) for x in error["loc"])
                    errors.append(f"{field}: {error['msg']}")

                return jsonify(
                    {"error": "Validation failed", "details": errors}
                ), 400

        return wrapper

    return decorator
