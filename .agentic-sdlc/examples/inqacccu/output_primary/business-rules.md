# Business Rules

## Rule ID: BR-001
**Rule Statement:** The system must retrieve account records associated with a given customer number.  
**Trigger Conditions:** When a valid customer number is provided.  
**Inputs:** Customer number (10 characters).  
**Outputs:** List of associated account records.  
**Error Conditions:** If the customer number is invalid or not found, return an error response indicating "Customer not found".

## Rule ID: BR-002
**Rule Statement:** The system must return a success flag indicating whether the customer was found.  
**Trigger Conditions:** After attempting to retrieve account records based on the customer number.  
**Inputs:** Customer number (10 characters).  
**Outputs:** Success flag (Y/N), number of accounts found.  
**Error Conditions:** If the retrieval process fails, set the success flag to 'N' and return an appropriate error code.

## Rule ID: BR-003
**Rule Statement:** The system must validate the format of the customer number before processing.  
**Trigger Conditions:** When a customer number is inputted.  
**Inputs:** Customer number (10 characters).  
**Outputs:** Validation result (valid/invalid).  
**Error Conditions:** If the customer number does not conform to the expected format, return an error indicating "Invalid customer number format".

## Rule ID: BR-004
**Rule Statement:** The system must ensure that the account details retrieved include all relevant fields as defined in the ACCOUNT structure.  
**Trigger Conditions:** When account records are successfully retrieved.  
**Inputs:** Customer number (10 characters).  
**Outputs:** Account details including account number, type, balance, etc.  
**Error Conditions:** If any required field is missing in the retrieved account records, log an error and return an incomplete data error response.

## Rule ID: BR-005
**Rule Statement:** The system must log all inquiries made for auditing and monitoring purposes.  
**Trigger Conditions:** Each time an inquiry is processed.  
**Inputs:** Customer number, timestamp, success flag.  
**Outputs:** Log entry created in structured JSON format.  
**Error Conditions:** If logging fails, ensure that the system continues to operate without crashing, but log the failure to the error monitoring system.

## Rule ID: BR-006
**Rule Statement:** The system must handle and respond to unauthorized access attempts appropriately.  
**Trigger Conditions:** When an unauthorized user attempts to access account information.  
**Inputs:** User credentials.  
**Outputs:** Error response indicating "Unauthorized access".  
**Error Conditions:** If access is denied, log the attempt and return a 403 Forbidden status.

## Rule ID: BR-007
**Rule Statement:** The system must ensure that all data returned to the client is sanitized to prevent injection attacks.  
**Trigger Conditions:** When preparing account data for response.  
**Inputs:** Account details.  
**Outputs:** Sanitized account data.  
**Error Conditions:** If sanitization fails, log the error and return a generic error message to the client.