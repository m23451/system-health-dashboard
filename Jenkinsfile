pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timeout(time: 1, unit: 'HOURS')
    }

    environment {
        IMAGE_NAME     = 'system-health-dashboard'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        PROMETHEUS_URL = 'http://prometheus:9090'
    }

    stages {
        stage('Checkout') {
    steps {
        script {
            def scmVars = checkout scm
            env.BRANCH_REF = scmVars.GIT_BRANCH ?: ''
            echo "Building branch: ${env.BRANCH_REF}"
        }
    }
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
            post { always { junit 'test-results.xml' } }
        }

        stage('Build and tag') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
                sh 'docker images ${IMAGE_NAME}'
            }
        }

        stage('Deploy to Staging') {
            steps {
                script {
                    env.DEPLOY_TARGET = 'staging'
                    env.PREV_STAGING = sh(
                        script: '''docker inspect --format '{{.Config.Image}}' app-staging 2>/dev/null | cut -d: -f2''',
                        returnStdout: true
                    ).trim()
                    echo "Previous staging tag: ${env.PREV_STAGING ?: 'none'}"
                }
                sh 'docker compose -p shd-staging -f docker-compose.staging.yml up -d'
                sh 'docker ps --filter name=app-staging'
            }
        }

        stage('Test (staging)') {
            steps { sh 'bash scripts/smoke_test.sh http://app-staging:5000' }
        }

        stage('Verify monitoring') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6 7 8; do
                      RESULT=$(curl -fsS -G "${PROMETHEUS_URL}/api/v1/query" \
                        --data-urlencode 'query=up{job="system-health",environment="staging"}' \
                        | python3 -c "import sys,json; r=json.load(sys.stdin)['data']['result']; print(r[0]['value'][1] if r else 'none')")
                      echo "Prometheus up{staging} = ${RESULT}"
                      if [ "${RESULT}" = "1" ]; then exit 0; fi
                      sleep 10
                    done
                    echo "Staging target is not UP in Prometheus"
                    exit 1
                '''
            }
        }

        stage('Approval gate') {
            when { expression { env.BRANCH_REF in ['origin/main', 'main'] } }
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    script {
                        def approver = input(
                            message: "Deploy build ${env.BUILD_NUMBER} to production?",
                            ok: 'Approve',
                            submitterParameter: 'approver'
                        )
                        echo "Approved by: ${approver}"
                    }
                }
            }
        }

        stage('Deploy to Production') {
            when { expression { env.BRANCH_REF in ['origin/main', 'main'] } }
            steps {
                script {
                    env.DEPLOY_TARGET = 'production'
                    env.PREV_PRODUCTION = sh(
                        script: '''docker inspect --format '{{.Config.Image}}' app-production 2>/dev/null | cut -d: -f2''',
                        returnStdout: true
                    ).trim()
                    echo "Previous production tag: ${env.PREV_PRODUCTION ?: 'none'}"
                }
                sh 'docker compose -p shd-production -f docker-compose.production.yml up -d'
                sh 'docker ps --filter name=app-production'
            }
        }

        stage('Smoke test (production)') {
            when { expression { env.BRANCH_REF in ['origin/main', 'main'] } }
            steps { sh 'bash scripts/smoke_test.sh http://app-production:5000' }
        }
    }

    post {
        failure {
            script {
                if (env.DEPLOY_TARGET == 'staging' && env.PREV_STAGING) {
                    sh "bash scripts/rollback.sh staging docker-compose.staging.yml ${env.PREV_STAGING}"
                } else if (env.DEPLOY_TARGET == 'production' && env.PREV_PRODUCTION) {
                    sh "bash scripts/rollback.sh production docker-compose.production.yml ${env.PREV_PRODUCTION}"
                } else {
                    echo 'Nothing to roll back (failed before a deploy, or no previous tag).'
                }
            }
        }
    }
}
