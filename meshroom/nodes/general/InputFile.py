__version__ = "1.0"

import os

from meshroom.core import desc
from meshroom.core.utils import VERBOSE_LEVEL

class InputFile(desc.InputNode, desc.InitNode):
    """
    This node is an input node that receives a File.
    """
    category = "Other"

    inputs = [
        desc.File(
            name="inputFile",
            label="Input File",
            description="A file or folder to use as the input.",
            value="",
        )
    ]

    def initialize(self, node, inputs, recursiveInputs):
        self.resetAttributes(node, ["inputFile"])
        if len(inputs) >= 1 and (os.path.isfile(inputs[0]) or os.path.isdir(inputs[0])):
            self.setAttributes(node, {"inputFile": inputs[0]})
