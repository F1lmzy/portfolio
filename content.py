"""Single source of truth for everything the portfolio renders.

Facts here trace to: ~/Documents/Resume/resume.tex (resume), Crossref plus the
publisher page for the DOI records (venue, volume, pages, citation counts),
OpenAlex for the author's full publication list, the GitHub API plus each
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
    "cv": "cv.pdf",
}

ABOUT = [
    "I am an Electrical Engineering undergraduate at the National University of "
    "Singapore, currently on exchange at Imperial College London. My interests sit "
    "where machine learning meets physical systems: condition monitoring and fault "
    "diagnosis, computer vision, and embedded firmware that has to run in real time.",
    "Most recently I built a full-stack robotics dashboard at Kabam Robotics, and "
    "before that a visualisation application for urban fluid dynamics at A*STAR IHPC.",
]

# ---------------------------------------------------------------- publications
# The author's full journal list, as indexed by OpenAlex for "Sri Rajkavin AV"
# and cross-checked against Crossref. The resume carries only two of these six.
# Titles, venues, volumes, pages and citation counts are the published record.
# Three preprint duplicates are deliberately left out (SSRN 5273389,
# Preprints.org 202409.1688 and 202409.1197): each is the preprint of an article
# already listed here.

PUBLICATIONS = [
    {
        "year": 2026,
        "title": "Signal Decomposition using the Hilbert-Huang Transform and "
                 "CatBoost Classification for Acoustic Signal-Driven Smart Tool "
                 "Wear Detection",
        "authors": ["A. Rajakannu", "K. Vijayalakshmi", "K. P. Ramachandran",
                    "A. V. Sri Rajkavin"],
        "me": "A. V. Sri Rajkavin",
        "venue": "International Journal of Electrical and Electronics Engineering",
        "volume": "13(2)",
        "pages": "60-70",
        "month": "Feb",
        "doi": "10.14445/23488379/IJEEE-V13I2P104",
        "doi_url": "https://doi.org/10.14445/23488379/IJEEE-V13I2P104",
        "citations": 0,
    },
    {
        "year": 2025,
        "title": "Airborne acoustic emission-based intelligent wear detection for "
                 "spatiotemporal data in CNC drill bits using CEEMDAN and ConvLSTM",
        "authors": ["A. Rajakannu", "K. Vijayalakshmi", "A. V. Sri Rajkavin",
                    "J. Wekalao"],
        "me": "A. V. Sri Rajkavin",
        "venue": "Sensors and Actuators A: Physical",
        "volume": "396",
        "pages": "117170",
        "month": "Dec",
        "doi": "10.1016/j.sna.2025.117170",
        "doi_url": "https://doi.org/10.1016/j.sna.2025.117170",
        "citations": 6,
    },
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
    },
    {
        "year": 2024,
        "title": "Intelligent Fault Diagnosis of Rotating Machinery Using Deep "
                 "Learning Algorithms: A Comparative Analysis of MLP, CNN, RNN, "
                 "and LSTM",
        "authors": ["K. Vijayalakshmi", "A. Rajakannu", "K. Mohsina",
                    "K. P. Ramachandran", "A. V. Sri Rajkavin"],
        "me": "A. V. Sri Rajkavin",
        "venue": "International Journal of Electrical and Electronics Engineering",
        "volume": "11(9)",
        "pages": "294-315",
        "month": "Sep",
        "doi": "10.14445/23488379/IJEEE-V11I9P127",
        "doi_url": "https://doi.org/10.14445/23488379/IJEEE-V11I9P127",
        "citations": 8,
    },
    {
        "year": 2024,
        "title": "Condition Monitoring of CNC Drill Bit for the Manufacturing "
                 "Sector Using Wavelet Analysis and Artificial Neural Network Based "
                 "on Feedforward Multilayer Perceptron (MLP)",
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
    },
    {
        "year": 2024,
        "title": "Federated Learning-Based Futuristic Fault Diagnosis and "
                 "Standardization in Rotating Machinery",
        "authors": ["K. Vijayalakshmi", "A. Rajakannu", "K. P. Ramachandran",
                    "A. V. Sri Rajkavin"],
        "me": "A. V. Sri Rajkavin",
        "venue": "International Journal of Electronics and Communication Engineering",
        "volume": "11(9)",
        "pages": "223-236",
        "month": "Sep",
        "doi": "10.14445/23488549/IJECE-V11I9P120",
        "doi_url": "https://doi.org/10.14445/23488549/IJECE-V11I9P120",
        "citations": 6,
    },
]

TOTAL_CITATIONS = sum(p["citations"] for p in PUBLICATIONS)

# ------------------------------------------------------------------- experience

EXPERIENCE = [
    {
        "role": "Software Intern",
        "org": "Kabam Robotics",
        "place": "Singapore",
        "start": "May 2025",
        "end": "Aug 2025",
        "bullets": [
            "Developed a web-based robotics dashboard as a full-stack intern, "
            "implementing frontend designs and backend functionality.",
            "Led the integration of Mixpanel analytics to enable data-driven UI/UX "
            "design improvements, enhancing dashboard usability and user engagement.",
        ],
    },
    {
        "role": "Research Engineering Intern",
        "org": "A*STAR Institute of High Performance Computing (IHPC)",
        "place": "Singapore",
        "start": "May 2024",
        "end": "Jul 2024",
        "bullets": [
            "Developed a web application for visualising urban fluid dynamics "
            "post-processing data, integrating front-end and back-end components.",
            "Implemented parsing techniques for VTP files, improving data processing "
            "throughput for simulation output.",
            "Built the 3D visualisation layer with Three.js, a responsive React and "
            "TypeScript front end, and Django for backend processing.",
        ],
    },
]

# ------------------------------------------------------------------- education

EDUCATION = [
    {
        "school": "National University of Singapore",
        "place": "Singapore",
        "degree": "Bachelor of Engineering (Electrical Engineering), Honours",
        "start": "Aug 2023",
        "end": "May 2027",
        "detail": "Current CAP 4.29 / 5.00, First Class Honours equivalent",
    },
    {
        "school": "Imperial College London",
        "place": "London, UK",
        "degree": "Exchange Student, Electrical and Electronic Engineering",
        "start": "Sep 2025",
        "end": "Jun 2026",
        "detail": "Year-long exchange",
    },
]

# ---------------------------------------------------------------------- thesis

THESIS = {
    "title": "StereoGS: Stereo Video Reconstruction Using Dynamic Gaussian Splatting",
    "org": "Imperial College London",
    "start": "Sep 2025",
    "end": "Jun 2026",
    "repo": "https://github.com/f1lmzyic/StereoGS",
}

# -------------------------------------------------------------------- projects
# Every entry is a repository on the user's own GitHub with a README behind it.
# The two without a repository say so rather than implying one.

PROJECTS = [
    {"name": "Embedded Music Synthesizer", "repo": "https://github.com/F1lmzy/Synth-CW",
     "year": 2026, "kind": "Embedded firmware", "stack": "C++, STM32, CAN"},
    {"name": "Trip Agent", "repo": "https://github.com/F1lmzy/Trip-Agent",
     "year": 2026, "kind": "AI agent", "stack": "Python, FastAPI, ChromaDB"},
    {"name": "Tennis Video Extraction",
     "repo": "https://github.com/F1lmzy/Tennis-Video-Extraction",
     "year": 2026, "kind": "Computer vision", "stack": "Python, YOLO"},
    {"name": "SG Film Calendar", "repo": "https://github.com/F1lmzy/SG-Film-Calendar",
     "year": 2026, "kind": "Data pipeline", "stack": "Python, Google Calendar API"},
    {"name": "NBA Savant", "repo": "https://github.com/F1lmzy/NBA_Savant",
     "year": 2026, "kind": "Data visualisation", "stack": "Python, Plotly, Dash"},
    {"name": "Advent of FPGA, Day 5", "repo": "https://github.com/F1lmzy/Advent_Of_FPGA",
     "year": 2026, "kind": "Digital design", "stack": "OCaml, Hardcaml"},
    {"name": "mac-wallpaper-tui", "repo": "https://github.com/F1lmzy/mac-wallpaper-tui",
     "year": 2026, "kind": "Developer tool", "stack": "Rust, SQLite"},
    {"name": "SpeedRead", "repo": "https://github.com/F1lmzy/SpeedRead",
     "year": 2026, "kind": "Mobile app", "stack": "React Native, Expo"},
    {"name": "Tennis Match Prediction Model", "repo": None,
     "year": 2025, "kind": "Machine learning", "stack": "Python, XGBoost"},
    {"name": "Custom 4-DOF Robot Arm Kinematics", "repo": None,
     "year": 2025, "kind": "Robotics", "stack": "MATLAB"},
]

SKILLS = [
    ("Languages", "English, Tamil, Hindi"),
    ("Programming", "TypeScript, Python, C, C++, SQL, Rust, Julia, MATLAB, OCaml"),
    ("Frameworks", "React, Django, Three.js, React Three Fiber, PyTorch, XGBoost"),
    ("Tools", "Git, Linux, Mixpanel, KiCad, STM32CubeIDE, Fusion360"),
]
