import random


coding_options = {
    "language": [
        "Python", "Python", "Rust", "Rust", "C++", "C++", "Go", "Go", "JavaScript",
        "Java", "C#", "Ruby", "Swift", "Kotlin",
        "TypeScript", "C", "Elm", "Zig", "Dart",
        "Scala", "Haskell", "Lua", "PHP", "R",
        "Julia", "Bash", "SQL"
    ],

    "topic": {
        "Algorithms": [
            "Sorting algorithms",
            "Searching algorithms",
            "Binary search",
            "Graph traversal",
            "Shortest path algorithms",
            "Dynamic programming",
            "Greedy algorithms",
            "Backtracking",
            "Divide and conquer",
            "String matching",
            "Computational geometry",
            "Bit manipulation",
            "Hashing algorithms",
            "Optimization algorithms",
            "Tree algorithms"
        ],

        "Data Structures": [
            "Arrays and dynamic arrays",
            "Linked lists",
            "Stacks and queues",
            "Hash maps and hash sets",
            "Binary search trees",
            "Balanced trees",
            "Heaps and priority queues",
            "Graphs",
            "Tries",
            "Disjoint-set union",
            "Segment trees",
            "Fenwick trees",
            "Bloom filters",
            "LRU caches",
            "Ring buffers"
        ],

        "Debugging": [
            "Logic errors",
            "Off-by-one errors",
            "Null and undefined values",
            "Memory leaks",
            "Race conditions",
            "Deadlocks",
            "Incorrect exception handling",
            "Infinite loops",
            "Type errors",
            "Unexpected mutations",
            "Floating-point errors",
            "Indexing mistakes",
            "Serialization bugs",
            "State synchronization bugs",
            "Platform-specific failures"
        ],

        "Performance Optimization": [
            "Time complexity optimization",
            "Space complexity optimization",
            "Memory allocations",
            "Cache locality",
            "Vectorization and SIMD",
            "Parallel processing",
            "Profiling bottlenecks",
            "Lazy evaluation",
            "Memoization",
            "Caching strategies",
            "Database query optimization",
            "Algorithm selection",
            "Reducing I/O overhead",
            "Efficient serialization",
            "Batch processing"
        ],

        "Concurrency and Parallelism": [
            "Threads and processes",
            "Mutexes and locks",
            "Atomics",
            "Race condition prevention",
            "Deadlock prevention",
            "Thread-safe data structures",
            "Async and await",
            "Event loops",
            "Producer-consumer patterns",
            "Work queues",
            "Parallel algorithms",
            "Synchronization primitives",
            "Cancellation and timeouts",
            "Concurrent task scheduling"
        ],

        "Systems Programming": [
            "Memory management",
            "Pointers and references",
            "Stack and heap allocation",
            "Memory ownership",
            "Resource management",
            "Operating system interfaces",
            "File descriptors",
            "Process management",
            "System calls",
            "Memory-mapped files",
            "Binary file formats",
            "Low-level I/O",
            "Interprocess communication",
            "Error handling at system boundaries"
        ],

        "Compilers and Interpreters": [
            "Lexical analysis",
            "Tokenization",
            "Parsing",
            "Abstract syntax trees",
            "Semantic analysis",
            "Type checking",
            "Intermediate representations",
            "Code generation",
            "Bytecode interpreters",
            "Virtual machines",
            "Compiler optimization passes",
            "Symbol tables",
            "Runtime environments",
            "Domain-specific languages"
        ],

        "APIs and Backend Development": [
            "REST APIs",
            "HTTP request handling",
            "Authentication",
            "Authorization",
            "Input validation",
            "Middleware",
            "Rate limiting",
            "Pagination",
            "Error responses",
            "Caching",
            "WebSockets",
            "Background jobs",
            "API versioning",
            "Request retries",
            "Service integration"
        ],

        "Databases": [
            "SQL queries",
            "Schema design",
            "Database indexing",
            "Transactions",
            "Query optimization",
            "Joins",
            "Normalization",
            "Data migrations",
            "Connection pooling",
            "Concurrency control",
            "Caching",
            "Document databases",
            "Data integrity",
            "Pagination strategies"
        ],

        "Networking": [
            "TCP sockets",
            "UDP communication",
            "HTTP protocols",
            "DNS",
            "Client-server architecture",
            "Connection management",
            "Network timeouts",
            "Retry strategies",
            "Packet parsing",
            "Streaming data",
            "Protocol design",
            "Network error handling",
            "Latency optimization",
            "Message framing"
        ],

        "Testing and Code Quality": [
            "Unit testing",
            "Integration testing",
            "Property-based testing",
            "Fuzz testing",
            "Mocking",
            "Test fixtures",
            "Regression testing",
            "Boundary testing",
            "Code coverage",
            "Test-driven development",
            "Refactoring",
            "Static analysis",
            "Code review",
            "Continuous integration",
            "Reproducible bug reports"
        ],

        "Security Engineering": [
            "Input sanitization",
            "SQL injection prevention",
            "Cross-site scripting prevention",
            "Secure authentication",
            "Password hashing",
            "Cryptographic API usage",
            "Secret management",
            "Access control",
            "Secure file handling",
            "Path traversal prevention",
            "Dependency security",
            "Defensive programming",
            "Secure configuration",
            "Safe deserialization"
        ],

        "Embedded Programming": [
            "Microcontroller programming",
            "GPIO",
            "I2C communication",
            "SPI communication",
            "UART communication",
            "Interrupt handling",
            "Timers",
            "PWM",
            "Sensor interfaces",
            "Memory-constrained programming",
            "Real-time scheduling",
            "State machines",
            "Hardware abstraction",
            "Embedded error recovery"
        ],

        "Robotics and Control": [
            "PID controllers",
            "Motor control",
            "Sensor fusion",
            "Odometry",
            "Coordinate transformations",
            "Robot kinematics",
            "Path planning",
            "Motion profiling",
            "State estimation",
            "Inverse kinematics",
            "Trajectory generation",
            "Finite state machines",
            "Robot simulation",
            "Control-loop timing"
        ],

        "Artificial Intelligence and ML": [
            "Tensor operations",
            "Matrix multiplication",
            "Neural network layers",
            "Automatic differentiation",
            "Model inference",
            "Training loops",
            "Batching",
            "Tokenization",
            "Attention mechanisms",
            "Gradient accumulation",
            "Optimizer implementation",
            "Model quantization",
            "Dataset preprocessing",
            "Checkpoint serialization",
            "Evaluation metrics"
        ],

        "File and Data Processing": [
            "JSON parsing",
            "CSV processing",
            "Binary file parsing",
            "Streaming large files",
            "Data validation",
            "Data transformation",
            "Log processing",
            "Deduplication",
            "Compression",
            "Incremental processing",
            "Data pipelines",
            "Unicode handling",
            "Schema validation"
        ],

        "Software Architecture": [
            "Modular design",
            "Dependency injection",
            "Interface design",
            "Design patterns",
            "Separation of concerns",
            "Plugin architectures",
            "Configuration systems",
            "Error propagation",
            "Extensible APIs",
            "Event-driven architecture",
            "Dependency management",
            "Codebase organization"
        ],

        "Developer Tools": [
            "Command-line interfaces",
            "Build systems",
            "Linters",
            "Formatters",
            "Code generators",
            "Configuration parsers",
            "Logging systems",
            "Automation scripts",
            "Package management",
            "Git workflows",
            "Development utilities",
            "Documentation generators"
        ],

        "Graphics and Simulation": [
            "2D rendering",
            "3D transformations",
            "Collision detection",
            "Physics simulation",
            "Game loops",
            "Spatial partitioning",
            "Animation systems",
            "Procedural generation",
            "Numerical simulation",
            "Coordinate systems",
            "Simulation optimization"
        ]
    },

    "difficulty": [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    ],

    "task_type": [
        "Write a function",
        "Implement a complete program",
        "Find and fix a bug",
        "Debug a provided code snippet",
        "Optimize existing code",
        "Refactor poorly structured code",
        "Explain how code works",
        "Predict the output of code",
        "Implement an algorithm",
        "Write unit tests",
        "Design a reusable module",
        "Implement an interface",
        "Review code for correctness",
        "Identify performance bottlenecks",
        "Compare two implementations",
        "Diagnose a runtime error",
        "Fix a compilation error",
        "Implement missing functionality",
        "Improve error handling",
        "Convert code between languages",
        "Explain a complex technical concept",
        "Design a software architecture",
        "Implement a feature from a specification",
        "Analyze edge cases",
        "Fix a failing test",
        "Improve concurrency safety"
    ],

    "scenario": [
        "Command-line utility",
        "Robotics control system",
        "Embedded device",
        "Backend service",
        "REST API",
        "Data processing pipeline",
        "Game engine",
        "Simulation",
        "Developer tool",
        "Desktop application",
        "File management utility",
        "Database-backed application",
        "Distributed service",
        "Machine learning pipeline",
        "Compiler or interpreter",
        "Real-time monitoring system",
        "Automation system",
        "Scientific computing application",
        "Performance-critical library",
        "Existing legacy codebase",
        "Open-source library",
        "School programming project",
        "Real-world engineering project"
    ],

    "constraints": [
        "Use only the standard library",
        "Avoid unnecessary dependencies",
        "Minimize memory allocations",
        "Optimize execution speed",
        "Prioritize readability",
        "Handle invalid inputs gracefully",
        "Handle important edge cases",
        "Avoid unnecessary copying",
        "Follow language idioms",
        "Maintain backward compatibility",
        "Use clear error messages",
        "Include appropriate type annotations",
        "Avoid recursion when practical",
        "Use an iterative approach",
        "Support large inputs",
        "Maintain thread safety",
        "Avoid blocking operations",
        "Preserve existing behavior",
        "Make the code easily testable",
        "Keep the implementation modular",
        "Use deterministic behavior",
        "Support cancellation or timeouts",
        "Explain relevant performance tradeoffs"
    ],

    "answer_style": [
        "Code first, followed by a concise explanation",
        "Explanation followed by complete code",
        "Step-by-step implementation",
        "Concise technical explanation",
        "Detailed technical explanation",
        "Explain design decisions and tradeoffs",
        "Provide code and unit tests",
        "Show the corrected code and explain the bug",
        "Compare approaches with code examples",
        "Production-oriented implementation",
        "Beginner-friendly explanation with examples",
        "Focus on correctness and edge cases",
        "Focus on performance and complexity"
    ]
}


