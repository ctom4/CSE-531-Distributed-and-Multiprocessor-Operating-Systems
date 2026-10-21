import grpc
import banks_pb2
import banks_pb2_grpc


class Branch(banks_pb2_grpc.BranchServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches

        # TODO: students are expected to store the processID of the branches
        self.branch_pid = None

    # store the process id of the branch instance
    def set_branch_pid(self, branch_pid):
        self.branch_pid = branch_pid

    # TODO: students are expected to process requests from both Client and Branch
    # MsgDelivery handles incoming messages from both Client and Branch
    def MsgDelivery(self, request, context):
        return self.ProcessRequest(request, True)

    # MsgPropagation handle incoming messages from Branch message propagation
    def MsgPropagation(self, request, context):
        return self.ProcessRequest(request, False)


    # Create stubs for branch messaging
    def createStubs(self):
        for branchId in self.branches:
            if branchId != self.id:
                port = str(50000 + branchId)
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(banks_pb2_grpc.BranchStub(channel))

    # ProcessMsg received messages and generate response
    def ProcessRequest(self, request, propagate):
        result = "success"

        if request.money < 0:
            result = "fail"

        # Handle deposits and then propagate to other branches if propagate = true
        elif request.interface == "deposit":
            self.balance += request.money
            if propagate == True:
                self.Propagate_Request(request, 'deposit')

        # Handle withdrawals and then propagate to other branches if propagate = true
        # if balance is less than withdraw amount then transaction fails
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.balance -= request.money
                if propagate == True:
                    self.Propagate_Request(request, 'withdraw')
            else:
                result = "fail"

        # Handle balance queries
        elif request.interface == "query":
            result = "success"

        # Message type not supported -- fail status
        else:
            result = "fail"

        # Prepare message response
        msg = {"interface": request.interface, "result": result}

        # Add the balance for query requests
        if request.interface == "query":
            msg["money"] = request.money

        self.recvMsg.append(msg)

        # Return message response
        return banks_pb2.MsgResponse(interface=request.interface, result=result, money=self.balance)

    # Propagate request to other branches action = deposit / withdraw
    def Propagate_Request(self, request, action):
        for stub in self.stubList:
            stub.MsgPropagation(banks_pb2.MsgRequest(id=request.id, interface=action, money=request.money))

