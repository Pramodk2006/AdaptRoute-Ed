"""
Domain-Tailored Quiz Generator — produces diagnostic multiple-choice questions with answer keys and explanations.
"""
from typing import Dict, List, Any


def generate_tailored_quiz(topic_title: str, skill_level: str = "beginner") -> Dict[str, Any]:
    title_lower = topic_title.lower()

    if "python" in title_lower or "object" in title_lower or "class" in title_lower:
        questions = [
            {
                "question_text": f"In Python OOP ({topic_title}), what is the primary purpose of the '__init__' method?",
                "options": [
                    {"label": "A", "text": "To initialize the object attributes when an instance is created"},
                    {"label": "B", "text": "To destroy the object and release VRAM/RAM memory"},
                    {"label": "C", "text": "To convert the object into a JSON string format"},
                    {"label": "D", "text": "To inherit private methods from child classes"}
                ],
                "correct_answer": "A",
                "explanation": "The '__init__' method acts as the constructor in Python, executing automatically when a new instance of a class is created to set initial attributes."
            },
            {
                "question_text": "What keyword is used in Python to define a class that inherits from a parent class 'BaseModel'?",
                "options": [
                    {"label": "A", "text": "class ChildModel extends BaseModel:"},
                    {"label": "B", "text": "class ChildModel(BaseModel):"},
                    {"label": "C", "text": "class ChildModel implements BaseModel:"},
                    {"label": "D", "text": "class ChildModel inherit BaseModel:"}
                ],
                "correct_answer": "B",
                "explanation": "Python specifies inheritance by passing the parent class name inside parentheses after the child class name."
            },
            {
                "question_text": "How do you access the parent class's implementation of a method in Python?",
                "options": [
                    {"label": "A", "text": "super().method_name()"},
                    {"label": "B", "text": "parent.method_name()"},
                    {"label": "C", "text": "this.super.method_name()"},
                    {"label": "D", "text": "base().method_name()"}
                ],
                "correct_answer": "A",
                "explanation": "The built-in 'super()' function returns a proxy object that delegates method calls to a parent or sibling class."
            },
            {
                "question_text": "What is encapsulation in Object-Oriented Python?",
                "options": [
                    {"label": "A", "text": "Bundling data and methods that operate on that data within a class while restricting direct access"},
                    {"label": "B", "text": "Compiling Python source code into binary machine code executable"},
                    {"label": "C", "text": "Converting all function arguments into global variables"},
                    {"label": "D", "text": "Creating multiple threads to execute loops in parallel"}
                ],
                "correct_answer": "A",
                "explanation": "Encapsulation hides internal state representation from outside modifications, allowing access only through public methods."
            },
            {
                "question_text": "What does a double leading underscore (e.g. '__variable') trigger in Python class definitions?",
                "options": [
                    {"label": "A", "text": "Name mangling to prevent accidental overriding in subclasses"},
                    {"label": "B", "text": "Global variable declaration accessible across all modules"},
                    {"label": "C", "text": "Automatic garbage collection prioritization"},
                    {"label": "D", "text": "Static constant compile time optimization"}
                ],
                "correct_answer": "A",
                "explanation": "Double leading underscores trigger name mangling in Python, transforming attribute names to '_ClassName__variable' to avoid inheritance collisions."
            }
        ]
    elif "pointer" in title_lower or "memory" in title_lower or "c " in title_lower or "c programming" in title_lower:
        questions = [
            {
                "question_text": f"In C Programming ({topic_title}), what does dereferencing a pointer using '*ptr' accomplish?",
                "options": [
                    {"label": "A", "text": "Accesses or modifies the memory address stored inside 'ptr'"},
                    {"label": "B", "text": "Accesses or modifies the value stored at the memory address stored in 'ptr'"},
                    {"label": "C", "text": "Frees the allocated VRAM heap memory"},
                    {"label": "D", "text": "Returns the size of the pointer variable in bytes"}
                ],
                "correct_answer": "B",
                "explanation": "The dereference operator '*' accesses the data stored at the memory address stored in the pointer."
            },
            {
                "question_text": "Which dynamic memory allocation function in C initializes allocated memory bytes to zero?",
                "options": [
                    {"label": "A", "text": "malloc()"},
                    {"label": "B", "text": "calloc()"},
                    {"label": "C", "text": "realloc()"},
                    {"label": "D", "text": "alloca()"}
                ],
                "correct_answer": "B",
                "explanation": "'calloc()' allocates memory for an array of elements and zeroes out all allocated bytes, unlike 'malloc()' which leaves garbage values."
            },
            {
                "question_text": "What critical error occurs if dynamically allocated heap memory is not released with 'free()'?",
                "options": [
                    {"label": "A", "text": "Memory Leak"},
                    {"label": "B", "text": "Stack Overflow"},
                    {"label": "C", "text": "Segmentation Fault"},
                    {"label": "D", "text": "Buffer Underrun"}
                ],
                "correct_answer": "A",
                "explanation": "Failing to release heap memory leads to memory leaks, causing the program to consume progressively more VRAM/RAM."
            },
            {
                "question_text": "What is a dangling pointer in low-level execution?",
                "options": [
                    {"label": "A", "text": "A pointer pointing to a memory location that has already been deallocated/freed"},
                    {"label": "B", "text": "A pointer initialized to NULL (0x0)"},
                    {"label": "C", "text": "A pointer pointing to constant string literals"},
                    {"label": "D", "text": "A pointer that points to another pointer"}
                ],
                "correct_answer": "A",
                "explanation": "A dangling pointer stores the address of memory that was freed. Dereferencing it causes undefined behavior or segmentation faults."
            },
            {
                "question_text": "What is the size of a pointer variable on a standard 64-bit architecture?",
                "options": [
                    {"label": "A", "text": "4 bytes"},
                    {"label": "B", "text": "8 bytes"},
                    {"label": "C", "text": "16 bytes"},
                    {"label": "D", "text": "2 bytes"}
                ],
                "correct_answer": "B",
                "explanation": "On 64-bit systems, all pointer variables store a 64-bit (8-byte) memory address regardless of the underlying data type."
            }
        ]
    else:
        questions = [
            {
                "question_text": f"What is the foundational principle underlying '{topic_title}'?",
                "options": [
                    {"label": "A", "text": f"Structured problem solving and conceptual breakdown of {topic_title}"},
                    {"label": "B", "text": "Unstructured random trial and error execution"},
                    {"label": "C", "text": "Deprecated legacy execution pattern"},
                    {"label": "D", "text": "Static constant compile time evaluation only"}
                ],
                "correct_answer": "A",
                "explanation": f"Core mastery of '{topic_title}' relies on structured decomposition of problems and understanding fundamental execution mechanics."
            },
            {
                "question_text": f"Which approach is recommended when implementing algorithms for '{topic_title}'?",
                "options": [
                    {"label": "A", "text": "Breaking the problem down into modular, testable sub-functions"},
                    {"label": "B", "text": "Writing all logic in a single global monolithic loop"},
                    {"label": "C", "text": "Ignoring boundary conditions and error checking"},
                    {"label": "D", "text": "Hardcoding magic numbers directly into production code"}
                ],
                "correct_answer": "A",
                "explanation": "Modular architecture allows clear reasoning, easier debugging, and reusable components."
            },
            {
                "question_text": f"What is the primary benefit of active diagnostic practice in '{topic_title}'?",
                "options": [
                    {"label": "A", "text": "Identifies knowledge gaps early and reinforces long-term conceptual retention"},
                    {"label": "B", "text": "Increases binary compilation speed"},
                    {"label": "C", "text": "Eliminates the need for code review"},
                    {"label": "D", "text": "Bypasses rate limiting constraints"}
                ],
                "correct_answer": "A",
                "explanation": "Frequent diagnostic testing reinforces memory retrieval pathways and highlights areas requiring focused remediation."
            },
            {
                "question_text": f"How do trade-offs impact technical decisions in '{topic_title}'?",
                "options": [
                    {"label": "A", "text": "Balancing time complexity, space complexity, and code maintainability"},
                    {"label": "B", "text": "Prioritizing syntax brevity over readability"},
                    {"label": "C", "text": "Ignoring system constraints"},
                    {"label": "D", "text": "Always choosing maximum memory usage"}
                ],
                "correct_answer": "A",
                "explanation": "Engineering decisions require evaluating space-time trade-offs to choose the optimal solution for given constraints."
            },
            {
                "question_text": f"What is the optimal strategy when encountering an error during execution of '{topic_title}'?",
                "options": [
                    {"label": "A", "text": "Inspecting exact log tracebacks and stepping through state variables"},
                    {"label": "B", "text": "Randomly modifying lines of code without analysis"},
                    {"label": "C", "text": "Ignoring error codes"},
                    {"label": "D", "text": "Deleting unit test assertions"}
                ],
                "correct_answer": "A",
                "explanation": "Systematic debugging using log evidence and stack trace inspection reveals the true root cause."
            }
        ]

    return {
        "title": f"Diagnostic Assessment: {topic_title}",
        "questions": questions
    }