LANGUAGES = {
    "general": ["Python", "Rust", "C++", "Go", "JavaScript", "Java", "C#", "Ruby", "Swift", "Kotlin", "TypeScript", "C", "Elm", "Zig", "Dart", "Scala", "Haskell", "Lua", "PHP", "R", "Julia", "Bash"],
    "applications": ["Python", "Rust", "C++", "Go", "JavaScript", "Java", "C#", "Ruby", "Swift", "Kotlin", "TypeScript", "Dart", "Scala", "Haskell", "Lua", "PHP", "Zig"],
    "systems": ["Rust", "C", "C++", "Zig"],
    "backend": ["Python", "Rust", "C++", "Go", "JavaScript", "TypeScript", "Java", "C#", "Kotlin", "Ruby", "PHP", "Scala"],
    "embedded": ["C", "C++", "Rust", "Zig"],
    "robotics": ["Python", "C++", "C", "Rust", "Go", "Java", "Kotlin", "Julia"],
    "scientific": ["Python", "Julia", "R", "C++", "Rust"],
    "database": ["SQL", "Python", "Go", "Java", "C#", "JavaScript", "TypeScript", "PHP", "Rust", "Kotlin", "Ruby"],
    "tooling": ["Python", "Rust", "C++", "Go", "JavaScript", "TypeScript", "Java", "C#", "Kotlin", "Ruby", "Bash", "Zig", "Lua", "Swift"],
    "graphics": ["Python", "Rust", "C++", "C", "Go", "JavaScript", "TypeScript", "Java", "C#", "Kotlin", "Swift", "Dart", "Julia", "Lua"],
    "compiler": ["Python", "Rust", "C", "C++", "Go", "Java", "C#", "Kotlin", "Swift", "Zig", "Haskell"],
}

