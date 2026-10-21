import grpc
import banks_pb2
import banks_pb2_grpc
import json

class Branch(banks_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        # Unique ID of the branch
        self.id = id
        # Branch's replica of the account balance
        self.balance = balance
        # List of IDs of all branches in the system
        self.branches = branches
        # List of gRPC stubs for communicating with other branches
        self.stubList = list()
        self.stubList_branch_id = list()
        # List of received messages for debugging and validation
        self.recMsg = list()
        # Log of events/messages for this branch
        self.msgs = list()
        # Logical clock for the branch
        self.clock = 1
        # TODO: students are expected to store the processID of the branches
        # Process ID of the branch (to be set later)
        self.branch_pid = None

    # Set the process ID for the branch instance
    def set_branch_pid(self, branch_pid):
        self.branch_pid = branch_pid

    # Write branch events to a JSON file
    def write_json(self):
        # Prepare output structure for the branch's logged events
        out_msg = {"id": self.id, "type": "branch", "events": self.msgs}
        json_file = f"part2_{self.id}.json"
        # Write the events to a JSON file for analysis
        with open(json_file, "w") as json_file:
            json.dump(out_msg, json_file, indent=4)

    # Handle incoming messages from clients (customers)
    def MsgDelivery(self, request, context):
        # Update the branch's logical clock based on the request clock
        self.clock = max(self.clock, request.clock) + 1

        # Log the incoming message
        msg = {
            "customer-request-id": request.id,
            "logical_clock": self.clock,
            "interface": request.interface,
            "comment": f"event_recv from customer {request.from_customer}"
        }
        self.msgs.append(msg)
        self.write_json()

        # Process the request and return a response
        return self.ProcessRequest(request, propagate=True)

    # Handle incoming propagation messages from other branches
    def MsgPropagation(self, request, context):
        # Update the branch's logical clock based on the propagation message clock
        self.clock = max(self.clock, request.clock) + 1

        # Log the incoming propagation message
        msg = {
            "customer-request-id": request.id,
            "logical_clock": self.clock,
            "interface": f"propogate_{request.interface}",
            "comment": f"event_recv from branch {request.from_branch}"
        }
        self.msgs.append(msg)
        self.write_json()

        # Process the request without further propagation
        return self.ProcessRequest(request, propagate=False)

    # Create gRPC stubs for communication with other branches
    def createStubs(self):
        for branchId in self.branches:
            if branchId != self.id:  # Skip creating a stub for itself
                port = str(50000 + branchId)  # Calculate the port number for the branch
                channel = grpc.insecure_channel(f"localhost:{port}")  # Create a gRPC channel
                self.stubList.append(banks_pb2_grpc.BranchStub(channel))  # Add the stub for the branch
                self.stubList_branch_id.append(branchId)  # Track the corresponding branch ID

    # Process requests received by the branch (from clients or other branches)
    def ProcessRequest(self, request, propagate):
        result = "success"

        # Reject invalid requests with negative amounts
        if request.money < 0:
            result = "fail"

        # Handle deposit requests
        elif request.interface == "deposit":
            self.balance += request.money  # Update the branch's balance
            if propagate:  # Propagate the deposit to other branches
                self.Propagate_Request(request, action='deposit')

        # Handle withdrawal requests
        elif request.interface == "withdraw":
            if self.balance >= request.money:  # Check if sufficient balance exists
                self.balance -= request.money  # Update the branch's balance
                if propagate:  # Propagate the withdrawal to other branches
                    self.Propagate_Request(request, action='withdraw')
            else:
                result = "fail"  # Fail if insufficient balance

        # Handle balance query requests
        elif request.interface == "query":
            result = "success"

        # Mark unsupported operations as failed
        else:
            result = "fail"

        # Log the processed message
        msg = {"interface": request.interface, "result": result}
        if request.interface == "query":  # Include balance information for queries
            msg["money"] = self.balance
        self.recMsg.append(msg)

        # Return the response message
        return banks_pb2.MsgResponse(
            interface=request.interface,
            result=result,
            money=self.balance,
            clock=self.clock,
            from_customer=request.from_customer,
            from_branch=self.id
        )

    # Propagate requests (deposit/withdraw) to other branches
    def Propagate_Request(self, request, action):
        for i in range(len(self.stubList)):
            stub = self.stubList[i]
            branch_id = self.stubList_branch_id[i]

            # Increment the logical clock before sending the propagation message
            self.clock += 1
            stub.MsgPropagation(
                banks_pb2.MsgRequest(
                    id=request.id,
                    interface=action,
                    money=request.money,
                    clock=self.clock,
                    from_customer=request.from_customer,
                    from_branch=self.id
                )
            )

            # Log the outgoing propagation message
            msg = {
                "customer-request-id": request.id,
                "logical_clock": self.clock,
                "interface": f"propogate_{request.interface}",
                "comment": f"event_sent to branch {branch_id}"
            }
            self.msgs.append(msg)
            self.write_json()

