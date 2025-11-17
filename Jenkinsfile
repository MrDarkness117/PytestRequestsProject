pipeline {
    agent any
    
    options {
        // Ограничиваем количество хранимых сборок (последние 10 для простоты)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 5, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Получение кода из репозитория...'
                checkout scm
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Установка зависимостей Python...'
                script {
                    // Настройка Python
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Запуск тестов GigaChat API...'
                script {
                    // Активаця venv и запуск тестов
                    sh '''
                        . venv/bin/activate || source venv/bin/activate || true
                        pytest -v -m gigachat --alluredir=allure-results --tb=short
                    '''
                }
            }
            post {
                always {
                    echo 'Тесты завершены. Результаты сохранены в allure-results/'
                }
            }
        }
    }
    
    post {
        always {
            // Публикация Allure отчетов
            allure includeProperties: false,
                  jdk: '',
                  properties: [],
                  reportBuildPolicy: 'ALWAYS',
                  results: [[path: 'allure-results']]
        }
        success {
            echo 'Все тесты прошли успешно!'
        }
        failure {
            echo 'Тесты прерваны из-за ошибки. Подробности в отчете Allure.'
        }
        unstable {
            echo 'Есть упавшие тесты, смотреть отчет Allure.'
        }
    }
}