PROFILES = {
    "Algorithms": ("general", ["Command-line utility", "Developer tool", "Scientific computing application", "School programming project", "Open-source library"]),
    "Data Structures": ("general", ["Command-line utility", "Developer tool", "Performance-critical library", "Open-source library", "School programming project"]),
    "Debugging": ("applications", ["Command-line utility", "Backend service", "REST API", "Desktop application", "Existing legacy codebase", "Open-source library"]),
    "Performance Optimization": ("applications", ["Command-line utility", "Backend service", "Data processing pipeline", "Performance-critical library", "Scientific computing application"]),
    "Concurrency and Parallelism": ("backend", ["Backend service", "Distributed service", "Real-time monitoring system", "Data processing pipeline", "Performance-critical library"]),
    "Systems Programming": ("systems", ["Command-line utility", "Developer tool", "Performance-critical library", "Real-world engineering project"]),
    "Compilers and Interpreters": ("compiler", ["Compiler or interpreter", "Developer tool", "Command-line utility", "Open-source library", "School programming project"]),
    "APIs and Backend Development": ("backend", ["REST API", "Backend service", "Distributed service", "Database-backed application"]),
    "Databases": ("database", ["Database-backed application", "Backend service", "Data processing pipeline", "REST API"]),
    "Networking": ("backend", ["Backend service", "Distributed service", "Real-time monitoring system", "Developer tool"]),
    "Testing and Code Quality": ("applications", ["Existing legacy codebase", "Open-source library", "Backend service", "Developer tool", "Command-line utility"]),
    "Security Engineering": ("backend", ["Backend service", "REST API", "Database-backed application", "Open-source library"]),
    "Embedded Programming": ("embedded", ["Embedded device", "Robotics control system", "Real-world engineering project"]),
    "Robotics and Control": ("robotics", ["Robotics control system", "Simulation", "Real-world engineering project", "Scientific computing application"]),
    "Artificial Intelligence and ML": ("scientific", ["Machine learning pipeline", "Scientific computing application", "Data processing pipeline", "Performance-critical library"]),
    "File and Data Processing": ("tooling", ["Command-line utility", "Data processing pipeline", "Developer tool", "File management utility", "Automation system"]),
    "Software Architecture": ("applications", ["Backend service", "Desktop application", "Open-source library", "Existing legacy codebase", "Developer tool"]),
    "Developer Tools": ("tooling", ["Command-line utility", "Developer tool", "Automation system", "Open-source library"]),
    "Graphics and Simulation": ("graphics", ["Game engine", "Simulation", "Desktop application", "Scientific computing application"]),
}

