# CCl_project

This project is focused on deploying an application successfully on the cloud environment by utilizing different cloud services. We have deployed an NLP application on AWS Cloud that summarizes text given as input in the text or file format. The following instructions can help you to deploy and access an application deployed on cloud.
Services used are:
•	IAM (Identity & Access Management)
•	EC2 (Elastic Cloud Compute)
•	DynamoDB

To access any of the cloud services, simply select the name from the Services menu in the AWS Management Console. Make sure to select services available only in Free Tier.

1]	**Create a New User via IAM service on the AWS Console.** 

    a.	Choose to create Access key - Programmatic access and give the name for user.
    
    b.	To Set Permissions select: AdministratorAccess and AmazonDynamoDBFullAccess. 
    
    c.	Add tags if you wish to and create the user.
    
    d.	Download CSV File of the credentials of Access Key when prompted as it is essential for future steps. Incase you forget to save the Secret Access Key then once user is created, select the User and in Security Credentials tab, generate new Access Key and save it.
    
(Creating an IAM User can help you or maybe your team to access the project on the console without having to share the Root User credentials as every user created, gets a separate set of credentials assigned.)

2]	**Create an EC2 Instance next. Make the following changes while creating an Instance.**

    a.	Choose AMI: Microsoft Windows Server 2022 Base (in Free Tier)
    b.	Instance Type: t2.micro
    c.	No change in Instance Details.
    d.	No change is Storage. Assigned storage is sufficient.
    e.	Add a tag: Key: Name
                       Value: instance_1 (name of instance you want)
    f.	Security Group Configuration: Add Rules: Custom TCP protocol and set port number to 8080. Add HTTP and HTTPS rules as well.    
    g.	When asked for Key Pair, select **Create a new Key Pair**. Name the Key Pair and create. A .pem file will be downloaded. Know the location of this file for further use. 
    h.	 Launch the instance
    i.	Go to EC2>>Instances and wait for the Instance State to display Running and Status Check to display 2/2 checks passed before proceeding.
    
3]	Create RDP Connect.

    a.	Select the instance you created and click on Connect in top panel.
    
    b.	Navigate to RDP Client section.
    
    c.	Click on Download remote desktop file, and a .rdp file will be downloaded.
    
    d.	In password section, click on Get Password.
    
    e.	Here, Browse and select the Key Pair file we downloaded in the preious step in .pem format. Click on Decrypt Password. You will redirected to the previous page and will see the password.
    
    f.	Open the .rdp file now. Click on Connect in the pop-up. You will be asked to enter password for Administrator user. Copy the Decrypted password from the console and past in the dialogue box and connect to the RDP client. Click on Yes if another pop-up appears.
    
    g.	As we have chosen Windows AMI, a VM will open up with Windows OS. Wait till you see the instance details on the Desktop of this VM before moving further. Select Refresh by right clicking in the VM if you don’t see the details on top right corner.
    
    h.	RDP Connection is now established.
    
    i.	To run this project, install Python in the instance and/or Xampp if you wish to check the SQL connectivity. You open Apache and MySQL connection on Xampp, create a database by the name of text_summarizer in phpMyAdmin and import the .sql file.
    
4]	Connecting to DynamoDB. (This step can be performed independently, before creating EC2 instance.)

    a.	Install AWS CLI on your system. To check its installation, open command prompt and type aws. If you get a message abut aws help and its usage then CLI is installed correctly.
    
    b.	Run the command: aws configure
    
    c.	Now for AWS Access Key ID, enter the Access Key ID mentioned in the .csv file we downloaded while creating a user in IAM. Also enter the Secret Access Key next and enter the region in which you have created your instance, example: us-west-1 OR us-east-1, etc.
    
    d.	Click enter key when asked for Default output format or you can type json.
    
    e.	Now you have configured the AWS connection required to connect to DynamoDB.
    
    f.	Run the command: aws sts get-session-token
    
    g.	This will give the Access Key ID and Secret Access Key for the session created along with the Session Token and Expiration time.
    
    h.	You need to copy Access Key ID, Secret Access Key and Session Token values and paste them in the key_config.py file and save it.
    
    i.	Now run the dynamodb_createTable.py file. This establishes a connection with DynamoDB using the Access Key we generated and creates the required tables. You can check the creation of the tables in the Console by navigating to DynamoDB>>Tables.
    
    j.	Click on Explore Items to check the data stored in the table.
    
    k.	**Make sure to change all the values in key_config.py file once the session token expires**.
    
5]	Launching the project in the instance.

    a.	Download the zip file of the project and copy it on the Desktop in the VM Instance. Extract the file in any location.
    
    b.	To run the application, open command prompt and navigate to the directory of the project folder.
    
    c.	Enter the command: venv\Scripts\activate
    
    d.	Once virtual environment is activated, install packages by running the command: pip install -r requirements.txt
    
    e.	Run the command: python app.py
        This will run the application. You will receive an URL on the command prompt. Copy that link and open in the browser to test the application.
        
    f.	You can create a profile and use the Summarizer tool to generate summary and check your profile to view the summaries generated. These entries will be reflected in the tables created in DynamoDB.

By following the above steps, you can deploy any project of your choice on the cloud environment. As we have used Free Tier services, make sure to **STOP the instance** on the console by selecting the instance and choosing Stop Instance in Instance State dropdown menu. AWS allows users to use EC2 instance for free for 750 hours per month only so if your instance is running but not in use then also the limit is applicable and if it exceeds 750 hours then you will be billed for the service in use.
