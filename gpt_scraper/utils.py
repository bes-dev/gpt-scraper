"""
Copyright 2024 by Sergei Belousov

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import re
import pydantic
from pydantic import BaseModel
import types
from openai import OpenAI
from typing import Optional, Dict, Any, get_origin, get_args


def parser_from_text(source_code: str) -> types.FunctionType:
    """
    Compile source code into a Python module and extract the 'parse' function.

    Args:
        source_code (str): The source code containing the 'parse' function.

    Returns:
        types.FunctionType: The function object of 'parse'.

    Raises:
        AssertionError: If 'parse' function is not found in the source code.
    """
    module = types.ModuleType("dynamic_module")
    exec(source_code, module.__dict__)
    assert hasattr(module, "parse"), "Model class not found in source code"
    return module.parse


def extract_code_block(text: str, language: str = "python") -> Optional[str]:
    """
    Extracts the first code block of a specified language from the given text.

    Args:
        text (str): The input text containing code blocks.
        language (str, optional): The programming language of the desired code block. Defaults to "python".

    Returns:
        Optional[str]: The extracted code block, or None if not found.
    """
    code_blocks = re.findall(r'```(.*?)```', text, re.DOTALL)
    for block in code_blocks:
        block = block.strip()
        if block.startswith(language):
            code = block[len(language):].strip()
            return code
    return None


def type_to_str(tp):
    """
    Converts a type annotation to a readable string.
    Handles generic types like List[int], Optional[str], etc.
    """
    origin = get_origin(tp)
    args = get_args(tp)

    if origin is None:
        return tp.__name__ if isinstance(tp, type) else str(tp)
    elif origin is list:
        return f"List[{type_to_str(args[0])}]"
    elif origin is dict:
        return f"Dict[{type_to_str(args[0])}, {type_to_str(args[1])}]"
    elif origin is Union:
        # Handle Optional and Union types
        return " | ".join(type_to_str(arg) for arg in args)
    else:
        return str(tp)


def data_structure_to_str(model: BaseModel) -> str:
    """
    Converts a Pydantic model into a string representation of its fields.

    Args:
        model (BaseModel): The Pydantic model to convert.

    Returns:
        str: A JSON-formatted string representing the fields of the model with their types.
    """
    fields_dict = {}
    for field_name, field_info in model.model_fields.items():
        field_type = field_info.annotation
        type_str = type_to_str(field_type)
        fields_dict[field_name] = f"<{type_str}>"
    return json.dumps(fields_dict, indent=4)


class ProviderOpenAI:
    def __init__(self, model_name: str = "gpt-4o"):
        """
        Initializes the ProviderOpenAI class to interact with the OpenAI GPT model.

        Args:
            model_name (str, optional): The name of the model to be used. Defaults to "gpt-4o".
        """
        self.model_name = model_name
        self.client = OpenAI()

    def __call__(self, prompt: str) -> Optional[str]:
        """
        Calls the GPT model with a given prompt and returns the response.

        Args:
            prompt (str): The input prompt to send to the model.

        Returns:
            Optional[str]: The generated text by the model, or None if an error occurs.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
