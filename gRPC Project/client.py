import json
import sys
from customer import Customer


# Function to service customers by creating a stub and executing the events
def serveCustomer(customer):
    customer.createStub()
    customer.executeEvents()

    return {"id": customer.id, "recv": customer.recvMsg}

# Function to create customer process and its associated requests
def createCustomerProcesses(input):

    outputs = []
    for request in input:
        if request["type"] == "customer":
            customer = Customer(request["id"], request["events"])
            output = serveCustomer(customer)
            outputs.append(output)

    # Write the responses to a json file
    with open("output.json", "w") as json_file:
        json.dump(outputs, json_file, indent=4)


if __name__ == "__main__":

    # Load input json file
    input_file = sys.argv[1]
    input_jason = json.load(open(input_file))

    #Create customer processes
    createCustomerProcesses(input_jason)



