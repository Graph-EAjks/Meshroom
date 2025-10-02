#!/usr/bin/env python

from meshroom.common import BaseObject, Property


class BaseSubmitter(BaseObject):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self._name = name

    def createJob(self, nodes, edges, filepath, submitLabel="{projectName}"):
        """ Create and submits the job
         Returns:
             bool: whether the submission succeeded
        """
        raise NotImplementedError("'createJob' method must be implemented in subclasses")
    
    def submit(self, nodes, edges, filepath, submitLabel="{projectName}"):
        """ Submit the given graph
         Returns:
             bool: whether the submission succeeded
        """
        return self.createJob(nodes, edges, filepath, submitLabel)

    name = Property(str, lambda self: self._name, constant=True)
