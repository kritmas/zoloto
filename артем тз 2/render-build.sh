#!/usr/bin/env bash
# Устанавливаем зависимости Python
pip install -r requirements.txt

# Устанавливаем Chrome и Chromedriver для Selenium
if [ ! -d "chrome" ]; then
  mkdir -p chrome
  cd chrome
  wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/linux64/chrome-linux64.zip
  unzip chrome-linux64.zip
  wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/linux64/chromedriver-linux64.zip
  unzip chromedriver-linux64.zip
  cd ..
fi
