* number of initial records must be divisble by the total number of clients.
Otherwise, some record may be missing and Fabric will report an error if the queried record is not found. 
2. During later transaction, inserted keys are ordered only within a single process, but not globally ordered.