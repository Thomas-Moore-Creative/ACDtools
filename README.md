# ACDtools
Australian Climate Data Tools
```
ACDtools/
│
├── ACDtools/        # Main package directory
│   ├── __init__.py  # Initialize the package
│   ├── ard.py       # ARD module
|   ├── ocean.py     # oceanographic functions
│   └── util.py      # utilities
│
├── tests/                    # Optional: Tests directory for your own testing
│   ├── test_ard.py
│
├── setup.py                  # Simple setup for easy local installation
└── .gitignore                # Optional: Git ignore file for excluding unnecessary files
```
## Installation - locally at NCI
To install the package on your local system, navigate to the root directory of your repo and run the following command:
```bash
pip install -e .
```
## Testing - very basic
Run your tests locally with pytest:
`pytest`