SUBTOPIC_LANGUAGE_OVERRIDES = {
    ("Performance Optimization", "Vectorization and SIMD"): "systems",
    ("Performance Optimization", "Cache locality"): "systems",
    ("Performance Optimization", "Memory allocations"): "systems",
    ("Concurrency and Parallelism", "Atomics"): ["Rust", "C", "C++", "Go", "Java", "C#"],
    ("Concurrency and Parallelism", "Mutexes and locks"): ["Rust", "C", "C++", "Go", "Java", "C#", "Kotlin"],
    ("Concurrency and Parallelism", "Thread-safe data structures"): ["Rust", "C", "C++", "Go", "Java", "C#", "Kotlin"],
    ("Networking", "Packet parsing"): ["Python", "Rust", "C", "C++", "Go", "Java", "C#"],
    ("Graphics and Simulation", "3D transformations"): ["Python", "Rust", "C++", "C", "JavaScript", "TypeScript", "Java", "C#", "Kotlin", "Swift", "Dart", "Julia"],
    ("Artificial Intelligence and ML", "Gradient accumulation"): ["Python", "Julia", "C++"],
    ("Artificial Intelligence and ML", "Training loops"): ["Python", "Julia", "C++"],
    ("Performance Optimization", "Database query optimization"): [
    "Python", "Go", "Java", "C#", "JavaScript",
    "TypeScript", "PHP", "Rust", "Kotlin", "Ruby"
    ],
}

