import json
import sys
import glob
from customer import Customer


# Function to service a customer by creating a stub and executing events
def serveCustomer(customer):
    # Initialize communication with the branch by creating a gRPC stub
    customer.createStub()
    # Execute all events (e.g., deposits, withdrawals, and queries) for the customer
    customer.executeEvents()

    # Prepare data for logging customer requests and logical clocks
    msg = []
    for ev in customer.events:
        ev_msg = {
            "customer-request-id": ev["customer-request-id"],  # ID of the customer request
            "logical_clock": ev["clock"],  # Logical clock value when the request is sent
            "interface": ev["interface"],  # Type of the request (e.g., deposit, withdraw, query)
            "comment": f"event_sent from customer {customer.id}"  # Log comment for tracking
        }
        msg.append(ev_msg)

    # Return structured data for the customer's processed events
    return {"id": customer.id, "type": "customer", "events": msg}


# Function to create customer processes and execute their requests
def createCustomerProcesses(input_data):
    outputs = []  # List to store results for all customers

    # Process each entry in the input JSON
    for request in input_data:
        if request["type"] == "customer":  # Only process customer requests
            # Initialize a Customer instance with its ID and event list
            customer = Customer(request["id"], request["customer-requests"])
            # Process the customer and log the results
            output = serveCustomer(customer)
            outputs.append(output)

    # Write the customer request results to a JSON file (part1.json)
    with open("part1.json", "w") as json_file:
        json.dump(outputs, json_file, indent=4)


# Helper function to format and create records for part 3 of the output JSON
def create_part3_record(partx_list, part3_list):
    for data in partx_list:
        rec_id = data['id']  # ID of the customer or branch
        rec_type = data['type']  # Type (customer or branch)
        for event in data['events']:
            ev = {
                'id': rec_id,  # ID of the entity (customer or branch)
                'customer-request-id': event['customer-request-id'],  # Associated request ID
                'type': rec_type,  # Type of entity (customer or branch)
                "logical_clock": event['logical_clock'],  # Logical clock value
                'interface': event['interface'],  # Type of event
                'comment': event['comment']  # Descriptive comment for the event
            }
            # Append a tuple containing the request ID, clock value, and event details
            rec_tuple = (ev['customer-request-id'], ev['logical_clock'], ev)
            part3_list.append(rec_tuple)


# Function to create the final output JSON file
def create_final_json():
    part3_all = []  # Stores all events (customers and branches) for part 3

    # Load customer events data from part1.json
    file_part1 = "./part1.json"
    with open(file_part1, 'r') as f:
        data = json.load(f)
        # Format and store part 1 data into the part3 list
        create_part3_record(data, part3_all)

    # Initialize the output list with customer events
    outputlist = data

    # Load branch event data from all part2_*.json files
    files2 = "./part2_*.json"
    part2_all = []
    for file in glob.glob(files2):  # Dynamically locate all matching files
        with open(file, 'r') as f:
            data = json.load(f)
            part2_all.append(data)
            # Format and store branch data into the part3 list
            create_part3_record([data], part3_all)
            # Append branch events to the output list
            outputlist.append(data)

    # Write all branch events to part2.json
    with open("part2.json", "w") as json_file:
        json.dump(part2_all, json_file, indent=4, separators=(',', ': '))

    # Sort part3_all by customer request ID and logical clock for proper ordering
    part3_all.sort(key=lambda x: (x[0], x[1]))

    # Format sorted part3 data for final output
    part3_all2 = []
    for row in part3_all:
        part3_all2.append(row[2])  # Extract the event details
        outputlist.append(row[2])  # Append to the final output list

    # Write part3 data to part3.json
    with open("part3.json", "w") as json_file:
        json.dump(part3_all2, json_file, indent=4, separators=(',', ': '))

    # Write the final output.json with data from part1, part2, and part3
    with open("output.json", "w") as json_file:
        json.dump(outputlist, json_file, indent=4, separators=(',', ': '))


if __name__ == "__main__":
    # Load the input JSON file containing customer and branch configurations
    input_file = sys.argv[1]
    input_json = json.load(open(input_file))

    # Create customer processes and execute their requests
    createCustomerProcesses(input_json)

    # Generate the final output JSON containing events from customers and branches
    create_final_json()

