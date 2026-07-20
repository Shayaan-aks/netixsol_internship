"""
tools.py — Tool definitions for the Week 5 Day 1 raw-Python agent.

Each tool has:
  • A JSON schema  (name, description, input_schema)  used by the Anthropic API
  • A Python implementation  run(input_dict) -> str  called when the model invokes it

Why tool descriptions matter
─────────────────────────────
Claude decides WHICH tool to call entirely from the name + description fields.
Vague descriptions ("does stuff") cause wrong tool selection. Precise descriptions
that state inputs, outputs, units, and edge-cases lead to reliable calling.
"""

import math
import json
import datetime
import os

# ─────────────────────────────────────────────────────────────────────────────
# 1. CALCULATOR TOOL
# ─────────────────────────────────────────────────────────────────────────────
CALCULATOR_SCHEMA = {
    "name": "calculator",
    "description": (
        "Evaluates a mathematical expression and returns the numeric result as a string. "
        "Supports standard arithmetic (+, -, *, /), exponentiation (**), parentheses, "
        "and math functions such as sqrt(), abs(), round(), floor(), ceil(), log(), "
        "sin(), cos(), tan(), pi, and e. "
        "Use this tool whenever a calculation is needed — do NOT compute in your head."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": (
                    "The mathematical expression to evaluate. "
                    "Examples: '2 + 2', 'sqrt(144)', '(3.14 * 5**2)', 'log(100, 10)'"
                )
            }
        },
        "required": ["expression"]
    }
}


def run_calculator(inputs: dict) -> str:
    """Execute a math expression safely and return the result."""
    expression = inputs.get("expression", "").strip()
    if not expression:
        return "ERROR: empty expression provided."

    # Allowlist of safe names for eval
    safe_globals = {
        "__builtins__": {},
        "abs": abs, "round": round,
        "floor": math.floor, "ceil": math.ceil,
        "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
        "pow": pow,
    }

    try:
        result = eval(expression, safe_globals)  # noqa: S307
        return f"{result}"
    except ZeroDivisionError:
        return "ERROR: division by zero."
    except Exception as exc:
        return f"ERROR: could not evaluate '{expression}': {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. WEATHER STUB TOOL
# ─────────────────────────────────────────────────────────────────────────────
WEATHER_SCHEMA = {
    "name": "get_weather",
    "description": (
        "Returns the current temperature and weather conditions for a given city. "
        "Temperature is in Celsius. Use this tool to answer any question about "
        "current weather, temperature comparisons, or whether to bring an umbrella. "
        "This is a STUB: it returns simulated data so no real API key is needed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The name of the city, e.g. 'Karachi', 'London', 'Tokyo'."
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit. Default is 'celsius'."
            }
        },
        "required": ["city"]
    }
}

# Simulated weather database
_WEATHER_DB = {
    "karachi":    {"temp_c": 34, "condition": "Hot and sunny",  "humidity": 65},
    "lahore":     {"temp_c": 38, "condition": "Very hot, hazy", "humidity": 45},
    "islamabad":  {"temp_c": 28, "condition": "Partly cloudy",  "humidity": 55},
    "london":     {"temp_c": 17, "condition": "Overcast",       "humidity": 78},
    "new york":   {"temp_c": 24, "condition": "Sunny",          "humidity": 60},
    "tokyo":      {"temp_c": 29, "condition": "Warm and humid", "humidity": 80},
    "dubai":      {"temp_c": 41, "condition": "Extremely hot",  "humidity": 50},
    "paris":      {"temp_c": 20, "condition": "Mild and cloudy","humidity": 70},
    "sydney":     {"temp_c": 15, "condition": "Cool and breezy","humidity": 62},
    "toronto":    {"temp_c": 22, "condition": "Sunny",          "humidity": 58},
    "cairo":      {"temp_c": 36, "condition": "Hot and sunny",  "humidity": 30},
    "moscow":     {"temp_c":  8, "condition": "Cold and cloudy","humidity": 72},
}