# SQL is a query language, not a substitute for a backend/application language.
SQL_SUBTOPICS = {"SQL queries", "Schema design", "Database indexing", "Transactions", "Query optimization", "Joins", "Normalization", "Data migrations", "Data integrity", "Pagination strategies"}
SQL_TASKS = {"Write a function", "Explain how code works", "Optimize existing code", "Review code for correctness", "Compare two implementations", "Diagnose a runtime error", "Implement missing functionality", "Explain a complex technical concept", "Analyze edge cases"}

# Tasks needing code in the *question* are restricted to scenarios where an
# example source snippet can be included. This is enforced again in the prompt.
CODE_INPUT_TASKS = {
    "Find and fix a bug", "Debug a provided code snippet", "Optimize existing code",
    "Refactor poorly structured code", "Explain how code works", "Predict the output of code",
    "Review code for correctness", "Identify performance bottlenecks",
    "Compare two implementations", "Diagnose a runtime error", "Fix a compilation error",
    "Implement missing functionality", "Improve error handling", "Fix a failing test",
    "Improve concurrency safety", "Convert code between languages"
}
EXPLANATION_TASKS = {"Explain how code works", "Explain a complex technical concept", "Analyze edge cases", "Design a software architecture", "Review code for correctness"}
CODE_ANSWER_STYLES = [x for x in coding_options["answer_style"] if x not in {"Beginner-friendly explanation with examples", "Concise technical explanation", "Detailed technical explanation"}]


BASE_CONSTRAINTS = ["Avoid unnecessary dependencies", "Prioritize readability", "Handle invalid inputs gracefully", "Handle important edge cases", "Follow language idioms", "Use clear error messages", "Make the code easily testable", "Keep the implementation modular", "Use deterministic behavior", "Explain relevant performance tradeoffs"]
PERF_CONSTRAINTS = ["Minimize memory allocations", "Optimize execution speed", "Avoid unnecessary copying", "Support large inputs"]
CONCURRENT_CONSTRAINTS = ["Maintain thread safety", "Avoid blocking operations", "Support cancellation or timeouts"]
MAINTENANCE_CONSTRAINTS = ["Maintain backward compatibility", "Preserve existing behavior"]


