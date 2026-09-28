"""Single source of truth for everything the portfolio renders.

Facts here trace to: ~/Documents/Resume/resume.tex (resume), Crossref for the two
DOI records (venue, volume, pages, citation counts), the GitHub API plus each
repository's README (projects), and jobscan/application_config.json (dates).
Do not add a claim without an artifact behind it.
"""

NAME = "Kavin Sriraj"
TAGLINE = "Electrical Engineering undergraduate · Singapore"
LOCATION = "Singapore"

CONTACT = {
    "email": "srirajkavin@u.nus.edu",
    "alt_email": "ka1525@ic.ac.uk",
    "github": "https://github.com/F1lmzy",
    "github_handle": "F1lmzy",
    "linkedin": "https://www.linkedin.com/in/kavin-sriraj",
    "linkedin_handle": "kavin-sriraj",
    "cv": "/cv",
}

ABOUT = [
    "I am an Electrical Engineering undergraduate at the National University of "
    "Singapore, currently on exchange at Imperial College London. My interests sit "
    "where machine learning meets physical systems: condition monitoring and fault "
    "diagnosis, computer vision, and embedded firmware that has to run in real time.",
    "Most recently I built a full-stack robotics dashboard at Kabam Robotics, and "
    "before that a visualisation application for urban fluid dynamics at A*STAR IHPC. "
    "This page is a single static document, pre-rendered and themed with all 187 "
    "Monkeytype themes.",
]

# ---------------------------------------------------------------- publications
# Author order, venue, volume, pages and citation counts come from the DOI records
# (Crossref). Both papers are on applications of machine learning to machine
# condition monitoring and fault diagnosis.

PUBLICATIONS = [
    {
        "year": 2025,
        "title": "Performance Analysis of Machine Learning and Deep Learning "
                 "Techniques in Diagnosing Imbalance Using Machine Fault Simulator: "
                 "A Case Study",
        "authors": ["K. Vijayalakshmi", "A. Rajakannu", "K. P. Ramachandran",
                    "K. Mohsina", "A. V. Sri Rajkavin"],
        "me": "A. V. Sri Rajkavin",
        "venue": "International Journal of Engineering Trends and Technology",
        "volume": "73(1)",
        "pages": "266-287",
        "month": "Jan",
        "doi": "10.14445/22315381/IJETT-V73I1P123",
        "doi_url": "https://doi.org/10.14445/22315381/IJETT-V73I1P123",
        "citations": 3,
        "topics": ["Machine learning", "Fault diagnosis"],
        "summary": "Compares machine learning and deep learning pipelines for "
                   "diagnosing rotor imbalance on a machine fault simulator, using "
                   "vibration signals collected across controlled fault conditions.",
    },
    {
        "year": 2024,
        "title": "Condition Monitoring of CNC Drill Bit for the Manufacturing Sector "
                 "Using Wavelet Analysis and Artificial Neural Network Based on "
                 "Feedforward Multilayer Perceptron (MLP)",
        "authors": ["A. Rajakannu", "K. P. Ramachandran", "K. Vijayalakshmi",
                    "A. V. Sri Rajkavin"],
        "me": "A. V. Sri Rajkavin",
        "venue": "International Journal of Electrical and Electronics Engineering",
        "volume": "11(12)",
        "pages": "61-75",
        "month": "Dec",
        "doi": "10.14445/23488379/IJEEE-V11I12P106",
        "doi_url": "https://doi.org/10.14445/23488379/IJEEE-V11I12P106",
        "citations": 5,
        "topics": ["Condition monitoring", "Signal processing", "Machine learning"],
        "summary": "Wavelet decomposition of machining vibration and acoustic "
                   "signals feeding a feedforward multilayer perceptron that "
                   "classifies CNC drill bit wear state.",
    },
]

PUBLICATION_TOPICS = sorted({t for p in PUBLICATIONS for t in p["topics"]})

# ------------------------------------------------------------------- experience

