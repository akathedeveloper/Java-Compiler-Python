import os
import base64
import subprocess
import json
import tempfile

def lambda_handler(event, context):
    try:
        # Ensure the PATH environment variable includes the directory for javac
        os.environ['PATH'] += ':/usr/bin'  # Update with the correct path if necessary

        # Create a temporary directory for storing the Java file
        with tempfile.TemporaryDirectory() as temp_dir:
            code = base64.b64decode(event['body']['code']).decode('utf-8')
            filename = event['body']['filename'] + '.java'
            file_path = os.path.join(temp_dir, filename)
            
            # Write the Java code to a file
            with open(file_path, 'w') as java_file:
                java_file.write(code)
            
            # Compile the Java code
            compile_process = subprocess.run(
                ['javac', file_path], capture_output=True, text=True
            )
            
            if compile_process.returncode != 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'status-code': 400,
                        'message': 'Compilation failed',
                        'output': base64.b64encode(compile_process.stderr.encode('utf-8')).decode('utf-8'),
                        'code': event['body']['code'],
                        'filename': event['body']['filename']
                    })
                }
            
            # Prepare the input for the Java program
            concatenated_inputs = '\n'.join(
                [base64.b64decode(input_value).decode('utf-8') for input_value in event['body'].get('input', [])]
            )
            
            class_filename = filename.replace('.java', '')
            run_process = subprocess.Popen(
                ['java', '-cp', temp_dir, class_filename],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            run_stdout, run_stderr = run_process.communicate(input=concatenated_inputs)
            
            if run_process.returncode != 0:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'status-code': 400,
                        'message': 'Execution failed',
                        'output': base64.b64encode(run_stderr.encode('utf-8')).decode('utf-8'),
                        'code': event['body']['code'],
                        'filename': event['body']['filename'],
                        'input': base64.b64encode(concatenated_inputs.encode('utf-8')).decode('utf-8')
                    })
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status-code': 200,
                    'message': 'success',
                    'output': base64.b64encode(run_stdout.encode('utf-8')).decode('utf-8'),
                    'code': event['body']['code'],
                    'filename': event['body']['filename'],
                    'input': base64.b64encode(concatenated_inputs.encode('utf-8')).decode('utf-8')
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status-code': 500,
                'message': 'Internal server error',
                'output': base64.b64encode(str(e).encode('utf-8')).decode('utf-8'),
                'code': event['body']['code'],
                'filename': event['body']['filename']
            })
        }

# Test the function locally
if __name__ == "__main__":
    test_event = {
        "body": {
            "code": base64.b64encode("public class HelloWorld { public static void main(String[] args) { System.out.println(\"Hello, World!\"); } }".encode('utf-8')).decode('utf-8'),
            "filename": "HelloWorld",
            "input": []
        }
    }
    print(lambda_handler(test_event, None))
