name: Telegram Quiz Bot

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Cache Python packages
      uses: actions/cache@v2
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y libreoffice
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run the script
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
        WP_SITE_URL: ${{ secrets.WP_SITE_URL }}
        WP_USER: ${{ secrets.WP_USER }}
      run: |
        python main.py