def choose_coding_options(rng=random):
    topic = rng.choice(list(coding_options["topic"]))
    subtopic = rng.choice(coding_options["topic"][topic])
    family, scenarios = PROFILES[topic]
    languages = list(LANGUAGES[family])
    override = SUBTOPIC_LANGUAGE_OVERRIDES.get((topic, subtopic))
    if override is not None:
        languages = [x for x in languages if x in (LANGUAGES[override] if isinstance(override, str) else override)]

    if topic == "Databases" and subtopic not in SQL_SUBTOPICS:
        languages = [x for x in languages if x != "SQL"]

    compatible = set(languages)
    languages = [
        lang for lang in coding_options["language"]
        if lang in compatible
    ]
    if not languages:
        raise ValueError(f"No compatible language for {topic} / {subtopic}")

    language = rng.choice(languages)
    scenario_choices = list(scenarios)
    if language == "SQL":
        scenario_choices = ["Database-backed application", "Data processing pipeline"]
    elif language == "Bash":
        scenario_choices = ["Command-line utility", "Automation system", "Developer tool", "File management utility"]
    elif topic == "Performance Optimization" and subtopic == "Database query optimization":
        scenario_choices = ["Backend service", "Data processing pipeline"]
    elif topic == "Robotics and Control":
        if language in {"Python", "Julia", "Go", "Java", "Kotlin"}:
            scenario_choices = ["Simulation", "Scientific computing application", "Robotics control system"]
        if language == "C":
            scenario_choices = ["Robotics control system", "Real-world engineering project"]

    tasks = list(coding_options["task_type"])
    if language == "SQL":
        tasks = [x for x in tasks if x in SQL_TASKS]
    if language in {"Python", "JavaScript", "TypeScript", "Ruby", "PHP", "Bash", "Lua", "R", "Julia"}:
        tasks = [x for x in tasks if x != "Fix a compilation error"]
    if topic not in {"Concurrency and Parallelism", "Systems Programming", "Networking", "Performance Optimization"}:
        tasks = [x for x in tasks if x != "Improve concurrency safety"]
    if topic not in {"Testing and Code Quality", "Debugging"}:
        tasks = [x for x in tasks if x != "Fix a failing test"]
    task = rng.choice(tasks)

    constraints = list(BASE_CONSTRAINTS)
    if topic in {"Performance Optimization", "Algorithms", "Data Structures", "Systems Programming", "Artificial Intelligence and ML", "File and Data Processing"}:
        constraints += PERF_CONSTRAINTS
    if topic in {"Concurrency and Parallelism", "Networking", "APIs and Backend Development"} and language != "SQL":
        constraints += CONCURRENT_CONSTRAINTS
    if task in CODE_INPUT_TASKS:
        constraints += MAINTENANCE_CONSTRAINTS
    if language in {"Python", "Java", "Kotlin", "TypeScript", "Swift"}:
        constraints.append("Include appropriate type annotations")
    if language not in {"SQL", "Elm", "Bash"}:
        constraints.append("Use only the standard library")
    if topic == "Algorithms" and "Recursion" not in subtopic:
        constraints += ["Avoid recursion when practical", "Use an iterative approach"]
    constraints = [x for x in constraints if x in coding_options["constraints"]]

    styles = (
        list(coding_options["answer_style"])
        if task in EXPLANATION_TASKS
        else list(CODE_ANSWER_STYLES)
    )

    if task in {
        "Explain a complex technical concept",
        "Design a software architecture",
        "Analyze edge cases",
    }:  
        styles = [
            s for s in styles
            if s not in {
                "Provide code and unit tests",
                "Production-oriented implementation",
                "Step-by-step implementation",
            }
    ]

    BUG_FIX_TASKS = {
        "Find and fix a bug",
        "Debug a provided code snippet",
        "Fix a compilation error",
        "Fix a failing test",
        "Diagnose a runtime error",
    }

    if task not in BUG_FIX_TASKS:
        styles = [
            s for s in styles
            if s != "Show the corrected code and explain the bug"
        ]

    if task in BUG_FIX_TASKS:
        styles = [
            s for s in styles
            if s != "Compare approaches with code examples"
        ]

    if language == "SQL":
        styles = [
            s for s in styles
            if s != "Provide code and unit tests"
        ]
    
    return {
        "language": language,
        "topic": topic,
        "subtopic": subtopic,
        "difficulty": rng.choice(coding_options["difficulty"]),
        "task_type": task,
        "scenario": rng.choice(scenario_choices),
        "constraints": rng.choice(constraints),
        "answer_style": rng.choice(styles),
        "requires_source_code": task in CODE_INPUT_TASKS,
    }

