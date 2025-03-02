#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов проекта Guitar Trainer.
"""
import unittest
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    # Обнаруживаем и запускаем все тесты
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    # Запускаем тесты
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Выходим с кодом ошибки, если тесты не прошли
    sys.exit(not result.wasSuccessful()) 