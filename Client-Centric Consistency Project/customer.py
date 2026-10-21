import grpc
import banks_pb2
import banks_pb2_grpc

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # dictionary to hold the stubs for the branches
        self.stubs = {}

    # TODO: students are expected to create the Customer stub
    # Get or create stubs for customers to communicate branches
    def get_stub(self, branch):

        #if the stub for the branch is not created, create it return the stub
        if branch not in self.stubs:
            port = str(50000 + branch)
            channel = grpc.insecure_channel("localhost:" + port)
            self.stubs[branch] = banks_pb2_grpc.BranchStub(channel)

        return self.stubs[branch]


    # TODO: students are expected to send out the events to the Bank
    # Execute the incoming events by communicating with the branch
    def executeEvents(self):
        for event in self.events:
            branch = event["branch"]
            #get the stub for the requested branch
            branch_stub = self.get_stub(branch)

            if event["interface"] == "query":
                # Send the query for balance request to the branch and wait for the response
                response = branch_stub.MsgDelivery(
                    banks_pb2.MsgRequest(id=event["id"], interface=event["interface"])
                )
                # setup response message for output file
                msg = {"interface": response.interface}

            else:
                # Send the deposit or withdraw request to the branch and wait for the response
                response = branch_stub.MsgDelivery(
                    banks_pb2.MsgRequest(id=event["id"], interface=event["interface"], money=event["money"])
                )
                # setup response message for output file
                msg = {"interface": response.interface, "result": response.result}

            if response.interface == "query":
                msg["balance"] = response.money

            # Add the branch id the logged message
            msg["branch"] = response.branch

            # Append the response to the revMsg list
            self.recvMsg.append(msg)