general_options = {
    "category": {
        "Mathematics": [
            "Algebra", "Geometry", "Trigonometry", "Calculus",
            "Linear Algebra", "Probability", "Statistics",
            "Number Theory", "Discrete Mathematics",
            "Mathematical Proofs", "Optimization"
        ],
        "Physics": [
            "Classical Mechanics", "Electricity and Magnetism",
            "Thermodynamics", "Optics", "Waves and Sound",
            "Quantum Mechanics", "Relativity", "Fluid Dynamics",
            "Astrophysics"
        ],
        "Chemistry": [
            "Atomic Structure", "Chemical Reactions",
            "Stoichiometry", "Organic Chemistry",
            "Chemical Bonding", "Acids and Bases",
            "Thermochemistry", "Electrochemistry"
        ],
        "Biology": [
            "Cell Biology", "Genetics", "Evolution",
            "Ecology", "Human Anatomy", "Physiology",
            "Microbiology", "Biochemistry", "Neuroscience"
        ],
        "Engineering": [
            "Mechanical Engineering", "Electrical Engineering",
            "Robotics", "Control Systems", "Materials Science",
            "Structural Engineering", "Manufacturing",
            "Circuit Design", "Aerospace Engineering"
        ],
        "Computer Science": [
            "Computer Architecture", "Operating Systems",
            "Computer Networks", "Databases", "Cybersecurity",
            "Artificial Intelligence", "Machine Learning",
            "Compilers", "Distributed Systems",
            "Algorithms and Complexity"
        ],
        "History": [
            "Ancient Civilizations", "Medieval History",
            "Renaissance", "Industrial Revolution",
            "World War I", "World War II", "Cold War",
            "American History", "World History",
            "History of Science and Technology"
        ],
        "Geography": [
            "Physical Geography", "Human Geography",
            "Climate", "Geology", "Natural Resources",
            "Maps and Navigation", "Countries and Regions",
            "Environmental Geography"
        ],
        "Economics": [
            "Microeconomics", "Macroeconomics",
            "Supply and Demand", "Inflation",
            "International Trade", "Economic Systems",
            "Personal Finance", "Business Economics"
        ],
        "Philosophy": [
            "Ethics", "Logic", "Epistemology",
            "Metaphysics", "Philosophy of Science",
            "Political Philosophy", "Moral Dilemmas"
        ],
        "Writing and Language": [
            "Grammar", "Creative Writing", "Essay Writing",
            "Persuasive Writing", "Technical Writing",
            "Literary Analysis", "Rhetoric",
            "Editing and Revision", "Communication"
        ],
        "Reasoning and Problem Solving": [
            "Deductive Reasoning", "Inductive Reasoning",
            "Causal Reasoning", "Critical Thinking",
            "Decision Making", "Pattern Recognition",
            "Multi-Step Problem Solving",
            "Evaluating Evidence", "Identifying Assumptions"
        ],
        "Everyday Assistance": [
            "Planning", "Organization", "Time Management",
            "Learning New Skills", "Troubleshooting",
            "Comparing Options", "Making Decisions",
            "Explaining Instructions", "Practical Advice",
            "Brainstorming"
        ],
        "Arts and Culture": [
            "Music Theory", "Art History", "Visual Arts",
            "Architecture", "Film Analysis",
            "Literature", "Cultural Traditions"
        ]
    },

    "difficulty": [
        "Beginner",
        "Intermediate",
        "Advanced",
        "Expert"
    ],

    "task_type": [
        "Explain a concept",
        "Answer a factual question",
        "Solve a problem",
        "Compare two concepts",
        "Analyze a situation",
        "Evaluate an argument",
        "Identify an error",
        "Explain why something happens",
        "Provide practical guidance",
        "Summarize information",
        "Apply knowledge to a scenario",
        "Make a recommendation",
        "Interpret provided information",
        "Teach a concept using examples",
        "Challenge a misconception",
        "Reason through a hypothetical situation"
    ],

    "question_style": [
        "Short direct question",
        "Detailed question",
        "Real-world scenario",
        "Curious follow-up question",
        "Multi-part question",
        "Question with constraints",
        "Question containing a misconception",
        "Question asking for examples",
        "Question asking for a comparison",
        "Question requiring multiple reasoning steps",
        "Informal conversational question",
        "Technical question"
    ],

    "response_style": [
        "Concise and direct",
        "Detailed explanation",
        "Beginner-friendly",
        "Technical and precise",
        "Step-by-step explanation",
        "Example-driven",
        "Conversational and natural",
        "Structured with clear sections",
        "Explain the reasoning briefly",
        "Practical and actionable"
    ],

    "context": [
        "No additional context",
        "The user is a beginner",
        "The user has intermediate knowledge",
        "The user is technically experienced",
        "The user has limited time",
        "The user has limited resources",
        "The user provides specific constraints",
        "The user is confused about a concept",
        "The user wants to understand why",
        "The user needs help making a decision",
        "The user has already tried something",
        "The user wants a real-world application"
    ]
}