EXPERIENCE = [
    {
        "role": "Software Intern",
        "org": "Kabam Robotics",
        "place": "Singapore",
        "start": "May 2025",
        "end": "Aug 2025",
        "summary": "Full-stack development on a web-based robotics fleet dashboard.",
        "bullets": [
            "Developed a web-based robotics dashboard as a full-stack intern, "
            "implementing frontend designs and backend functionality.",
            "Led the integration of Mixpanel analytics to enable data-driven UI/UX "
            "design improvements, enhancing dashboard usability and user engagement.",
        ],
        "stack": ["TypeScript", "React", "Mixpanel"],
    },
    {
        "role": "Research Engineering Intern",
        "org": "A*STAR Institute of High Performance Computing (IHPC)",
        "place": "Singapore",
        "start": "May 2024",
        "end": "Jul 2024",
        "summary": "Post-processing and visualisation tooling for urban fluid dynamics.",
        "bullets": [
            "Developed a web application for visualising urban fluid dynamics "
            "post-processing data, integrating front-end and back-end components.",
            "Implemented parsing techniques for VTP files, improving data processing "
            "throughput for simulation output.",
            "Built the 3D visualisation layer with Three.js, a responsive React and "
            "TypeScript front end, and Django for backend processing.",
        ],
        "stack": ["Three.js", "React", "Django", "Python"],
    },
]

# ------------------------------------------------------------------- education

EDUCATION = [
    {
        "school": "National University of Singapore",
        "place": "Singapore",
        "degree": "Bachelor of Engineering (Electrical Engineering), Honours",
        "start": "Aug 2023",
        "end": "May 2027 (expected)",
        "detail": "Current CAP 4.29 / 5.00 (First Class Honours equivalent).",
    },
    {
        "school": "Imperial College London",
        "place": "London, UK",
        "degree": "Exchange Student, Electrical and Electronic Engineering",
        "start": "Sep 2025",
        "end": "Jun 2026",
        "detail": "Year-long exchange, including the Bachelor thesis below.",
    },
]

# ---------------------------------------------------------------------- thesis

THESIS = {
    "title": "StereoGS: Stereo Video Reconstruction Using Dynamic Gaussian Splatting",
    "org": "Imperial College London",
    "start": "Sep 2025",
    "end": "Jun 2026",
    "repo": "https://github.com/f1lmzyic/StereoGS",
    "summary": "Fitting deformable 4D Gaussians to monocular video so that "
               "synchronised stereo views can be rendered from virtual cameras.",
    "bullets": [
        "Reconstructed stereo video from monocular footage by fitting deformable 4D "
        "Gaussians to Structure-from-Motion camera poses and rendering synchronised "
        "left and right views from virtual stereo cameras.",
        "Avoided monocular depth priors, adding optical-flow motion priors and a "
        "synthetic stereo renderer.",
        "Evaluated on the South Kensington Stereo Video dataset with PSNR, SSIM, "
        "LPIPS, temporal flicker, TEPE and stereo disparity consistency.",
    ],
    "stack": ["Python", "PyTorch", "Gaussian splatting", "COLMAP"],
}

# -------------------------------------------------------------------- projects
# Every entry is a repository on the user's own GitHub accounts with a README
# behind the description. `fork` is recorded so nothing is presented as original
# work when it is not.

