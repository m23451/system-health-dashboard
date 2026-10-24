pipeline {
    agent any

    environment {
        IMAGE_NAME = 'system-health-dashboard'
        CONTAINER  = "shd-check-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '. .venv/bin/activate && python -m pytest -v --junitxml=test-results.xml'
            }
            post {
                always { junit 'test-results.xml' }
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:latest .'
                sh 'docker images ${IMAGE_NAME}'
            }
        }

        stage('Tag') {
            steps {
                sh 'docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${BUILD_NUMBER}'
                sh 'docker images ${IMAGE_NAME}'
            }
        }

        stage('Health check') {
            steps {
                sh '''
                    docker run -d --name ${CONTAINER} -e APP_ENV=jenkins ${IMAGE_NAME}:${BUILD_NUMBER}
                    sleep 5
                    docker exec ${CONTAINER} python -c "import urllib.request as u; r=u.urlopen('http://localhost:5000/health'); print(r.status, r.read().decode())"
                '''
            }
            post {
                always { sh 'docker rm -f ${CONTAINER} || true' }
            }
        }
    }
}
