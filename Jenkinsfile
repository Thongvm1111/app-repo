pipeline {
  agent any

  environment {
    IMAGE = "thongvm/my-app"
    TAG = "${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Docker Build') {
      steps {
        sh "docker build -t ${IMAGE}:${TAG} ."
      }
    }

    stage('Docker Push') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'USER',
          passwordVariable: 'PASS'
        )]) {
          sh """
            echo $PASS | docker login -u $USER --password-stdin
            docker push ${IMAGE}:${TAG}
          """
        }
      }
    }

    stage('Update GitOps Repo') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'github-token',
          usernameVariable: 'GIT_USER',
          passwordVariable: 'GIT_PASS'
        )]) {
          sh """
            git clone https://${GIT_USER}:${GIT_PASS}@github.com/Thongvm1111/gitops-repo.git
            cd gitops-repo
            sed -i "s|image: ${IMAGE}:.*|image: ${IMAGE}:${TAG}|g" deployment.yaml
            git config user.email "jenkins@ci.com"
            git config user.name "Jenkins"
            git add .
            git commit -m "Update image to ${TAG}"
            git push
          """
        }
      }
    }

  }
}
