"""
Socratic Dialogue Engine — Generates intelligent, topic-specific Socratic responses
and probing follow-up questions tailored to the student's message and topic.
"""
from typing import List, Dict, Any


def generate_socratic_response(
    topic_title: str,
    user_message: str,
    history: List[Dict[str, str]] = None,
    skill_level: str = "beginner",
) -> str:
    """
    Generates a dynamic, highly targeted Socratic response that validates student input
    and asks a probing follow-up question to guide them toward deep understanding.
    """
    msg_lower = user_message.strip().lower()
    topic_lower = topic_title.lower()

    # 1. Off-Topic Non-Educational Check
    off_topic_keywords = [
        "recipe", "cake", "food", "cook", "weather", "rain", "movie", "film", "actor", "sports",
        "football", "cricket", "nba", "match", "joke", "funny", "song", "music", "dance", "game",
        "playstation", "xbox", "car", "flight", "hotel", "vacation", "trip", "president", "politics"
    ]
    if any(k in msg_lower for k in off_topic_keywords):
        return (
            f"That's an interesting topic! However, as your Socratic AI Tutor for **'{topic_title}'**, "
            f"my goal is to guide you to master your core study curriculum. "
            f"Let's connect back to **'{topic_title}'**! What specific concept or code snippet would you like to explore next?"
        )

    # 2. Cross-Language & Python vs Java / Technical Queries
    if "python" in msg_lower or "java" in msg_lower or "compare" in msg_lower:
        return (
            f"Great comparative technical question! When comparing Python and Java, notice how Python uses dynamic typing (`x = 10`) "
            f"while Java enforces strict static typing (`int x = 10;`) with JVM bytecode execution. "
            f"In Java, every variable must be explicitly declared before compilation. "
            f"How do you think Java's strict type safety helps prevent bugs at compile-time compared to Python?"
        )

    # 2. Greetings & Introductions
    if msg_lower in ["hi", "hello", "hey", "greetings", "hi there", "hello there", "good morning", "good evening"]:
        return (
            f"Hello! I am your AdaptRoute Socratic AI Tutor for '{topic_title}'. "
            f"Instead of giving plain answers, I help you master concepts through guided step-by-step reasoning! "
            f"What specific concept or question about {topic_title} would you like to explore first?"
        )

    # 2. Identity / "Who are you?"
    elif "who are you" in msg_lower or "what are you" in msg_lower or "your name" in msg_lower:
        return (
            f"I am the AdaptRoute Socratic Tutor Agent! "
            f"My mission is to help you build deep conceptual understanding in {topic_title} by asking targeted probing questions. "
            f"What question or problem are you working on right now?"
        )

    # 3. What is C Programming?
    elif "what is c" in msg_lower or "c programming" in msg_lower or "c language" in msg_lower:
        return (
            "C is a foundational, compiled procedural programming language created by Dennis Ritchie in 1972 at Bell Labs. "
            "It gives developers direct control over system RAM memory addresses and CPU execution. "
            "When you compile a `.c` file, do you know what component converts your human-readable C code into executable machine binary?"
        )

    # 4. Pointers & Memory Addresses
    elif "pointer" in msg_lower or "address" in msg_lower or "&" in msg_lower or "*" in msg_lower:
        return (
            f"Spot on! When working with pointers in {topic_title}, remember that a pointer stores a RAM memory address rather than a raw value. "
            "If you have `int num = 42; int *p = &num;`, what do you think `*p` will evaluate to if we assign `*p = 100`? "
            "Will `num` also change?"
        )

    # 5. Dynamic Memory (malloc, calloc, free)
    elif "malloc" in msg_lower or "free" in msg_lower or "heap" in msg_lower or "memory leak" in msg_lower:
        return (
            "Great observation about memory allocation! Stack memory is cleaned up automatically when functions return, but heap memory allocated via `malloc()` persists. "
            "If you allocate memory with `int *arr = malloc(5 * sizeof(int));`, what critical check should you perform immediately before accessing `arr[0]`?"
        )

    # 6. Main Function & Compilation Pipeline
    elif "main" in msg_lower or "printf" in msg_lower or "compile" in msg_lower or "gcc" in msg_lower or "stdio" in msg_lower:
        return (
            f"You're touching on core execution concepts in {topic_title}! "
            "When the compiler turns your source code into a runnable binary, `main()` serves as the primary entry point. "
            "Why is the header `#include <stdio.h>` required at the top of your program before calling `printf()`?"
        )

    # 7. Structs & Unions
    elif "struct" in msg_lower or "union" in msg_lower or "member" in msg_lower or "->" in msg_lower or "structure" in msg_lower:
        return (
            "Excellent question regarding structures! In C, a `struct` bundles multiple variable types into one custom data object. "
            "When accessing a struct through a pointer `Student *s`, why do we use the arrow operator `s->name` instead of the dot operator `s.name`?"
        )

    # 8. Functions & Recursion
    elif "function" in msg_lower or "recurs" in msg_lower or "return" in msg_lower or "parameter" in msg_lower:
        return (
            f"Functions are the core building blocks of modular programs in {topic_title}! "
            "Every function call pushes a new frame onto the execution stack RAM. "
            "If a function calls itself recursively, what essential base condition must exist to prevent stack overflow crashes?"
        )

    # 9. Memory Architecture / Stack vs Heap
    elif "memory" in msg_lower or "stack" in msg_lower or "ram" in msg_lower:
        return (
            f"Memory management is vital when studying {topic_title}! "
            "C programs manage memory across Text, Data, Stack, and Heap regions. "
            "Local variables declared inside functions live on the Stack. How does Stack memory management differ from Heap dynamic allocation?"
        )

    # 10. Conditionals & Loops
    elif "if" in msg_lower or "loop" in msg_lower or "for" in msg_lower or "while" in msg_lower or "switch" in msg_lower:
        return (
            f"Good thinking on control flow in {topic_title}! In C, any non-zero value evaluates to true in a conditional check. "
            "If you write a `while(count < 5)` loop, what specific operation inside the loop body ensures it doesn't run forever?"
        )

    # 11. Arrays & Strings
    elif "array" in msg_lower or "string" in msg_lower or "char" in msg_lower or "\\0" in msg_lower:
        return (
            "You're zeroing in on key memory patterns! Unlike languages with dynamic string objects, C strings are null-terminated character arrays. "
            "What happens if a character array `char name[5]` is filled with 5 letters without leaving space for the null terminator `\\0`?"
        )

    # 12. Errors, Segfaults & Bugs
    elif "error" in msg_lower or "segfault" in msg_lower or "bug" in msg_lower or "crash" in msg_lower or "fault" in msg_lower:
        return (
            "Debugging is a vital software engineering skill! In C, a Segmentation Fault (SIGSEGV) occurs when a program attempts to read or write illegal memory. "
            "What is the single most common pointer mistake (such as uninitialized or NULL pointers) that triggers a segmentation fault?"
        )

    # 13. Dynamic Context-Aware Fallback
    else:
        return (
            f"That's a very interesting thought about '{user_message}' in relation to {topic_title}! "
            f"To help you connect this with core principles: What underlying rules or data patterns do you think govern this concept? "
            f"How would you test your reasoning in code?"
        )
