import sys
import json
import multiprocessing
from concurrent import futures
import grpc
import banks_pb2_grpc
from branch import Branch


# Function to initialize and start the gRPC server for a branch
def branch_serve(branch):
    # Create gRPC stubs for communication between branches
    branch.createStubs()

    # Initialize the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    # Register the branch service with the server
    banks_pb2_grpc.add_BranchServicer_to_server(branch, server)

    # Assign a unique port to the branch based on its ID and start the server
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)  # Bind the server to the specified port
    server.start()  # Start the gRPC server
    server.wait_for_termination()  # Keep the server running to handle requests


# Function to create and start processes for each branch based on input configuration
def createBranchProcesses(processes):
    branches = []  # List to store all branch objects
    branchIds = []  # List to store IDs of all branches

    # Initialize Branch objects based on the input configuration
    for process in processes:
        if process["type"] == "branch":  # Only process entries of type "branch"
            # Create a Branch instance with its ID, initial balance, and list of branch IDs
            branch = Branch(process["id"], process["balance"], branchIds)
            branches.append(branch)
            branchIds.append(branch.id)  # Add branch ID to the list of branch IDs

    # Start a separate process for each branch
    for branch in branches:
        # Create a new process to run the branch's gRPC server
        branch_process = multiprocessing.Process(target=branch_serve, args=(branch,))
        # Record the process ID for the branch (used for tracking/debugging)
        branch.set_branch_pid(branch_process.pid)
        branch_process.start()  # Start the branch process


if __name__ == "__main__":
    # Load the input JSON file provided as a command-line argument
    input_file = sys.argv[1]
    input_json = json.load(open(input_file))

    # Create and start branch processes based on the input configuration
    createBranchProcesses(input_json)

