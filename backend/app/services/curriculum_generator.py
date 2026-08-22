"""
Curriculum Generator — Intelligent domain-specific curriculum builder.
Generates highly tailored, professional N-week topic breakdowns for C Programming,
Python, DSA, Web Development, Machine Learning, Java, and general goals.
"""
import re
from typing import List, Dict, Any


def generate_tailored_curriculum(learning_goal: str, num_weeks: int = 8) -> List[Dict[str, Any]]:
    """
    Analyzes the learning goal and returns a structured list of week objects,
    each containing specific, realistic pedagogical topics and descriptions.
    """
    goal_lower = learning_goal.lower()

    # 1. C Programming
    if any(k in goal_lower for k in ["c prog", "c lang", "c master", "programming in c", "learn c"]):
        template = [
            ("Week 1: C Syntax & Fundamentals", [
                ("C Environment & First Program", "Installing GCC, understanding main(), printf, scanf, and compilation workflow."),
                ("Variables, Data Types & Operators", "Primitive data types (int, float, char, double), arithmetic and relational operators."),
            ]),
            ("Week 2: Control Flow & Functions", [
                ("Conditionals & Branching", "Mastering if-else, nested conditionals, and switch-case statements."),
                ("Loops & Modular Functions", "for, while, do-while loops, function prototypes, arguments, and return values."),
            ]),
            ("Week 3: Arrays & String Manipulation", [
                ("1D and 2D Arrays", "Array declaration, indexing, iteration, and multi-dimensional matrices in C."),
                ("Strings & String Library", "Character arrays, null-terminator ('\\0'), and string.h utilities (strlen, strcpy, strcmp)."),
            ]),
            ("Week 4: Pointers & Memory Concepts", [
                ("Pointer Basics & Dereferencing", "Memory addresses, address-of operator (&), dereference operator (*), and pointer types."),
                ("Pointer Arithmetic & Arrays", "Navigating arrays with pointers, passing pointers to functions (pass-by-reference)."),
            ]),
            ("Week 5: Dynamic Memory Allocation", [
                ("Heap Memory with malloc & calloc", "Allocating memory dynamically using malloc(), calloc(), and checking NULL pointers."),
                ("Memory Reallocation & Deallocation", "Resizing blocks with realloc(), freeing memory with free(), and avoiding dangling pointers."),
            ]),
            ("Week 6: Structures & Unions", [
                ("Struct Declaration & Usage", "Defining custom data types with struct, accessing members, and struct pointers."),
                ("Unions & Typedef", "Memory sharing in unions, creating type aliases with typedef, and nested structs."),
            ]),
            ("Week 7: File I/O & Preprocessor", [
                ("File Handling in C", "Opening (fopen), reading (fgets/fread), writing (fputs/fwrite), and closing (fclose) text and binary files."),
                ("Preprocessor Directives & Macros", "#define, #include, conditional compilation (#ifndef, #endif), and header files."),
            ]),
            ("Week 8: C Capstone & Best Practices", [
                ("Building a CLI Application", "Integrating structs, pointers, and file storage into a complete C terminal project."),
                ("Debugging & Code Optimization", "Using GDB debugger, Valgrind memory leak checker, and code safety standards."),
            ]),
        ]
    # 2. Data Structures & Algorithms
    elif any(k in goal_lower for k in ["dsa", "data structure", "algorithm", "leetcode", "system design"]):
        template = [
            ("Week 1: Complexity & Arrays", [
                ("Big-O Notation & Complexity Analysis", "Time and space complexity, asymptotic analysis, best/worst/average cases."),
                ("Arrays & Array Manipulations", "Two-pointer technique, sliding window, and prefix sums."),
            ]),
            ("Week 2: Linked Lists", [
                ("Singly Linked Lists", "Node definition, insertion, deletion, and reversal algorithms."),
                ("Doubly & Circular Linked Lists", "Bidirectional navigation, sentinel nodes, and cycle detection (Floyd's algorithm)."),
            ]),
            ("Week 3: Stacks & Queues", [
                ("Stack Implementations & Uses", "LIFO principle, array/linked list stacks, and expression evaluation (infix/postfix)."),
                ("Queue Variants", "FIFO principle, circular queues, deques, and BFS queue patterns."),
            ]),
            ("Week 4: Trees & BSTs", [
                ("Binary Tree Traversals", "In-order, Pre-order, Post-order, and Level-order tree traversals."),
                ("Binary Search Trees (BST)", "Insertion, deletion, search complexity, and BST validation."),
            ]),
            ("Week 5: Heaps & Priority Queues", [
                ("Binary Heaps", "Min-heap, max-heap, heapify operation, and priority queues."),
                ("Heap Applications", "Top-K elements pattern and HeapSort implementation."),
            ]),
            ("Week 6: Graph Algorithms", [
                ("Graph Representations", "Adjacency matrix vs adjacency list, graph traversal algorithms (BFS & DFS)."),
                ("Shortest Path & Topological Sort", "Dijkstra's algorithm, Kahn's algorithm for topological sorting."),
            ]),
            ("Week 7: Dynamic Programming", [
                ("DP Fundamentals", "Overlapping subproblems, optimal substructure, memoization (top-down) vs tabulation (bottom-up)."),
                ("Classic DP Patterns", "Knapsack problem, Longest Common Subsequence, and Fibonacci DP variants."),
            ]),
            ("Week 8: Advanced Algorithms & Review", [
                ("Greedy Algorithms & Backtracking", "Activity selection, N-Queens problem, and state space search."),
                ("Technical Interview Problem Solving", "Mock interview problem solving strategy and optimal pattern matching."),
            ]),
        ]
    # 3. Python & Machine Learning
    elif any(k in goal_lower for k in ["python", "machine learning", "ml", "data science", "ai"]):
        template = [
            ("Week 1: Python Basics & Syntax", [
                ("Variables & Data Types", "Python fundamentals, control flow, functions, and lambda expressions."),
                ("Collections & Data Structures", "Lists, dictionaries, tuples, sets, and comprehension patterns."),
            ]),
            ("Week 2: OOP & Modules", [
                ("Object-Oriented Python", "Classes, objects, inheritance, polymorphism, and dunder methods."),
                ("Modules, Packages & Exceptions", "Importing packages, error handling with try-except, and file I/O."),
            ]),
            ("Week 3: Numerical Python (NumPy)", [
                ("NumPy Arrays & Vectorization", "N-dimensional arrays, indexing, slicing, and broadcast operations."),
                ("Mathematical Operations", "Linear algebra operations, matrix multiplications, and statistics."),
            ]),
            ("Week 4: Data Manipulation (Pandas)", [
                ("DataFrames & Series", "Loading CSV/JSON datasets, indexing, filtering, and summary statistics."),
                ("Data Cleaning & Aggregation", "Handling missing values, merging, joining, and groupby aggregations."),
            ]),
            ("Week 5: Data Visualization", [
                ("Matplotlib Fundamentals", "Line plots, scatter plots, bar charts, and figure customization."),
                ("Seaborn Statistical Graphics", "Distribution plots, heatmaps, box plots, and pairwise relationships."),
            ]),
            ("Week 6: Supervised Learning", [
                ("Linear & Logistic Regression", "Model training, cost functions, gradient descent, and evaluation metrics."),
                ("Classification Algorithms", "Decision trees, random forests, and support vector machines (SVM)."),
            ]),
            ("Week 7: Model Evaluation & Tuning", [
                ("Cross-Validation & Metrics", "Train-test split, K-fold cross validation, precision, recall, F1-score, and ROC-AUC."),
                ("Hyperparameter Optimization", "GridSearchCV and RandomizedSearchCV for optimal model parameters."),
            ]),
            ("Week 8: End-to-End ML Pipeline", [
                ("Feature Engineering & Pipelines", "Preprocessing pipelines, scaling, and categorical encoding."),
                ("Model Deployment & Capstone", "Saving models with Joblib/Pickle and building a simple predictive web app."),
            ]),
        ]
    # 4. Web Development / Fullstack
    elif any(k in goal_lower for k in ["web", "react", "fullstack", "frontend", "backend", "javascript", "node"]):
        template = [
            ("Week 1: Modern HTML5 & CSS3", [
                ("Semantic HTML & Page Structure", "HTML5 elements, form validation, accessibility (ARIA), and SEO basics."),
                ("CSS Flexbox & Grid", "Modern layout techniques, responsive media queries, and utility styling."),
            ]),
            ("Week 2: Modern JavaScript (ES6+)", [
                ("JS Core Concepts", "Variables (let/const), arrow functions, destructuring, and spread operator."),
                ("Asynchronous JS", "Promises, async/await, Fetch API, and handling JSON data."),
            ]),
            ("Week 3: React Fundamentals", [
                ("JSX & React Components", "Component-driven design, props, conditional rendering, and key props."),
                ("State Management", "useState hook, user input handling, and component state flows."),
            ]),
            ("Week 4: Advanced React Hooks", [
                ("Effects & Context API", "useEffect lifecycle, custom hooks, and useContext for global state."),
                ("React Router & Navigation", "Client-side routing, dynamic route parameters, and navigation links."),
            ]),
            ("Week 5: Backend with Node.js & Express", [
                ("Node.js Runtime & Express Server", "RESTful API principles, route handlers, and middleware."),
                ("API Security & Middleware", "CORS, request validation, error-handling middleware, and environment variables."),
            ]),
            ("Week 6: Databases & ORMs", [
                ("SQL & PostgreSQL Basics", "Database schema design, CRUD operations, relationships, and queries."),
                ("ORM Integration", "Connecting Express to PostgreSQL/MongoDB with ORMs and data models."),
            ]),
            ("Week 7: Authentication & Security", [
                ("JWT & Password Hashing", "User registration, password hashing with bcrypt, and JWT access tokens."),
                ("Protected Routes & State", "Securing API endpoints and managing authenticated state in frontend."),
            ]),
            ("Week 8: Fullstack Project Deployment", [
                ("Fullstack Integration", "Connecting React frontend with Express API and managing state."),
                ("Production Deployment", "Deploying applications with Vercel/Render/Docker and environment configuration."),
            ]),
        ]
    # 5. General Subject Fallback Generator
    else:
        clean_goal = re.sub(r'^(i want|how to|learn|master|study|i need to)\s+', '', goal_lower, flags=re.IGNORECASE).title()
        template = [
            (f"Week 1: Introduction to {clean_goal}", [
                ("Core Principles & Key Terminology", f"Foundational concepts, vocabulary, and primary setup for {clean_goal}."),
                ("Basic Operations & Environment", f"Setting up tools, workspace, and executing first practical exercises."),
            ]),
            (f"Week 2: Fundamental Building Blocks", [
                ("Core Structural Patterns", f"Understanding the essential components and rules governing {clean_goal}."),
                ("Standard Workflows & Tools", f"Hands-on application of foundational techniques and best practices."),
            ]),
            (f"Week 3: Intermediate Concepts", [
                ("Methodology & Problem Solving", f"Solving common problems and implementing standard patterns in {clean_goal}."),
                ("Data & Control Logic", f"Managing complexity and structuring logic effectively."),
            ]),
            (f"Week 4: Applied Practice & Refinement", [
                ("Practical Exercise & Scenarios", f"Real-world case studies and guided problem solving."),
                ("Code & Workflow Optimization", f"Improving efficiency, clarity, and maintainability."),
            ]),
            (f"Week 5: Advanced Principles", [
                ("Advanced Techniques", f"Exploring deeper, complex topics and advanced design principles."),
                ("Architectural Overview", f"Structuring modular and scalable solutions in {clean_goal}."),
            ]),
            (f"Week 6: Integration & Ecosystem", [
                ("System Integration", f"Connecting core concepts with peripheral libraries and tools."),
                ("Testing & Error Analysis", f"Debugging, identifying edge cases, and robust execution."),
            ]),
            (f"Week 7: Performance & Best Practices", [
                ("Performance Optimization", f"Refining efficiency, speed, and execution quality."),
                ("Industry Standards & Conventions", f"Adopting production-ready standards and methodologies."),
            ]),
            (f"Week 8: Capstone Project & Mastery", [
                ("Comprehensive Capstone Project", f"Building a complete, standalone project applying all learned concepts."),
                ("Assessment & Next Steps", f"Reviewing overall progress, knowledge retention, and advanced roadmap."),
            ]),
        ]

    # Adjust to requested num_weeks
    weeks_out = []
    for idx in range(num_weeks):
        template_idx = idx % len(template)
        w_title, topics = template[template_idx]

        topics_data = []
        for t_idx, (t_title, t_desc) in enumerate(topics):
            topics_data.append({
                "title": t_title,
                "description": t_desc,
                "order_index": t_idx,
            })

        weeks_out.append({
            "week_number": idx + 1,
            "title": w_title if idx < len(template) else f"Week {idx + 1}: Advanced Module {idx + 1}",
            "topics": topics_data,
        })

    return weeks_out