def run_get_weather(inputs: dict) -> str:
    """Return simulated weather for a city."""
    city = inputs.get("city", "").strip().lower()
    unit = inputs.get("unit", "celsius").lower()

    if not city:
        return "ERROR: no city provided."

    # Try exact match, then partial match
    data = _WEATHER_DB.get(city)
    if data is None:
        for key in _WEATHER_DB:
            if key in city or city in key:
                data = _WEATHER_DB[key]
                city = key
                break

    if data is None:
        return (
            f"ERROR: No weather data for '{city}'. "
            f"Available cities: {', '.join(c.title() for c in _WEATHER_DB)}."
        )

    temp_c = data["temp_c"]
    if unit == "fahrenheit":
        temp = round(temp_c * 9 / 5 + 32, 1)
        unit_sym = "°F"
    else:
        temp = temp_c
        unit_sym = "°C"

    return (
        f"Weather in {city.title()}: {temp}{unit_sym}, "
        f"{data['condition']}, humidity {data['humidity']}%."
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. TEXT FILE READER TOOL
# ─────────────────────────────────────────────────────────────────────────────
FILE_READER_SCHEMA = {
    "name": "read_text_file",
    "description": (
        "Reads a local plain-text file and returns its contents as a string. "
        "Only works with .txt, .md, .csv, .json, .py, .sql, and .log files. "
        "Use this tool when the user asks you to read, summarise, or analyse a file. "
        "If the file does not exist or is not a text file, an error is returned."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Absolute or relative path to the file to read."
            },
            "max_chars": {
                "type": "integer",
                "description": (
                    "Maximum number of characters to return (default 3000). "
                    "Set lower for large files."
                )
            }
        },
        "required": ["filepath"]
    }
}

ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".py", ".sql", ".log"}


def run_read_text_file(inputs: dict) -> str:
    """Read a text file and return its contents."""
    filepath = inputs.get("filepath", "").strip()
    max_chars = int(inputs.get("max_chars", 3000))

    if not filepath:
        return "ERROR: no filepath provided."

    _, ext = os.path.splitext(filepath)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return (
            f"ERROR: extension '{ext}' not allowed. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if not os.path.isfile(filepath):
        return f"ERROR: file not found: '{filepath}'"

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
        truncated = "(... truncated)" if os.path.getsize(filepath) > max_chars else ""
        return f"--- {filepath} ---\n{content}\n{truncated}".strip()
    except Exception as exc:
        return f"ERROR reading '{filepath}': {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. UNIT CONVERTER TOOL
# ─────────────────────────────────────────────────────────────────────────────
UNIT_CONVERTER_SCHEMA = {
    "name": "convert_units",
    "description": (
        "Converts a numeric value from one unit to another. "
        "Supported categories: temperature (celsius, fahrenheit, kelvin), "
        "length (meters, feet, inches, km, miles), "
        "weight (kg, lbs, grams, ounces). "
        "Use this tool for any unit conversion question."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "value": {
                "type": "number",
                "description": "The numeric value to convert."
            },
            "from_unit": {
                "type": "string",
                "description": "Source unit (e.g. 'celsius', 'meters', 'kg')."
            },
            "to_unit": {
                "type": "string",
                "description": "Target unit (e.g. 'fahrenheit', 'feet', 'lbs')."
            }
        },
        "required": ["value", "from_unit", "to_unit"]
    }
}

_CONVERSIONS = {
    # Temperature handled specially
    # Length — base: meters
    "meters": 1.0, "meter": 1.0, "m": 1.0,
    "km": 1000.0, "kilometers": 1000.0, "kilometre": 1000.0,
    "feet": 0.3048, "foot": 0.3048, "ft": 0.3048,
    "inches": 0.0254, "inch": 0.0254, "in": 0.0254,
    "miles": 1609.344, "mile": 1609.344, "mi": 1609.344,
    # Weight — base: kg
    "kg": 1.0, "kilograms": 1.0, "kilogram": 1.0,
    "grams": 0.001, "gram": 0.001, "g": 0.001,
    "lbs": 0.453592, "pounds": 0.453592, "pound": 0.453592, "lb": 0.453592,
    "ounces": 0.0283495, "ounce": 0.0283495, "oz": 0.0283495,
}


