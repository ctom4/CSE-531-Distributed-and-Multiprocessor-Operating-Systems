import grpc
import banks_pb2
import banks_pb2_grpc


class Customer:
    def __init__(self, id, events):
        # Unique ID of the customer
        self.id = id
        # List of events assigned to the customer (e.g., deposit, withdraw, query)
        self.events = events
        # List to store received responses from the branch
        self.recvMsg = list()
        # Stub for communicating with the branch
        self.stub = None
        # Logical clock for the customer
        self.clock = 1

    # TODO: students are expected to create the Customer stub
    # Create a gRPC stub for the customer to communicate with the branch server
    def createStub(self):
        port = str(50000 + self.id)  # Port number based on customer ID
        channel = grpc.insecure_channel("localhost:" + port)  # Establish a gRPC channel
        self.stub = banks_pb2_grpc.BranchStub(channel)  # Initialize the stub with the channel

    # TODO: students are expected to send out the events to the Bank
    # Execute events assigned to the customer by sending requests to the branch
    def executeEvents(self):
        for event in self.events:
            # Log the current logical clock before sending the request
            event['clock'] = self.clock

            # Handle "query" interface events
            if event["interface"] == "query":
                # Send a query request to the branch and wait for the response
                response = self.stub.MsgDelivery(
                    banks_pb2.MsgRequest(
                        id=event["customer-request-id"],
                        interface=event["interface"],
                        clock=event["clock"],
                        from_customer=self.id
                    )
                )
                # Increment the logical clock after receiving the response
                self.clock += 1

                # Prepare the response message to log for output
                msg = {"interface": response.interface, "clock": self.clock}

            else:
                # Handle "deposit" and "withdraw" interface events
                # Send a deposit/withdraw request to the branch and wait for the response
                response = self.stub.MsgDelivery(
                    banks_pb2.MsgRequest(
                        id=event["customer-request-id"],
                        interface=event["interface"],
                        money=event["money"],
                        clock=event["clock"],
                        from_customer=self.id
                    )
                )
                # Increment the logical clock after receiving the response
                self.clock += 1

                # Prepare the response message to log for output
                msg = {
                    "interface": response.interface,
                    "result": response.result,
                    "clock": self.clock
                }

            # Synchronize the internal logical clock with the branch's clock
            # Update to max of the internal clock and the received clock + 1
            self.clock = max(self.clock, response.clock) + 1
            msg["clock"] = self.clock

            # Include balance information in the response if it was a "query" event
            if response.interface == "query":
                msg["balance"] = response.money

            # Append the processed response message to the received message log
            self.recvMsg.append(msg)