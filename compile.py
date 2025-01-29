import os
import subprocess
import argparse
import re

def run_llava(input_image):
    try:
        command = ["ollama","run","llava","This image represents ideas for a computer program: " + input_image + ". Give a description of the computer program that could be used by another generative AI tool to write the program.  Be as specific as possible about specific functions that will need to be written as computer code and number each function in a list."]
        process = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running ollama: {e.stderr}")
        return None

def run_codellama(language, task):
    try:
        command = ["ollama","run","codellama","Write code in " + language + " to accomplish the following task. " + task]
        # Run the ollama command with the input data
        process = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=True
        )
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running ollama: {e.stderr}")
        return None
    

def analyze_images(image_dir, output_dir, language):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    analysis_results = []
    
    # Process each image file
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)
        
        # Skip non-image files
        if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
            continue

        print(f"Analyzing image: {image_file}")

        # Call ollama for image analysis
        analysis_result = run_llava(image_path)
        if analysis_result is None:
            print(f"Skipping {image_file} due to analysis error.")
            continue

        print(f"Analysis Result for {image_file}: {analysis_result}")

        analysis_results.append(analysis_result)

    functions_to_gen = []
    
    for analysis_result in analysis_results:
        # Regular expression to match the pattern
        pattern = r"^\d+\.\s*(.*)$"

        # Extracting the text after the number for each line
        lines = analysis_result.split("\n")
        extracted_texts = [re.search(pattern, line).group(1) for line in lines if re.search(pattern, line)]
        functions_to_gen.append(extracted_texts)

    print(functions_to_gen)
        
    for analysis_result in analysis_results:
        # Call ollama to generate code
        print(f"Generating code for {analysis_result}...")
        code_result = run_codellama(language, analysis_result)
        if code_result is None:
            print(f"Skipping {image_file} due to code generation error.")
            continue

        # Save the generated code
        output_file = os.path.join(output_dir, f"{os.path.splitext(image_file)[0]}_code.py")
        with open(output_file, 'w') as f:
            f.write(code_result)
            print(f"Code saved to {output_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Analyze images and generate code using ollama.")
    parser.add_argument("image_directory", type=str, help="Directory containing image files to analyze.")
    parser.add_argument("output_directory", type=str, help="Directory to save generated code files.")
    parser.add_argument("language", type=str, help="Programming language for code generation (e.g., python, javascript).")
    args = parser.parse_args()

    # Run the analysis and code generation
    analyze_images(args.image_directory, args.output_directory, args.language)
