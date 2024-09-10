import os

def create_directory_map(start_path):
    map_lines = []

    def add_to_map(path, depth):
        for item in sorted(os.listdir(path)):
            if item.startswith('.') or item == 'node_modules':
                continue
            item_path = os.path.join(path, item)
            map_lines.append("  " * depth + "├─ " + item)
            if os.path.isdir(item_path):
                add_to_map(item_path, depth + 1)

    map_lines.append(os.path.basename(os.path.abspath(start_path)))
    add_to_map(start_path, 1)
    return "\n".join(map_lines)

def compile_files(start_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Create and write the directory map
        outfile.write("Directory Structure:\n\n")
        outfile.write(create_directory_map(os.getcwd()))
        outfile.write("\n\n" + "="*50 + "\n\n")

        # Process files in the current directory
        for item in os.listdir('.'):
            if os.path.isfile(item) and item != 'compiled.txt' and not item.startswith('.'):
                outfile.write(f"\n\n--- File: {item} ---\n\n")
                try:
                    with open(item, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {str(e)}")

        # Process files in the 'src' directory and its subdirectories
        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, start=os.getcwd())
                outfile.write(f"\n\n--- File: {relative_path} ---\n\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {str(e)}")

if __name__ == "__main__":
    src_directory = "src"
    output_file = "compiled.txt"

    if not os.path.exists(src_directory):
        print(f"Error: '{src_directory}' directory not found.")
    else:
        compile_files(src_directory, output_file)
        print(f"Compilation complete. Check '{output_file}' for the results.")
