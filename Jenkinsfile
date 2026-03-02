pipeline {
  agent any

  environment {
    IMAGE_NAME = "thongvm/my-app"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    NAMESPACE  = "jenkins"
    GIT_REPO   = "https://github.com/Thongvm1111/app-repo"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Docker Build & Push with Kaniko') {
      steps {
        sh """
        kubectl run kaniko-${BUILD_NUMBER} \
          --image=gcr.io/kaniko-project/executor:latest \
          --restart=Never \
          --namespace=${NAMESPACE} \
          --overrides='{
            "spec": {
              "containers": [{
                "name": "kaniko",
                "image": "gcr.io/kaniko-project/executor:latest",
                "args": [
                  "--context=git://github.com/Thongvm1111/app-repo#refs/heads/main",
                  "--dockerfile=Dockerfile",
                  "--destination=${IMAGE_NAME}:${IMAGE_TAG}"
                ],
                "volumeMounts": [{
                  "name": "dockerhub-secret",
                  "mountPath": "/kaniko/.docker"
                }]
              }],
              "volumes": [{
                "name": "dockerhub-secret",
                "secret": {
                  "secretName": "dockerhub-secret",
                  "items": [{
                    "key": ".dockerconfigjson",
                    "path": "config.json"
                  }]
                }
              }],
              "restartPolicy": "Never"
            }
          }'

        echo "Waiting for Kaniko pod..."
        while true; do
          STATUS=\$(kubectl get pod kaniko-${BUILD_NUMBER} -n ${NAMESPACE} -o jsonpath='{.status.phase}')
          echo "Status: \$STATUS"
          [ "\$STATUS" = "Succeeded" ] && break
          [ "\$STATUS" = "Failed" ] && kubectl logs kaniko-${BUILD_NUMBER} -n ${NAMESPACE} && exit 1
          sleep 5
        done

        kubectl delete pod kaniko-${BUILD_NUMBER} -n ${NAMESPACE}
        """
      }
    }

    stage('Update GitOps Repo') {
      when {
        expression { currentBuild.currentResult == 'SUCCESS' }
      }
      steps {
        echo "TODO: update GitOps repo (ArgoCD)"
      }
    }
  }
}
