# circular-servers
An experimental server cluster implementation, in which each server has an instance of state machine and able to receive and process requests from outer sources (let's say clients). If a server fails, it redirects the request to its neighbor.
