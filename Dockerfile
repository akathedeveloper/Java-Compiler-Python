# Use the Amazon Linux 2 base image for Python 3.8
FROM public.ecr.aws/lambda/python:3.8

# Install Java JDK (Amazon Corretto 11)
RUN yum install -y wget \
    && wget https://corretto.aws/downloads/latest/amazon-corretto-11-x64-linux-jdk.rpm \
    && yum localinstall -y amazon-corretto-11-x64-linux-jdk.rpm \
    && rm amazon-corretto-11-x64-linux-jdk.rpm

# Verify the installation of Java and javac
RUN java -version
RUN javac -version


# Copy the application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the command to execute the Lambda function
CMD ["app.lambda_handler"]
