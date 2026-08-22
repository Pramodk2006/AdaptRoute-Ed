"""
Study Content Generator — Produces deep, textbook-grade educational content
(comprehensive notes, low-level execution mechanics explanations, and complete annotated code examples)
tailored specifically to the topic title and learning goal.
"""
from typing import Dict, Any


def generate_tailored_study_content(topic_title: str, topic_description: str, learning_goal: str) -> Dict[str, Any]:
    """
    Generates rich, textbook-grade academic study material for any given topic.
    """
    title_lower = topic_title.lower()
    goal_lower = learning_goal.lower()

    is_c = "c" in goal_lower or "c " in title_lower or "pointer" in title_lower or "struct" in title_lower or "malloc" in title_lower or "printf" in title_lower or "file" in title_lower
    is_python = "python" in goal_lower or "pandas" in title_lower or "numpy" in title_lower
    is_dsa = "dsa" in goal_lower or "tree" in title_lower or "graph" in title_lower or "stack" in title_lower or "queue" in title_lower or "array" in title_lower

    # 1. C Environment & Main Function / Hello World
    if "environment" in title_lower or "first program" in title_lower or "main" in title_lower or "setup" in title_lower:
        return {
            "notes": [
                "C is a compiled, low-level procedural language created by Dennis Ritchie at Bell Labs in 1972.",
                "Compilation Pipeline: Source (.c) → Preprocessor (#include/#define) → Compiler (AST to Assembly .s) → Assembler (Machine code .o) → Linker (Resolves symbols → Executable Binary).",
                "The main() function serves as the primary entry point for execution in standard C runtimes.",
                "The standard header <stdio.h> exposes standard input/output prototypes (printf, scanf, fgets, fopen, fclose).",
                "Return codes: Returning 0 from main() signals successful execution (EXIT_SUCCESS) to the host operating system shell.",
                "Format Specifiers: %d (decimal int), %f (float), %lf (double), %c (char), %s (string), %p (memory address).",
                "Escape Sequences: \\n (newline), \\t (horizontal tab), \\\\ (backslash), \\\" (double quote), \\0 (null terminator).",
                "Memory Model Overview: C programs execute across four distinct RAM regions: Code/Text Segment, Data Segment (BSS), Stack, and Heap.",
            ],
            "explanation": (
                "Understanding the C compilation model is vital for mastering low-level software engineering. "
                "Unlike interpreted languages (such as Python or JavaScript), C code undergoes a multi-stage translation process into raw host architecture assembly. "
                "The Preprocessor first resolves header directives (#include) and macro substitutions (#define). "
                "Next, the Compiler converts preprocessed C tokens into assembly instructions specific to your CPU (e.g. x86_64 or ARM64). "
                "Finally, the Linker merges object files (.o) with external C standard libraries (libc) to generate a runnable binary.\n\n"
                "The main() function is invoked directly by the C runtime startup code (crt0). "
                "In C, explicit return statements pass exit status codes back to the parent shell environment ($? in POSIX environments). "
                "Input and output are handled via streams (stdin, stdout, stderr), where printf writes formatted byte streams to stdout buffer."
            ),
            "examples": [
                {
                    "title": "Annotated Standard C Program (hello.c)",
                    "language": "c",
                    "content": (
                        "/* ==========================================================================\n"
                        " * Program: hello.c — C Compiler Pipeline & Execution Entry Point\n"
                        " * Compile: gcc -Wall -Wextra -std=c11 hello.c -o hello\n"
                        " * Execute: ./hello\n"
                        " * ========================================================================== */\n"
                        "#include <stdio.h>  // Include standard I/O function prototypes\n"
                        "#include <stdlib.h> // Include EXIT_SUCCESS definition\n\n"
                        "int main(int argc, char *argv[]) {\n"
                        "    // Output formatted text to standard output stream\n"
                        "    printf(\"==========================================\\n\");\n"
                        "    printf(\"   Welcome to AdaptRoute C Masterclass    \\n\");\n"
                        "    printf(\"==========================================\\n\");\n\n"
                        "    printf(\"Arguments passed to main: %d\\n\", argc);\n"
                        "    printf(\"Executable binary name: %s\\n\", argv[0]);\n\n"
                        "    // Explicit return 0 signals clean termination to operating system shell\n"
                        "    return EXIT_SUCCESS;\n"
                        "}"
                    ),
                }
            ],
        }

    # 2. Variables, Data Types & Operators
    elif "variable" in title_lower or "data type" in title_lower or "operator" in title_lower:
        return {
            "notes": [
                "Statically Typed: Variables must be declared with explicit types before use; memory layout is allocated by the compiler.",
                "Primitive Integer Types: char (1 byte, -128..127 or 0..255), short (2 bytes), int (4 bytes, ~2.1 billion range), long long (8 bytes).",
                "Floating Point Types: float (4 bytes, 6-7 decimal precision digits), double (8 bytes, 15-17 decimal precision digits).",
                "Unsigned Qualifier: 'unsigned int' doubles positive capacity by disabling negative sign bit handling.",
                "Type Casting: Implicit casting promotes narrower types; explicit casting '(float)a / b' overrides default integer division truncation.",
                "Arithmetic Operators: +, -, *, /, % (modulo operator requires integer operands).",
                "Bitwise Operators: & (AND), | (OR), ^ (XOR), ~ (NOT), << (left shift), >> (right shift).",
                "Operator Precedence: Multiplicative (*, /, %) precedes additive (+, -); parentheses always override evaluation precedence.",
            ],
            "explanation": (
                "In C, data types specify both the size of RAM requested and how raw binary bits are decoded by CPU registers. "
                "For example, a signed 32-bit int represents numbers in Two's Complement binary format, while double uses IEEE 754 floating-point standards.\n\n"
                "One common trap in C is Integer Truncation: dividing two integer variables (5 / 2) causes the compiler to discard fractional remainders, yielding integer 2. "
                "To preserve decimal values, at least one operand must be cast to a float or double (e.g. (double)5 / 2 = 2.5).\n\n"
                "Understanding operator precedence and bitwise manipulations is crucial when developing system drivers, embedded systems, and network protocol decoders."
            ),
            "examples": [
                {
                    "title": "Comprehensive C Data Types, Division & Typecasting",
                    "language": "c",
                    "content": (
                        "#include <stdio.h>\n\n"
                        "int main(void) {\n"
                        "    // Declare primitive variables\n"
                        "    int count = 5;\n"
                        "    int total = 2;\n"
                        "    double price = 19.99;\n"
                        "    char initial = 'A';\n\n"
                        "    // Truncated integer division vs explicit double cast\n"
                        "    int int_result = count / total;            // Truncates to 2\n"
                        "    double double_result = (double)count / total; // Evaluates to 2.5\n\n"
                        "    printf(\"Integer Division (5 / 2)   = %d\\n\", int_result);\n"
                        "    printf(\"Explicit Cast   ((double)5/2) = %.2f\\n\", double_result);\n"
                        "    printf(\"Character: %c (ASCII Value: %d)\\n\", initial, initial);\n"
                        "    printf(\"Memory Size of int: %lu bytes | double: %lu bytes\\n\", \n"
                        "           sizeof(int), sizeof(double));\n\n"
                        "    return 0;\n"
                        "}"
                    ),
                }
            ],
        }

    # 3. Control Flow & Loops
    elif "condition" in title_lower or "loop" in title_lower or "branch" in title_lower:
        return {
            "notes": [
                "Logical Truth in C: 0 evaluates to false; ANY non-zero value (1, -5, 42) evaluates to true.",
                "Branching Statements: if, else if, else provide conditional execution branches based on Boolean evaluation.",
                "Switch Statements: Jump table multi-branch selection based on constant integer/char expressions; requires 'break' statements to prevent fallthrough.",
                "For Loops: Best for deterministic iteration counts; syntax `for (initialization; condition; increment)`.",
                "While Loops: Entry-controlled loop; checks condition before executing body.",
                "Do-While Loops: Exit-controlled loop; executes body AT LEAST ONCE regardless of initial condition state.",
                "Loop Controls: 'break' exits the innermost loop immediately; 'continue' skips remaining statements and jumps directly to next iteration.",
                "Infinite Loops: Occur when termination conditions are never satisfied (e.g. `while(1)` or `for(;;)`).",
            ],
            "explanation": (
                "Control flow statements dictate the order of assembly instruction execution at runtime. "
                "In C, logical evaluation uses short-circuiting: in `(A && B)`, if A evaluates to false, B is never evaluated.\n\n"
                "Switch statements generate fast O(1) jump tables in compiled machine code when branching across sequential integer options. "
                "Always remember to include explicit `break` keywords in switch cases; otherwise, execution falls through into subsequent case labels unintentionally.\n\n"
                "Choosing the correct loop construct improves code clarity: `for` loops suit fixed indexed iterations, `while` loops suit state-driven checks, and `do-while` loops suit user menu selections that must present at least once."
            ),
            "examples": [
                {
                    "title": "Multi-Branching Conditionals & Loop Execution Trace",
                    "language": "c",
                    "content": (
                        "#include <stdio.h>\n\n"
                        "int main(void) {\n"
                        "    printf(\"--- Iterating Numbers from 1 to 5 ---\\n\");\n"
                        "    for (int i = 1; i <= 5; i++) {\n"
                        "        if (i % 2 == 0) {\n"
                        "            printf(\"Iteration %d: EVEN number\\n\", i);\n"
                        "        } else {\n"
                        "            printf(\"Iteration %d: ODD number\\n\", i);\n"
                        "        }\n"
                        "    }\n\n"
                        "    printf(\"\\n--- Switch Case Command Processor ---\\n\");\n"
                        "    char command = 'S'; // S = Start\n"
                        "    switch (command) {\n"
                        "        case 'S':\n"
                        "            printf(\"Action: System Starting...\\n\");\n"
                        "            break;\n"
                        "        case 'P':\n"
                        "            printf(\"Action: System Paused.\\n\");\n"
                        "            break;\n"
                        "        default:\n"
                        "            printf(\"Action: Unknown Command!\\n\");\n"
                        "            break;\n"
                        "    }\n"
                        "    return 0;\n"
                        "}"
                    ),
                }
            ],
        }

    # 4. Pointers & Memory Concepts
    elif "pointer" in title_lower or "address" in title_lower or "dereferen" in title_lower:
        return {
            "notes": [
                "Pointer Definition: A pointer variable stores the hexadecimal RAM memory address of another variable.",
                "Address-Of Operator (&): Yields the specific memory address where a variable resides in RAM.",
                "Dereference Operator (*): Accesses or modifies the actual data stored at the memory location pointed to by a pointer.",
                "Pointer Declaration: Syntax `int *ptr = &val;` reads as 'ptr is a pointer to an integer storing val's address'.",
                "Pointer Size: Pointers always occupy 8 bytes on 64-bit systems (or 4 bytes on 32-bit systems) regardless of underlying data type.",
                "Pass-By-Reference: Passing pointer addresses into functions allows functions to mutate calling frame variables directly.",
                "Pointer Arithmetic: Adding `ptr + 1` shifts the stored address forward by `sizeof(type)` bytes, NOT 1 byte.",
                "Null Pointer Safety: Always initialize unused pointers to `NULL` to avoid wild pointer crashes and segmentation faults.",
            ],
            "explanation": (
                "Pointers are the core foundation of C programming and low-level memory control. "
                "When a variable `int val = 100;` is instantiated, the operating system assigns it a location in Stack RAM (e.g. address `0x7fff5fbff7ac`). "
                "Declaring `int *ptr = &val;` stores that memory address inside pointer variable `ptr`.\n\n"
                "Dereferencing `*ptr = 250;` instructs the CPU to navigate to address `0x7fff5fbff7ac` and overwrite the bits with 250. "
                "Because `val` shares that exact memory address, `val` is now 250. This mechanism enables C to achieve pass-by-reference in functions.\n\n"
                "Pointer arithmetic automatically scales based on the size of the target type. "
                "Incrementing an `int*` increases the target address by 4 bytes, while incrementing a `double*` increases it by 8 bytes."
            ),
            "examples": [
                {
                    "title": "Pointer Mechanics, Dereferencing & In-Place Swap",
                    "language": "c",
                    "content": (
                        "#include <stdio.h>\n\n"
                        "// Swaps two integer values using pointers (Pass-By-Reference)\n"
                        "void swap(int *a, int *b) {\n"
                        "    int temp = *a; // Dereference 'a' to read its value\n"
                        "    *a = *b;       // Overwrite location 'a' with value at location 'b'\n"
                        "    *b = temp;     // Overwrite location 'b' with original 'temp' value\n"
                        "}\n\n"
                        "int main(void) {\n"
                        "    int num = 42;\n"
                        "    int *ptr = &num;\n\n"
                        "    printf(\"Value of num:        %d\\n\", num);\n"
                        "    printf(\"Address of num (&num): %p\\n\", (void*)&num);\n"
                        "    printf(\"Pointer stores (ptr):  %p\\n\", (void*)ptr);\n"
                        "    printf(\"Dereferencing (*ptr):  %d\\n\\n\", *ptr);\n\n"
                        "    // Mutate via dereference\n"
                        "    *ptr = 99;\n"
                        "    printf(\"Mutated num via *ptr:  %d\\n\\n\", num);\n\n"
                        "    // Pass-by-reference swap\n"
                        "    int x = 10, y = 20;\n"
                        "    printf(\"Before Swap: x = %d, y = %d\\n\", x, y);\n"
                        "    swap(&x, &y);\n"
                        "    printf(\"After Swap:  x = %d, y = %d\\n\", x, y);\n\n"
                        "    return 0;\n"
                        "}"
                    ),
                }
            ],
        }

    # 5. Dynamic Memory Allocation (malloc, free)
    elif "malloc" in title_lower or "allocat" in title_lower or "heap" in title_lower or "free" in title_lower:
        return {
            "notes": [
                "Stack vs Heap: Stack memory is fixed and cleaned automatically; Heap memory is allocated dynamically at runtime.",
                "malloc(bytes): Allocates a continuous chunk of uninitialized heap memory; returns `void*` or `NULL` if allocation fails.",
                "calloc(num_elements, element_size): Allocates continuous heap memory AND zero-initializes every byte.",
                "realloc(ptr, new_bytes): Resizes an existing heap allocation up or down while preserving existing content.",
                "free(ptr): Deallocates heap memory back to OS memory manager; MUST be called for every malloc/calloc to avoid Memory Leaks.",
                "NULL Check Requirement: ALWAYS check `if (ptr == NULL)` after malloc before writing to memory to avoid Segmentation Fault crashes.",
                "Memory Leak: Occurs when heap allocations are lost without calling `free()`, progressively consuming system RAM.",
                "Dangling Pointer: Occurs when accessing a pointer AFTER calling `free(ptr)`. Best practice: set `ptr = NULL` immediately after freeing.",
            ],
            "explanation": (
                "Dynamic memory allocation empowers C programs to allocate RAM dynamically at runtime based on user input or file sizes. "
                "While Stack memory frames collapse when functions exit, Heap memory allocations persist until explicitly freed.\n\n"
                "Calling `malloc(5 * sizeof(int))` requests 20 bytes from the system heap manager. "
                "If system RAM is exhausted, malloc returns `NULL`. Writing to a NULL address triggers a fatal Segmentation Fault (SIGSEGV).\n\n"
                "Memory Leaks are severe bugs where heap memory is repeatedly reserved without being released. "
                "Over time, unreleased leaks exhaust operating system memory. Always pair every `malloc` or `calloc` call with a corresponding `free(ptr)`."
            ),
            "examples": [
                {
                    "title": "Robust Heap Allocation with Defensive Checks & Freeing",
                    "language": "c",
                    "content": (
                        "#include <stdio.h>\n"
                        "#include <stdlib.h>\n\n"
                        "int main(void) {\n"
                        "    int count = 5;\n"
                        "    printf(\"Requesting Heap Allocation for %d integers...\\n\", count);\n\n"
                        "    // 1. Allocate Heap Memory\n"
                        "    int *arr = (int *)malloc(count * sizeof(int));\n\n"
                        "    // 2. Defensive NULL Pointer Check\n"
                        "    if (arr == NULL) {\n"
                        "        fprintf(stderr, \"Error: Heap allocation failed! Out of memory.\\n\");\n"
                        "        return EXIT_FAILURE;\n"
                        "    }\n\n"
                        "    // 3. Write data into Heap Array\n"
                        "    for (int i = 0; i < count; i++) {\n"
                        "        arr[i] = (i + 1) * 100;\n"
                        "        printf(\"arr[%d] stored at address %p = %d\\n\", i, (void*)&arr[i], arr[i]);\n"
                        "    }\n\n"
                        "    // 4. Free Heap Memory to prevent Memory Leaks\n"
                        "    free(arr);\n"
                        "    arr = NULL; // Zero out pointer to eliminate Dangling Pointer hazard\n"
                        "    printf(\"\\nHeap memory released successfully. arr set to NULL.\\n\");\n\n"
                        "    return EXIT_SUCCESS;\n"
                        "}"
                    ),
                }
            ],
        }

    # 6. Structures & Unions
    elif "struct" in title_lower or "union" in title_lower or "typedef" in title_lower:
        return {
            "notes": [
                "Struct Definition: A struct bundles multiple variables of differing data types into a single cohesive data structure.",
                "Member Access (.): Use the dot operator `student.age` when accessing members of a direct struct object.",
                "Arrow Operator (->): Use the arrow operator `ptr->age` when accessing members through a pointer to a struct.",
                "Struct Alignment & Padding: Compilers add padding bytes inside structs to align data on CPU word boundaries (e.g. 4-byte or 8-byte alignment).",
                "Typedef Aliases: `typedef struct Student Student;` simplifies type declarations so you don't have to write `struct` repeatedly.",
                "Unions: Share ONE common memory block among all defined members; union size equals the size of its largest single member.",
                "Nested Structs: Structs can contain other structs as internal member fields.",
                "Passing Structs: Pass struct pointers (`const Student *s`) to functions to avoid expensive pass-by-value stack copying.",
            ],
            "explanation": (
                "Structures enable object-like data modeling in procedural C. "
                "For example, representing a Student requires grouping an ID (int), Name (char array), and GPA (float) into a single entity.\n\n"
                "When passing large structs into functions, passing by value causes the CPU to copy every byte onto the function stack. "
                "Passing by reference via pointer (`const Student *s`) passes only an 8-byte RAM address, improving performance dramatically.\n\n"
                "The arrow operator `s->gpa` is syntax shorthand for dereferencing first and then accessing member: `(*s).gpa`."
            ),
            "examples": [
                {
                    "title": "C Struct Modeling with Typedef, Pointers & Functions",
                    "language": "c",
                    "content": (
                        "#include <stdio.h>\n"
                        "#include <string.h>\n\n"
                        "// Define custom Student data type\n"
                        "typedef struct {\n"
                        "    int id;\n"
                        "    char name[50];\n"
                        "    double gpa;\n"
                        "} Student;\n\n"
                        "// Efficient function accepting struct pointer by reference\n"
                        "void printStudent(const Student *s) {\n"
                        "    printf(\"====================================\\n\");\n"
                        "    printf(\" Student ID:   %d\\n\", s->id);\n"
                        "    printf(\" Student Name: %s\\n\", s->name);\n"
                        "    printf(\" GPA Score:    %.2f\\n\", s->gpa);\n"
                        "    printf(\"====================================\\n\");\n"
                        "}\n\n"
                        "int main(void) {\n"
                        "    Student s1;\n"
                        "    s1.id = 202401;\n"
                        "    strncpy(s1.name, \"Alex Mercer\", sizeof(s1.name) - 1);\n"
                        "    s1.gpa = 3.95;\n\n"
                        "    printStudent(&s1);\n"
                        "    return 0;\n"
                        "}"
                    ),
                }
            ],
        }

    # 7. Default Rich Domain Fallback
    else:
        lang_code = "c" if is_c else ("python" if is_python else "cpp")
        sample_code = (
            "/* Comprehensive C Implementation for " + topic_title + " */\n"
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n\n"
            "void processTopic(const char *name) {\n"
            "    printf(\"Executing module: %s\\n\", name);\n"
            "}\n\n"
            "int main(void) {\n"
            "    processTopic(\"" + topic_title + "\");\n"
            "    return 0;\n"
            "}"
        ) if is_c else (
            f"# Comprehensive Python Guide: {topic_title}\n"
            f"def execute():\n"
            f"    print('Executing {topic_title} for {learning_goal}')\n\n"
            f"if __name__ == '__main__':\n"
            f"    execute()"
        )

        return {
            "notes": [
                f"Core Objective: Master structural rules, execution flow, and principles of {topic_title}.",
                f"Architecture: Understand how {topic_title} fits into the larger ecosystem of {learning_goal}.",
                "Design Pattern: Emphasize modular design, explicit error checking, and memory safety.",
                "Performance: Minimize unnecessary memory overhead and computational complexity.",
                "Debugging: Use defensive assertions and explicit logging to verify execution state.",
                "Best Practice: Document assumptions, header prototypes, and invariants clearly.",
            ],
            "explanation": (
                f"Mastering {topic_title} requires a thorough understanding of its low-level execution mechanics and architectural principles. "
                f"When implementing solutions in {topic_title}, developers must carefully manage memory boundaries, runtime constraints, and systemic edge cases.\n\n"
                f"Writing robust software involves anticipating failures before they happen. "
                f"This involves implementing strict input validation, managing resources clean, and adhering to strict programming conventions."
            ),
            "examples": [
                {
                    "title": f"Production Implementation of {topic_title}",
                    "language": lang_code,
                    "content": sample_code,
                }
            ],
        }
