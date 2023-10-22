from flask import Flask, render_template, request
import pandas as pd
import time
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, BlobServiceClient
from urllib.parse import quote

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Generate time
        timestamp = str(int(time.time()))  # Use current timestamp

        # Retrieve the input values from the form
        input_value1 = request.form['input1']
        input_value2 = request.form['input2']

        # Create an input file with the input values
        input_file_content = f'Input 1: {input_value1}\nInput 2: {input_value2}'

        # Perform data processing based on the input values
        sum_value = int(input_value1) + int(input_value2)

        # Create a pandas DataFrame with the processed data
        data = {'Input1': [input_value1], 'Input2': [input_value2], 'Sum': [sum_value]}
        df = pd.DataFrame(data)

        # Convert the DataFrame to Excel format
        output_file_content = df.to_csv(index=False)

        # Save the input file to Azure Blob Storage
        #input_blob_name = 'input_values.txt'
        input_blob_name = f'input_values_{timestamp}.txt'
        save_blob_to_storage(input_file_content, input_blob_name)

        # Save the output file to Azure Blob Storage
        # Generate a unique blob name
        timestamp = str(int(time.time()))  # Use current timestamp
        output_blob_name = f'output_{timestamp}.csv'
        #output_blob_name = 'output.csv'
        save_blob_to_storage(output_file_content, output_blob_name)

        # Render the template with the download links for the input and output files
        input_file_url = get_blob_sas_url(input_blob_name)
        output_file_url = get_blob_sas_url(output_blob_name)
        return render_template('index.html', input_file=input_file_url, output_file=output_file_url)

    # Render the initial page with an empty form
    return render_template('index.html')

def save_blob_to_storage(content, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=adfblobstorageaccount1;AccountKey=oy1iAwR7r8ocxzi/xsdPnLe0VEmlitNsJVMy0A1oqzDiUN0W8gHRNnQCRKEoKCho7IHcssIYrGTx+ASt5hPJbQ==;BlobEndpoint=https://adfblobstorageaccount1.blob.core.windows.net/;FileEndpoint=https://adfblobstorageaccount1.file.core.windows.net/;QueueEndpoint=https://adfblobstorageaccount1.queue.core.windows.net/;TableEndpoint=https://adfblobstorageaccount1.table.core.windows.net/")
    container_name = "inputfolder"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(content)

def get_blob_sas_url(blob_name):
    blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=adfblobstorageaccount1;AccountKey=oy1iAwR7r8ocxzi/xsdPnLe0VEmlitNsJVMy0A1oqzDiUN0W8gHRNnQCRKEoKCho7IHcssIYrGTx+ASt5hPJbQ==;BlobEndpoint=https://adfblobstorageaccount1.blob.core.windows.net/;FileEndpoint=https://adfblobstorageaccount1.file.core.windows.net/;QueueEndpoint=https://adfblobstorageaccount1.queue.core.windows.net/;TableEndpoint=https://adfblobstorageaccount1.table.core.windows.net/")
    container_name = "inputfolder"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
     # Generate the SAS token with read permission and an expiry time of 1 hour
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time
    )

    # Encode the blob name for URL
    encoded_blob_name = quote(blob_name)
    blob_url = blob_client.url + "?" + sas_token
    #blob_url = blob_client.url + "/" + encoded_blob_name + "?" + sas_token
    return blob_url
#    sas_token = blob_client.generate_blob_sas(permission="r", expiry=datetime.utcnow() + timedelta(hours=1))
#    blob_url = blob_client.url + "?" + sas_token
#    return blob_url

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug=True)
