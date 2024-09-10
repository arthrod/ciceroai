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

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def create_context_file():
    with open('context2.txt', 'w', encoding='utf-8') as context_file:
        context_file.write("Directory Structure:\n\n")
        context_file.write(create_directory_map(os.getcwd()))
        context_file.write("\n\n" + "="*50 + "\n\n")

        files_to_read = [
            "package.json",
            "tsconfig.json",
            "next.config.mjs",
            ".eslintrc.js",
            "src/locales/en.json",
            "src/locales/pt.json",
            "src/utils/translations.ts",
            "src/styles/globals.css",
            "src/app/page.tsx",
            "src/app/layout.tsx",
            "src/app/chat/page.tsx",
            "src/app/chat/actions.ts",
            "vercel.json",
            "README.md",
            "tailwind.config.ts",
            "postcss.config.js",
            ".env.local",  # If it exists
            "src/app/globals.css",  # If it exists
            "src/components/ChatInterface.tsx",  # If it exists
            "src/components/WelcomeScreen.tsx",  # If it exists
            "src/pages/_app.tsx",  # If it exists
            "src/pages/index.tsx",  # If it exists
            "src/pages/chat.tsx",  # If it exists
        ]

        for file_path in files_to_read:
            if os.path.exists(file_path):
                context_file.write(f"\n--- File: {file_path} ---\n\n")
                context_file.write(read_file_content(file_path))
                context_file.write("\n")
            else:
                context_file.write(f"\n--- File: {file_path} ---\n\n")
                context_file.write(f"File not found: {file_path}\n")

if __name__ == "__main__":
    create_context_file()
    print("context2.txt has been created with the project structure and file contents.")
