import sys
import json
import multiprocessing
from concurrent import futures
import grpc
import banks_pb2_grpc
from branch import Branch


# Function to service a branch by creating stubs and starting the gRPC server
def branch_serve(branch):

    branch.createStubs()

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    banks_pb2_grpc.add_BranchServicer_to_server(branch, server)

    # Set up the port based on branch id and start the service
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()

# Function to create and start process for branches based on input
def createBranchProcesses(processes):
    # List of Branch objects
    branches = []
    # List of Branch IDs
    branchIds = []


    for process in processes:
        if process["type"] == "branch":
            # Create a Branch instance
            branch = Branch(process["id"], process["balance"], branchIds)
            branches.append(branch)
            branchIds.append(branch.id)


    for branch in branches:
        # Start branch_serv process
        branch_process = multiprocessing.Process(target=branch_serve, args=(branch,))
        branch.set_branch_pid(branch_process.pid)
        branch_process.start()


if __name__ == "__main__":

    #Load input jason file
    input_file = sys.argv[1]
    input_jason = json.load(open(input_file))

    #Crete processes based on input file
    createBranchProcesses(input_jason)

