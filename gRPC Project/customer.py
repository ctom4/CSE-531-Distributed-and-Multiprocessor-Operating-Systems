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
        # pointer for the stub
        self.stub = None

    # TODO: students are expected to create the Customer stub
    # Create stubs for customers to communicate with the branch
    def createStub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = banks_pb2_grpc.BranchStub(channel)

    # TODO: students are expected to send out the events to the Bank
    # Execute the incoming events by communicating with the branch
    def executeEvents(self):
        for event in self.events:
            if event["interface"] == "query":
                # Send the query for balance request to the branch and wait for the response
                response = self.stub.MsgDelivery(
                    banks_pb2.MsgRequest(id=event["id"], interface=event["interface"])
                )
                # setup response message for output file
                msg = {"interface": response.interface}

            else:
                # Send the deposit or withdraw request to the branch and wait for the response
                response = self.stub.MsgDelivery(
                    banks_pb2.MsgRequest(id=event["id"], interface=event["interface"], money=event["money"])
                )
                # setup response message for output file
                msg = {"interface": response.interface, "result": response.result}

            if response.interface == "query":
                msg["balance"] = response.money

            # Append the response to the revMsg list
            self.recvMsg.append(msg)