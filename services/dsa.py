from datetime import date

PROBLEMS = [
    {
        "difficulty": "🟢 EASY",
        "title": "Two Sum",
        "url": "https://leetcode.com/problems/two-sum/",
        "pattern": "Hash map / array",
        "prereq": "Arrays, hash maps, O(n) complexity",
        "goal": "Solve in under 15 minutes.",
    },
    {
        "difficulty": "🟡 MEDIUM",
        "title": "Longest Substring Without Repeating Characters",
        "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/",
        "pattern": "Sliding window / hash set",
        "prereq": "Two pointers, hash sets, window invariants",
        "goal": "Solve in under 30 minutes.",
    },
    {
        "difficulty": "🔴 HARD",
        "title": "Word Ladder",
        "url": "https://leetcode.com/problems/word-ladder/",
        "pattern": "Graph BFS",
        "prereq": "Graphs, BFS, queues, hash sets",
        "goal": "First derive the graph model before coding.",
    },
    {
        "difficulty": "🟢 EASY",
        "title": "Valid Parentheses",
        "url": "https://leetcode.com/problems/valid-parentheses/",
        "pattern": "Stack",
        "prereq": "Stacks, matching pairs",
        "goal": "Solve in under 15 minutes.",
    },
    {
        "difficulty": "🟡 MEDIUM",
        "title": "3Sum",
        "url": "https://leetcode.com/problems/3sum/",
        "pattern": "Sorting / two pointers",
        "prereq": "Sorting, two pointers, duplicate handling",
        "goal": "Explain why sorting enables O(n²).",
    },
    {
        "difficulty": "🔴 HARD",
        "title": "Trapping Rain Water",
        "url": "https://leetcode.com/problems/trapping-rain-water/",
        "pattern": "Two pointers / prefix maxima",
        "prereq": "Arrays, two pointers, invariants",
        "goal": "Derive the O(1)-space approach.",
    },
]


def get_daily_dsa():
    # Stable daily rotation.
    day = date.today().toordinal()
    return [
        PROBLEMS[day % len(PROBLEMS)],
        PROBLEMS[(day + 1) % len(PROBLEMS)],
        PROBLEMS[(day + 2) % len(PROBLEMS)],
    ]
