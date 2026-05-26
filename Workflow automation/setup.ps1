"""
PowerShell script for setting up and running the Workflow Automation system.

Usage:
  .\setup.ps1 -Setup
  .\setup.ps1 -RunExample -ExampleNumber 1
"""

param(
    [switch]$Setup,
    [switch]$RunExample,
    [int]$ExampleNumber = 1,
    [switch]$ShowHelp
)

function Show-Help {
    Write-Host @"
Leceil Morgan Corp - Workflow Automation Setup Script

USAGE:
  .\setup.ps1 -Setup              # Setup Python environment
  .\setup.ps1 -RunExample -N 1    # Run example 1
  .\setup.ps1 -ShowHelp           # Show this help

EXAMPLES:
  1. HR Onboarding Workflow
  2. Document Management & Versioning
  3. E-Form Validation & Export

REQUIREMENTS:
  - Python 3.8+
  - pip package manager
"@
}

function Setup-Environment {
    Write-Host "Setting up Workflow Automation environment..." -ForegroundColor Green
    
    # Create Python virtual environment
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    New-Item -ItemType Directory -Path "documents" -Force | Out-Null
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    New-Item -ItemType Directory -Path "temp" -Force | Out-Null
    
    Write-Host "✓ Environment setup complete!" -ForegroundColor Green
}

function Run-Example {
    param([int]$Number)
    
    # Activate environment
    & ".\venv\Scripts\Activate.ps1"
    
    $examples = @{
        1 = "examples/example_1_hr_onboarding.py"
        2 = "examples/example_2_document_management.py"
        3 = "examples/example_3_eform_validation.py"
    }
    
    if ($examples.ContainsKey($Number)) {
        $script = $examples[$Number]
        Write-Host "Running Example $Number..." -ForegroundColor Green
        python $script
    } else {
        Write-Host "Invalid example number. Choose 1, 2, or 3." -ForegroundColor Red
    }
}

# Main execution
if ($ShowHelp) {
    Show-Help
} elseif ($Setup) {
    Setup-Environment
} elseif ($RunExample) {
    Run-Example -Number $ExampleNumber
} else {
    Show-Help
}
