# Retail Multi-Brand Data Project: Setup Script for Windows (PowerShell)

Write-Host "🚀 Starting local environment setup..." -ForegroundColor Cyan

# 1. Create virtual environment
if (-Not (Test-Path -Path ".venv")) {
    Write-Host "📦 Creating virtual environment..."
    python -m venv .venv
}

# 2. Activate virtual environment
Write-Host "🔌 Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# 3. Upgrade pip
Write-Host "🆙 Upgrading pip..."
python -m pip install --upgrade pip

# 4. Install requirements
Write-Host "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# 5. Initialize dbt dependencies
Write-Host "🛠️ Initializing dbt packages..."
cd dbt_project
dbt deps
cd ..

Write-Host "✅ Setup complete! You're ready to run the pipeline." -ForegroundColor Green
Write-Host "To start, run: .\.venv\Scripts\Activate.ps1"