def _temp_convert(value, from_unit, to_unit):
    """Handle temperature conversions via Celsius as base."""
    f, t = from_unit.lower(), to_unit.lower()
    # to Celsius
    if f in ("celsius", "c"):
        c = value
    elif f in ("fahrenheit", "f"):
        c = (value - 32) * 5 / 9
    elif f in ("kelvin", "k"):
        c = value - 273.15
    else:
        return None
    # from Celsius
    if t in ("celsius", "c"):
        return c
    elif t in ("fahrenheit", "f"):
        return c * 9 / 5 + 32
    elif t in ("kelvin", "k"):
        return c + 273.15
    return None


def run_convert_units(inputs: dict) -> str:
    """Convert between units."""
    try:
        value = float(inputs["value"])
        from_u = inputs["from_unit"].strip().lower()
        to_u   = inputs["to_unit"].strip().lower()
    except (KeyError, ValueError) as exc:
        return f"ERROR: invalid inputs: {exc}"

    # Temperature
    temp_units = {"celsius", "c", "fahrenheit", "f", "kelvin", "k"}
    if from_u in temp_units or to_u in temp_units:
        result = _temp_convert(value, from_u, to_u)
        if result is None:
            return f"ERROR: cannot convert temperature '{from_u}' -> '{to_u}'"
        return f"{value} {from_u} = {round(result, 4)} {to_u}"

    # Length / Weight via base unit
    f_factor = _CONVERSIONS.get(from_u)
    t_factor = _CONVERSIONS.get(to_u)
    if f_factor is None:
        return f"ERROR: unknown unit '{from_u}'"
    if t_factor is None:
        return f"ERROR: unknown unit '{to_u}'"

    result = value * f_factor / t_factor
    return f"{value} {from_u} = {round(result, 6)} {to_u}"


# ─────────────────────────────────────────────────────────────────────────────
# Tool registry — single source of truth consumed by Agent
# ─────────────────────────────────────────────────────────────────────────────
TOOL_SCHEMAS = [
    CALCULATOR_SCHEMA,
    WEATHER_SCHEMA,
    FILE_READER_SCHEMA,
    UNIT_CONVERTER_SCHEMA,
]

TOOL_RUNNERS = {
    "calculator":      run_calculator,
    "get_weather":     run_get_weather,
    "read_text_file":  run_read_text_file,
    "convert_units":   run_convert_units,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Dispatch a tool call by name and return the result string."""
    runner = TOOL_RUNNERS.get(tool_name)
    if runner is None:
        return (
            f"ERROR: tool '{tool_name}' is not defined. "
            f"Available tools: {', '.join(TOOL_RUNNERS.keys())}"
        )
    return runner(tool_input)


# ─────────────────────────────────────────────────────────────────────────────
# Quick self-test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Tools self-test ===\n")

    tests = [
        ("calculator",    {"expression": "sqrt(144) + 3**2"}),
        ("calculator",    {"expression": "1 / 0"}),
        ("get_weather",   {"city": "Karachi"}),
        ("get_weather",   {"city": "London", "unit": "fahrenheit"}),
        ("get_weather",   {"city": "Atlantis"}),
        ("convert_units", {"value": 100, "from_unit": "celsius", "to_unit": "fahrenheit"}),
        ("convert_units", {"value": 5,   "from_unit": "km",      "to_unit": "miles"}),
        ("read_text_file",{"filepath": "nonexistent.txt"}),
    ]

    for tool, inp in tests:
        result = execute_tool(tool, inp)
        print(f"[{tool}] {inp}")
        print(f"  -> {result}\n")