template_general = """
You are generating high-quality supervised fine-tuning
data for a general-purpose AI assistant.

Create exactly ONE original user question and its
ideal assistant response.

Category: {category}
Topic: {topic}
Difficulty: {difficulty}
Task type: {task_type}
Question style: {question_style}
Response style: {response_style}
Context: {context}

Requirements:
- The question must sound like something a real user
  might ask.
- Produce a helpful, accurate, natural response.
- Match the requested difficulty and response style.
- Avoid unsupported claims and fabricated sources.
- Avoid questions requiring rapidly changing facts
  unless all necessary facts are supplied in context.
- Include uncertainty when the answer isn't definite.
- Do not expose hidden reasoning or internal analysis.
- Return ONLY valid JSON with "question" and "answer".
- Do not include markdown fences around the JSON.
- When a task requires source material, include that
  material in the generated user question.
- Difficulty refers to subject complexity, not user
  expertise. Adapt the explanation to the user.
"""

template_code = """
You are generating high-quality supervised fine-tuning
data for a general-purpose AI assistant.

Create exactly ONE original coding question and its
ideal answer.

Language: {language}
Topic: {topic}
Subtopic: {subtopic}
Difficulty: {difficulty}
Task type: {task_type}
Scenario: {scenario}
Constraints: {constraints}
Answer style: {answer_style}
Question must include source code: {requires_source_code}

Requirements:
- The question must be specific, realistic, and solvable.
- Use only language APIs and capabilities appropriate to the selected
  language, subtopic, and scenario.
- If the task requires source code in the question, supply a realistic
  original code snippet (or failing test/error as appropriate) that
  contains enough information to answer it.
- Use an executable code example only when appropriate to the task.
- Never make up runtime output, compiled behavior, or test results.
- For SQL, state the SQL dialect in the question; prefer SQLite
  unless the task requires another dialect.
- For code conversion tasks, include the original language and code
  snippet in the question and name the destination language.
- Do not force a scenario that the chosen language cannot support.
- Vary the structure and wording naturally.
- The answer must be accurate, complete, and useful.
- Include working code when appropriate.
- Handle important edge cases.
- Never invent test results or claim code was executed.
- Do not expose hidden reasoning or internal analysis.
- Return ONLY valid JSON with "question" and "answer".
- Do not include markdown fences around the JSON.
- Match the answer style to the task.
- Never pretend to correct code that the question
  does not provide.
"""

def generate_prompt(rng=random):
    dataset_type = "general" if rng.random() < 0.6 else "coding"

    if dataset_type == "coding":
        selected = choose_coding_options(rng)
        return template_code.format(**selected)

    category = rng.choice(list(general_options["category"]))

    selected = {
        "category": category,
        "topic": rng.choice(general_options["category"][category]),
        "difficulty": rng.choice(general_options["difficulty"]),
        "task_type": rng.choice(general_options["task_type"]),
        "question_style": rng.choice(general_options["question_style"]),
        "response_style": rng.choice(general_options["response_style"]),
        "context": rng.choice(general_options["context"]),
    }

    return template_general.format(**selected)


if __name__ == "__main__":
    print(generate_prompt())