PROJECTS = [
    {
        "slug": "synth-cw",
        "name": "Embedded Music Synthesizer",
        "repo": "https://github.com/F1lmzy/Synth-CW",
        "repo_label": "F1lmzy/Synth-CW",
        "year": 2026,
        "summary": "Real-time polyphonic synthesizer firmware for an STM32 "
                   "Nucleo-L432KC, with an OLED UI and CAN bus multi-board support.",
        "stack": ["C++", "STM32", "PlatformIO", "CAN", "FreeRTOS"],
        "detail": [
            "Generates polyphonic audio by PWM at 22 kHz while servicing note input, "
            "an OLED display and CAN traffic on one microcontroller.",
            "Documents the real-time analysis behind the design: minimum initiation "
            "intervals, worst case execution time, CPU utilisation and critical "
            "instant analysis for each task.",
            "Keyboards are hot swappable over CAN, so extra boards join the polyphony "
            "without a reset.",
        ],
        "kind": "Embedded firmware",
    },
    {
        "slug": "trip-agent",
        "name": "Trip Agent",
        "repo": "https://github.com/F1lmzy/Trip-Agent",
        "repo_label": "F1lmzy/Trip-Agent",
        "year": 2026,
        "summary": "A FastAPI travel-planning agent that builds multi-day itineraries "
                   "with hotels and flights, with layered memory and tool routing.",
        "stack": ["Python", "FastAPI", "ChromaDB", "RAG", "MCP", "SSE"],
        "detail": [
            "Combines deterministic prompt parsing and planning with multi-agent "
            "routing and tool execution rather than leaving the itinerary to free-form "
            "generation.",
            "Short-term conversation memory sits alongside long-term preference memory "
            "in ChromaDB, so repeat requests keep dietary, accessibility and budget "
            "constraints across sessions.",
            "Exposes tools over MCP, streams responses with Server-Sent Events, and "
            "serves a small browser UI plus a REST and streaming chat API.",
        ],
        "kind": "AI agent",
    },
    {
        "slug": "tennis-video-extraction",
        "name": "Tennis Video Extraction",
        "repo": "https://github.com/F1lmzy/Tennis-Video-Extraction",
        "repo_label": "F1lmzy/Tennis-Video-Extraction",
        "year": 2026,
        "summary": "Computer vision pipeline that maps players and the ball from "
                   "fixed-camera tennis footage onto 2D court-plane coordinates.",
        "stack": ["Python", "YOLO", "OpenCV", "uv", "pytest"],
        "detail": [
            "Tracks players and the ball with a YOLO model, then homographies the "
            "detections onto a top-down court plane.",
            "Packaged as a CLI with a written specification, an implementation plan, "
            "tests and Ruff linting.",
            "Published validation and benchmark documents are still templates, so the "
            "project is described here by method only.",
        ],
        "kind": "Computer vision",
    },
    {
        "slug": "sg-film-calendar",
        "name": "SG Film Calendar",
        "repo": "https://github.com/F1lmzy/SG-Film-Calendar",
        "repo_label": "F1lmzy/SG-Film-Calendar",
        "year": 2026,
        "summary": "Scrapes Singapore film screenings into a shared Google Calendar "
                   "and accumulates a historic archive.",
        "stack": ["Python", "Google Calendar API", "Scraping"],
        "detail": [
            "Reads Filmhouse.sg and Singapore Film Society, including the SFS "
            "Eventive schedule JSON, and expands bundled events into individual "
            "screenings.",
            "Creates or updates a Google Calendar event per screening with "
            "deterministic IDs, so re-runs update rather than duplicate.",
            "Keeps every screening ever seen as an archive for later analysis.",
        ],
        "kind": "Data pipeline",
    },
    {
        "slug": "nba-savant",
        "name": "NBA Savant",
        "repo": "https://github.com/F1lmzy/NBA_Savant",
        "repo_label": "F1lmzy/NBA_Savant",
        "year": 2026,
        "summary": "Plotly and Dash dashboard that renders Baseball Savant style "
                   "percentile cards for NBA players on top of nba_api.",
        "stack": ["Python", "Plotly", "Dash", "pandas"],
        "detail": [
            "Percentile bars across value, scoring, creation and defence, computed "
            "against the players who meet the selected minutes filter.",
            "Ships player summary cards, a league leaderboard, radar and shot charts, "
            "career trends and a sortable player table.",
        ],
        "kind": "Data visualisation",
    },
    {
        "slug": "advent-of-fpga",
        "name": "Advent of FPGA, Day 5",
        "repo": "https://github.com/F1lmzy/Advent_Of_FPGA",
        "repo_label": "F1lmzy/Advent_Of_FPGA",
        "year": 2026,
        "summary": "Hardware design in OCaml with Hardcaml for the Jane Street Advent "
                   "of FPGA challenge.",
        "stack": ["OCaml", "Hardcaml", "RTL"],
        "detail": [
            "Loads ranges into a memory structure and answers queries against them "
            "with a pipelined datapath, driven by a control FSM that handles load, "
            "query and aggregation phases.",
            "Developed with a testbench harness and verified through simulation "
            "rather than on hardware.",
        ],
        "kind": "Digital design",
    },
    {
        "slug": "mac-wallpaper-tui",
        "name": "mac-wallpaper-tui",
        "repo": "https://github.com/F1lmzy/mac-wallpaper-tui",
        "repo_label": "F1lmzy/mac-wallpaper-tui",
        "year": 2026,
        "summary": "Terminal wallpaper manager for macOS with live image previews, "
                   "favourites and history in SQLite.",
        "stack": ["Rust", "SQLite", "TUI"],
        "detail": [
            "Renders live previews through the Kitty, Sixel and iTerm2 graphics "
            "protocols, with async image loading so the UI never blocks.",
            "Vim-style keybindings, a favourites list and a recent-wallpaper history "
            "persisted in SQLite.",
        ],
        "kind": "Developer tool",
    },
    {
        "slug": "speedread",
        "name": "SpeedRead",
        "repo": "https://github.com/F1lmzy/SpeedRead",
        "repo_label": "F1lmzy/SpeedRead",
        "year": 2026,
        "summary": "React Native speed reading app that flashes text one word at a "
                   "time at the reader's optimal viewing position.",
        "stack": ["React Native", "Expo", "JavaScript"],
        "detail": [
            "Rapid serial visual presentation display with the optimal viewing "
            "position of each word pinned to a fixed red anchor, which minimises eye "
            "movement.",
            "Adjustable reading speed from 100 to 1000 words per minute, taking text "
            "pasted directly or extracted from EPUB and PDF files.",
        ],
        "kind": "Mobile app",
    },
    {
        "slug": "tennis-prediction",
        "name": "Tennis Match Prediction Model",
        "repo": None,
        "repo_label": "no public repository",
        "year": 2025,
        "summary": "Machine learning model predicting tennis match outcomes from "
                   "player statistics and historical results.",
        "stack": ["Python", "XGBoost", "Feature engineering"],
        "detail": [
            "Gradient boosted trees over engineered player statistics and historical "
            "match records.",
            "No repository was published for this project, so no results are quoted "
            "here.",
        ],
        "kind": "Machine learning",
    },
    {
        "slug": "robot-arm-kinematics",
        "name": "Custom 4-DOF Robot Arm Kinematics",
        "repo": None,
        "repo_label": "no public repository",
        "year": 2025,
        "summary": "Forward and inverse kinematics written from scratch for an "
                   "OpenManipulator-X arm, without robotics toolboxes.",
        "stack": ["MATLAB", "Kinematics"],
        "detail": [
            "Derived and implemented the kinematics directly as maths, using no "
            "external robotics library.",
        ],
        "kind": "Robotics",
    },
]

SKILLS = [
    ("Languages", ["English", "Tamil", "Hindi"]),
    ("Programming", ["TypeScript", "Python", "C", "C++", "SQL", "Rust", "Julia",
                     "MATLAB", "OCaml"]),
    ("Frameworks", ["React", "Django", "Three.js", "React Three Fiber", "PyTorch",
                    "XGBoost"]),
    ("Tools", ["Git", "Linux", "Mixpanel", "KiCad", "STM32CubeIDE", "Fusion360"]),
]

SECTIONS = [
    ("about", "About"),
    ("publications", "Publications"),
    ("thesis", "Bachelor Thesis"),
    ("projects", "Projects"),
    ("experience", "Experience"),
    ("education", "Education"),
    ("skills", "Skills"),
]
