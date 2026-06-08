
## What is tsconfig.json?

- It’s a JSON file placed at the root of a TypeScript project.
- It defines how TypeScript files (.ts, .tsx) are compiled to JavaScript.
- It controls which files are included, how strict type checking is, output directory, module system, and more.

---

## Why is tsconfig.json Important?

- **Centralizes configuration:** All TypeScript settings are in one place.
- **Enables project-wide type checking:** tsc uses it to know which files to check and how.
- **Supports tooling:** Editors like VS Code use it for intellisense, error checking, and refactoring.

---

## Key Sections in tsconfig.json

1. **compilerOptions**  
   - Controls how code is compiled.
   - Examples:
     - `"target"`: Output JS version (e.g., ES6, ES2017)
     - `"module"`: Module system (e.g., commonjs, esnext)
     - `"outDir"`: Where to put compiled JS files
     - `"strict"`: Enables all strict type-checking options
     - `"esModuleInterop"`: Allows default imports from CommonJS modules

2. **include**  
   - Array of file globs to include in the project (e.g., ["src/**/*"]).

3. **exclude**  
   - Array of file globs to exclude (e.g., ["node_modules", "dist"]).

4. **files**  
   - Explicit list of files to include (rarely used; include is preferred).

---

## Example tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES6",
    "module": "esnext",
    "outDir": "dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## How tsconfig.json Works

- When you run `tsc`, it looks for tsconfig.json in the current directory.
- It compiles all files matched by include (or 