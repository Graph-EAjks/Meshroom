#!/usr/bin/env python

from meshroom.common import BaseObject, Property
from enum import IntFlag, auto
from typing import Optional


class SubmitterOptionsEnum(IntFlag):
    RETRIEVE = auto()       # Can retrieve job (read job tasks, ...)
    INTERRUPT_JOB = auto()  # Can interrupt
    RESUME_JOB = auto()     # Can resume after interruption
    EDIT_TASKS = auto()     # Can edit tasks
    
    @classmethod
    def get(cls, option):
        if isinstance(option, str):
            # Try to cast to SubmitterOptionsEnum
            option = getattr(cls, option.upper(), None)
        elif isinstance(option, int):
            option = cls(option)
        if isinstance(option, cls):
            return option
        return 0

SubmitterOptionsEnum.ALL = SubmitterOptionsEnum._all_bits_


class SubmitterOptions:
    def __init__(self, *args):
        self._options = 0
        for option in args:
            self.addOption(option)
    
    def addOption(self, option):
        option = SubmitterOptionsEnum.get(option)
        self._options |= option
    
    def hasOption(self, option):
        option = SubmitterOptionsEnum.get(option)
        return self._options & option > 0
    
    def __iter__(self):
        for o in SubmitterOptionsEnum:
            if self.hasOption(o):
                yield(o)


class BaseSubmittedJob:
    """
    Interface to manipulate the job via Meshroom
    """
    
    def __init__(self, jobId, submitter):
        self.jobId = jobId
        self.submitterOptions = submitter._options
    
    def interrupt(self):
        raise NotImplementedError("'interrupt' method must be implemented in subclasses")
    
    def resume(self):
        raise NotImplementedError("'resume' method must be implemented in subclasses")


class JobManager(BaseObject):
    """ Central manager for all jobs """
    
    def __init__(self):
        super().__init__()
        self._jobs = {}  # jobId -> BaseSubmittedJob
        self._nodeToJob = {}  # node uid -> Job
    
    def addJob(self, job: BaseSubmittedJob):
        if job.id not in self._jobs:
            self._jobs[job.id] = job
    
    def getJob(self, jobId: str) -> Optional[BaseSubmittedJob]:
        return self._jobs.get(jobId)
    
    def removeJob(self, jobId: str):
        with self._lock:
            if jobId in self._jobs:
                del self._jobs[jobId]

    def addNodes(self, jobId, nodes):
        for node in nodes:
            nodeUid = node._uid
            self._nodeToJob[nodeUid] = jobId
    
    def getNodeJob(self, node):
        nodeUid = node._uid
        jobId = self._nodeToJob.get(nodeUid)
        if jobId:
            return self.getJob(jobId)
        return None
    
    # TODO
    # All the methods necessary to 
    # - interrupt/resume job specific to a node/chunk
    # - spool tasks, edit job
    # - ...


# Global instance that manages submitted jobs
jobManager = JobManager()


class BaseSubmitter(BaseObject):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self._name = name
        self._options: SubmitterOptions = SubmitterOptions()

    def addOptions(self, options):
        if not isinstance(options, list):
            options = [options]
        for option in options:
            self._options.addOption(option)

    def createJob(self, nodes, edges, filepath, submitLabel="{projectName}"):
        """ Submit the given graph
         Returns:
             bool: whether the submission succeeded
        """
        raise NotImplementedError("'createJob' method must be implemented in subclasses")
    
    def retrieveJob(self, jobId) -> BaseSubmittedJob:
        raise NotImplementedError("'retrieveJob' method must be implemented in subclasses")

    def submit(self, nodes, edges, filepath, submitLabel="{projectName}"):
        """ Submit the given graph
         Returns:
             bool: whether the submission succeeded
        """
        job = self.createJob(nodes, edges, filepath, submitLabel)
        if not job:
            # Failed to create the job
            return False
        if self._options.hasOption(SubmitterOptions.RETRIEVE):
            jobManager.addJob(job)
            jobManager.addNodes(job, nodes)
        return True

    name = Property(str, lambda self: self._name, constant=True)
