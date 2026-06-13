from enum import Enum

# This file defines the JobStatus enum, which represents the possible states of a job in the system.
# No need to write status hardcoded in the codebase, we can just use this enum to check the status of a job and update it accordingly.
class JobStatus(str, Enum):
    QUEUED = "queued"

    PROCESSING = "processing"

    COMPLETED = "completed"

    FAILED = "failed"